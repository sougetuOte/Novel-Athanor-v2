"""Tests for Secret model."""

import pytest
from pydantic import ValidationError

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.models.secret import Secret, SecretImportance


class TestSecretImportance:
    """SecretImportance 列挙型のテスト."""

    def test_importance_values(self) -> None:
        """重要度の値を確認できる."""
        assert SecretImportance.CRITICAL == "critical"
        assert SecretImportance.HIGH == "high"
        assert SecretImportance.MEDIUM == "medium"
        assert SecretImportance.LOW == "low"


class TestSecret:
    """Secret モデルのテスト."""

    def test_create_secret(self) -> None:
        """秘密を作成できる."""
        secret = Secret(
            id="SEC-001",
            content="アイラは実は王族の血筋",
            visibility=AIVisibilityLevel.KNOW,
            forbidden_keywords=["王族", "血筋", "高貴"],
            allowed_expressions=[
                "彼女の瞳には見覚えのある光があった",
                "その立ち振る舞いには育ちの良さが滲み出ていた",
            ],
        )
        assert secret.id == "SEC-001"
        assert secret.content == "アイラは実は王族の血筋"
        assert secret.visibility == AIVisibilityLevel.KNOW
        assert "王族" in secret.forbidden_keywords
        assert len(secret.allowed_expressions) == 2

    def test_secret_with_importance(self) -> None:
        """重要度を指定して秘密を作成できる."""
        secret = Secret(
            id="SEC-002",
            content="犯人の正体",
            visibility=AIVisibilityLevel.HIDDEN,
            importance=SecretImportance.CRITICAL,
        )
        assert secret.importance == SecretImportance.CRITICAL

    def test_secret_defaults(self) -> None:
        """デフォルト値が設定される."""
        secret = Secret(
            id="SEC-003",
            content="秘密の内容",
        )
        assert secret.visibility == AIVisibilityLevel.HIDDEN
        assert secret.importance == SecretImportance.MEDIUM
        assert secret.forbidden_keywords == []
        assert secret.allowed_expressions == []
        assert secret.related_entity is None
        assert secret.notes is None

    def test_secret_with_related_entity(self) -> None:
        """関連エンティティを指定できる."""
        secret = Secret(
            id="SEC-004",
            content="メイドの動機",
            visibility=AIVisibilityLevel.KNOW,
            related_entity="character:メイド田中",
        )
        assert secret.related_entity == "character:メイド田中"

    def test_secret_with_notes(self) -> None:
        """備考を追加できる."""
        secret = Secret(
            id="SEC-005",
            content="封印された魔法",
            visibility=AIVisibilityLevel.AWARE,
            notes="第10話で暗示、第25話で回収予定",
        )
        assert secret.notes == "第10話で暗示、第25話で回収予定"

    def test_secret_visibility_int_coercion(self) -> None:
        """整数から可視性レベルに変換できる."""
        secret = Secret(
            id="SEC-006",
            content="テスト",
            visibility=2,
        )
        assert secret.visibility == AIVisibilityLevel.KNOW

    def test_secret_visibility_validation(self) -> None:
        """可視性レベルは 0-3 の範囲でなければならない."""
        with pytest.raises(ValidationError):
            Secret(
                id="SEC-007",
                content="テスト",
                visibility=4,
            )

    def test_secret_get_similarity_threshold(self) -> None:
        """重要度に応じた類似度閾値を取得できる."""
        critical = Secret(
            id="SEC-C",
            content="重要",
            importance=SecretImportance.CRITICAL,
        )
        high = Secret(
            id="SEC-H",
            content="高",
            importance=SecretImportance.HIGH,
        )
        medium = Secret(
            id="SEC-M",
            content="中",
            importance=SecretImportance.MEDIUM,
        )
        low = Secret(
            id="SEC-L",
            content="低",
            importance=SecretImportance.LOW,
        )

        assert critical.get_similarity_threshold() == pytest.approx(0.55)
        assert high.get_similarity_threshold() == pytest.approx(0.60)
        assert medium.get_similarity_threshold() == pytest.approx(0.70)
        assert low.get_similarity_threshold() == pytest.approx(0.75)
