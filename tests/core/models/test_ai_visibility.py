"""Tests for AI Visibility model (complete version)."""

import pytest
from pydantic import ValidationError

from src.core.models.ai_visibility import (
    AIVisibility,
    AIVisibilityLevel,
    AllowedExpression,
    EntityVisibilityConfig,
    SectionVisibility,
    VisibilityConfig,
)


class TestAIVisibilityLevel:
    """AIVisibilityLevel 列挙型のテスト."""

    def test_level_values(self) -> None:
        """各レベルの値を確認できる."""
        assert AIVisibilityLevel.HIDDEN == 0
        assert AIVisibilityLevel.AWARE == 1
        assert AIVisibilityLevel.KNOW == 2
        assert AIVisibilityLevel.USE == 3

    def test_level_names(self) -> None:
        """各レベルの名前を確認できる."""
        assert AIVisibilityLevel.HIDDEN.name == "HIDDEN"
        assert AIVisibilityLevel.AWARE.name == "AWARE"
        assert AIVisibilityLevel.KNOW.name == "KNOW"
        assert AIVisibilityLevel.USE.name == "USE"


class TestAllowedExpression:
    """AllowedExpression モデルのテスト."""

    def test_create_allowed_expression(self) -> None:
        """許可された表現を作成できる."""
        expr = AllowedExpression(
            expression="彼女の瞳には見覚えのある光があった",
            context="王族の血筋を暗示する場面",
        )
        assert expr.expression == "彼女の瞳には見覚えのある光があった"
        assert expr.context == "王族の血筋を暗示する場面"

    def test_allowed_expression_context_optional(self) -> None:
        """context は省略可能."""
        expr = AllowedExpression(expression="何気ない表現")
        assert expr.expression == "何気ない表現"
        assert expr.context is None


class TestAIVisibility:
    """AIVisibility モデルのテスト."""

    def test_create_ai_visibility(self) -> None:
        """AI可視性設定を作成できる."""
        visibility = AIVisibility(
            level=AIVisibilityLevel.KNOW,
            forbidden_keywords=["王族", "血筋", "高貴"],
            allowed_expressions=[
                AllowedExpression(expression="彼女の瞳には見覚えのある光があった")
            ],
        )
        assert visibility.level == AIVisibilityLevel.KNOW
        assert visibility.forbidden_keywords == ["王族", "血筋", "高貴"]
        assert len(visibility.allowed_expressions) == 1

    def test_ai_visibility_defaults(self) -> None:
        """デフォルト値はすべて最も安全な設定."""
        visibility = AIVisibility()
        assert visibility.level == AIVisibilityLevel.HIDDEN
        assert visibility.forbidden_keywords == []
        assert visibility.allowed_expressions == []

    def test_ai_visibility_with_string_expressions(self) -> None:
        """文字列リストでも許可表現を設定できる."""
        visibility = AIVisibility(
            level=AIVisibilityLevel.KNOW,
            allowed_expressions=["表現1", "表現2"],
        )
        assert len(visibility.allowed_expressions) == 2
        assert visibility.allowed_expressions[0].expression == "表現1"

    def test_ai_visibility_level_int_coercion(self) -> None:
        """整数からレベルに変換できる."""
        visibility = AIVisibility(level=2)
        assert visibility.level == AIVisibilityLevel.KNOW

    def test_ai_visibility_level_validation(self) -> None:
        """レベルは 0-3 の範囲でなければならない."""
        with pytest.raises(ValidationError):
            AIVisibility(level=4)
        with pytest.raises(ValidationError):
            AIVisibility(level=-1)


class TestSectionVisibility:
    """SectionVisibility モデルのテスト."""

    def test_create_section_visibility(self) -> None:
        """セクション可視性を作成できる."""
        section = SectionVisibility(
            section_name="隠し設定",
            level=AIVisibilityLevel.HIDDEN,
        )
        assert section.section_name == "隠し設定"
        assert section.level == AIVisibilityLevel.HIDDEN

    def test_section_visibility_with_full_config(self) -> None:
        """完全な設定でセクション可視性を作成できる."""
        section = SectionVisibility(
            section_name="背景設定",
            level=AIVisibilityLevel.KNOW,
            forbidden_keywords=["秘密の言葉"],
            allowed_expressions=["暗示表現"],
        )
        assert section.forbidden_keywords == ["秘密の言葉"]


class TestEntityVisibilityConfig:
    """EntityVisibilityConfig モデルのテスト."""

    def test_create_entity_config(self) -> None:
        """エンティティ可視性設定を作成できる."""
        config = EntityVisibilityConfig(
            entity_type="character",
            entity_name="アイラ",
            default_level=AIVisibilityLevel.USE,
            sections=[
                SectionVisibility(
                    section_name="基本情報",
                    level=AIVisibilityLevel.USE,
                ),
                SectionVisibility(
                    section_name="隠し設定",
                    level=AIVisibilityLevel.HIDDEN,
                ),
            ],
        )
        assert config.entity_type == "character"
        assert config.entity_name == "アイラ"
        assert config.default_level == AIVisibilityLevel.USE
        assert len(config.sections) == 2

    def test_entity_config_defaults(self) -> None:
        """デフォルト値が設定される."""
        config = EntityVisibilityConfig(
            entity_type="world_setting",
            entity_name="魔法体系",
        )
        assert config.default_level == AIVisibilityLevel.HIDDEN
        assert config.sections == []


class TestVisibilityConfig:
    """VisibilityConfig モデルのテスト."""

    def test_create_visibility_config(self) -> None:
        """可視性設定を作成できる."""
        config = VisibilityConfig(
            version="1.0",
            default_visibility=AIVisibilityLevel.USE,
            entities=[
                EntityVisibilityConfig(
                    entity_type="character",
                    entity_name="主人公",
                ),
            ],
        )
        assert config.version == "1.0"
        assert config.default_visibility == AIVisibilityLevel.USE
        assert len(config.entities) == 1

    def test_visibility_config_defaults(self) -> None:
        """デフォルト値が設定される."""
        config = VisibilityConfig()
        assert config.version == "1.0"
        assert config.default_visibility == AIVisibilityLevel.HIDDEN
        assert config.entities == []

    def test_visibility_config_get_entity(self) -> None:
        """エンティティ設定を取得できる."""
        config = VisibilityConfig(
            entities=[
                EntityVisibilityConfig(
                    entity_type="character",
                    entity_name="主人公",
                    default_level=AIVisibilityLevel.USE,
                ),
                EntityVisibilityConfig(
                    entity_type="character",
                    entity_name="敵",
                    default_level=AIVisibilityLevel.HIDDEN,
                ),
            ],
        )
        entity = config.get_entity("character", "主人公")
        assert entity is not None
        assert entity.default_level == AIVisibilityLevel.USE

        not_found = config.get_entity("character", "存在しない")
        assert not_found is None
