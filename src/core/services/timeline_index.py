"""Timeline index for cross-episode foreshadowing queries.

横断参照インデックス: 各 Foreshadowing モデル内の timeline フィールドから
エピソード横断のクエリ機能を提供する導出ビュー。
"""

import re
from dataclasses import dataclass, field
from datetime import date

from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingStatus,
)


def _episode_number(episode_id: str) -> int:
    """エピソードIDからエピソード番号を抽出.

    Args:
        episode_id: エピソードID ("ep010", "010", "10" など)

    Returns:
        エピソード番号 (数値が抽出できない場合は 0)

    Examples:
        >>> _episode_number("ep010")
        10
        >>> _episode_number("010")
        10
        >>> _episode_number("10")
        10
        >>> _episode_number("invalid")
        0
    """
    cleaned = re.sub(r"[^0-9]", "", episode_id)
    return int(cleaned) if cleaned else 0


def _episodes_match(ep1: str, ep2: str) -> bool:
    """2つのエピソードIDが同じかどうか.

    Args:
        ep1: エピソードID1
        ep2: エピソードID2

    Returns:
        同じエピソード番号を指している場合 True

    Examples:
        >>> _episodes_match("ep010", "010")
        True
        >>> _episodes_match("ep010", "ep011")
        False
    """
    return _episode_number(ep1) == _episode_number(ep2)


@dataclass
class TimelineEvent:
    """タイムラインイベント（横断参照用）.

    各 Foreshadowing の TimelineEntry から変換された
    横断参照用のイベントデータ。

    Attributes:
        foreshadowing_id: 伏線ID
        foreshadowing_title: 伏線タイトル
        episode: エピソードID
        event_type: イベントタイプ（ForeshadowingStatus）
        expression: 使用された表現
        subtlety: 微細度 (1-10)
        event_date: イベント発生日
    """

    foreshadowing_id: str
    foreshadowing_title: str
    episode: str
    event_type: ForeshadowingStatus
    expression: str
    subtlety: int
    event_date: date


@dataclass
class TimelineIndex:
    """伏線タイムラインの横断参照インデックス（導出ビュー）.

    各 Foreshadowing モデル内の timeline フィールドを集約し、
    エピソード横断のクエリ機能を提供する。

    マスターデータは各 Foreshadowing 内の timeline フィールド。
    本インデックスは導出ビューであり、必要時に build() で再構築する。

    Attributes:
        events_by_episode: エピソードごとのイベントリスト
        last_mention: 各伏線の最終言及エピソード
        _all_events: 全イベントリスト（内部用）
    """

    events_by_episode: dict[str, list[TimelineEvent]] = field(default_factory=dict)
    last_mention: dict[str, str] = field(default_factory=dict)
    _all_events: list[TimelineEvent] = field(default_factory=list)

    @classmethod
    def build(cls, foreshadowings: list[Foreshadowing]) -> "TimelineIndex":
        """全伏線からインデックスを構築.

        Args:
            foreshadowings: 全伏線のリスト

        Returns:
            構築された TimelineIndex
        """
        index = cls()
        for fs in foreshadowings:
            if fs.timeline and fs.timeline.events:
                for entry in fs.timeline.events:
                    event = TimelineEvent(
                        foreshadowing_id=fs.id,
                        foreshadowing_title=fs.title,
                        episode=entry.episode,
                        event_type=entry.type,
                        expression=entry.expression,
                        subtlety=entry.subtlety,
                        event_date=entry.date,
                    )
                    index._all_events.append(event)

                    # events_by_episode
                    ep = entry.episode
                    if ep not in index.events_by_episode:
                        index.events_by_episode[ep] = []
                    index.events_by_episode[ep].append(event)

                    # last_mention (最新のイベントで更新)
                    # エピソード番号で比較して最大のものを保持
                    current_last = index.last_mention.get(fs.id)
                    if current_last is None or _episode_number(ep) > _episode_number(
                        current_last
                    ):
                        index.last_mention[fs.id] = ep

        return index

    def get_events_for_episode(self, episode_id: str) -> list[TimelineEvent]:
        """指定エピソードの全イベントを取得.

        Args:
            episode_id: エピソードID

        Returns:
            そのエピソードのイベントリスト
        """
        # 正規化して検索
        for ep_key, events in self.events_by_episode.items():
            if _episodes_match(ep_key, episode_id):
                return events
        return []

    def get_silent_foreshadowings(
        self,
        current_episode: str,
        threshold: int = 5,
        active_statuses: set[ForeshadowingStatus] | None = None,
    ) -> list[tuple[str, int]]:
        """threshold エピソード以上言及されていない伏線を返す.

        Args:
            current_episode: 現在のエピソード
            threshold: 沈黙の閾値（エピソード数）
            active_statuses: チェック対象のステータス（デフォルト: PLANTED, REINFORCED）

        Returns:
            (foreshadowing_id, episodes_since_last_mention) のタプルリスト
            沈黙が長い順にソート
        """
        if active_statuses is None:
            active_statuses = {
                ForeshadowingStatus.PLANTED,
                ForeshadowingStatus.REINFORCED,
            }

        current_num = _episode_number(current_episode)
        results = []

        # last_mention から silence を計算
        for fs_id, last_ep in self.last_mention.items():
            last_num = _episode_number(last_ep)
            silence = current_num - last_num
            if silence >= threshold:
                results.append((fs_id, silence))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def get_approaching_payoffs(
        self,
        current_episode: str,
        foreshadowings: list[Foreshadowing],
        threshold: int = 3,
    ) -> list[tuple[str, int]]:
        """回収予定が threshold エピソード以内の伏線を返す.

        Args:
            current_episode: 現在のエピソード
            foreshadowings: 全伏線リスト（payoff情報取得用）
            threshold: 接近閾値（エピソード数）

        Returns:
            (foreshadowing_id, remaining_episodes) のタプルリスト
            残りエピソードが少ない順にソート
        """
        current_num = _episode_number(current_episode)
        results = []

        for fs in foreshadowings:
            if fs.payoff and fs.payoff.planned_episode:
                payoff_num = _episode_number(fs.payoff.planned_episode)
                remaining = payoff_num - current_num
                if 0 < remaining <= threshold:
                    results.append((fs.id, remaining))

        return sorted(results, key=lambda x: x[1])

    @property
    def total_events(self) -> int:
        """全イベント数."""
        return len(self._all_events)

    @property
    def episode_count(self) -> int:
        """イベントが存在するエピソード数."""
        return len(self.events_by_episode)
