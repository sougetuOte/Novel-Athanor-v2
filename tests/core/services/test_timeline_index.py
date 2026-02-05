"""Test TimelineIndex and TimelineEvent."""

from datetime import date

from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingPayoff,
    ForeshadowingStatus,
    ForeshadowingType,
    TimelineEntry,
    TimelineInfo,
)
from src.core.services.timeline_index import TimelineEvent, TimelineIndex


def make_foreshadowing(
    fs_id: str = "FS-03-test",
    title: str = "Test FS",
    status: ForeshadowingStatus = ForeshadowingStatus.PLANTED,
    events: list[TimelineEntry] | None = None,
    payoff_episode: str | None = None,
) -> Foreshadowing:
    """Create a test foreshadowing object.

    Args:
        fs_id: Foreshadowing ID
        title: Foreshadowing title
        status: Foreshadowing status
        events: Timeline events (optional)
        payoff_episode: Planned payoff episode (optional)

    Returns:
        Foreshadowing object for testing
    """
    timeline = None
    if events:
        timeline = TimelineInfo(registered_at=date(2024, 1, 1), events=events)
    payoff = None
    if payoff_episode:
        payoff = ForeshadowingPayoff(content="test", planned_episode=payoff_episode)
    return Foreshadowing(
        id=fs_id,
        title=title,
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=status,
        subtlety_level=5,
        timeline=timeline,
        payoff=payoff,
    )


class TestTimelineEvent:
    """Test TimelineEvent dataclass."""

    def test_create_timeline_event(self):
        """TimelineEvent can be created with all required fields."""
        event = TimelineEvent(
            foreshadowing_id="FS-03-rocket",
            foreshadowing_title="Rocket",
            episode="ep010",
            event_type=ForeshadowingStatus.PLANTED,
            expression="A mysterious device",
            subtlety=8,
            event_date=date(2024, 1, 15),
        )

        assert event.foreshadowing_id == "FS-03-rocket"
        assert event.foreshadowing_title == "Rocket"
        assert event.episode == "ep010"
        assert event.event_type == ForeshadowingStatus.PLANTED
        assert event.expression == "A mysterious device"
        assert event.subtlety == 8
        assert event.event_date == date(2024, 1, 15)


class TestTimelineIndexBuild:
    """Test TimelineIndex.build() method."""

    def test_build_empty_list(self):
        """Build from empty foreshadowing list returns empty index."""
        index = TimelineIndex.build([])

        assert index.total_events == 0
        assert index.episode_count == 0
        assert index.events_by_episode == {}
        assert index.last_mention == {}

    def test_build_foreshadowing_without_timeline(self):
        """Build from foreshadowing without timeline returns empty index."""
        fs = make_foreshadowing(events=None)
        index = TimelineIndex.build([fs])

        assert index.total_events == 0
        assert index.episode_count == 0

    def test_build_single_foreshadowing_single_event(self):
        """Build from single foreshadowing with one event."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="A mysterious device",
                subtlety=8,
            )
        ]
        fs = make_foreshadowing(fs_id="FS-03-rocket", title="Rocket", events=events)
        index = TimelineIndex.build([fs])

        assert index.total_events == 1
        assert index.episode_count == 1
        assert "ep010" in index.events_by_episode
        assert len(index.events_by_episode["ep010"]) == 1

        event = index.events_by_episode["ep010"][0]
        assert event.foreshadowing_id == "FS-03-rocket"
        assert event.foreshadowing_title == "Rocket"
        assert event.episode == "ep010"
        assert event.event_type == ForeshadowingStatus.PLANTED

        assert index.last_mention["FS-03-rocket"] == "ep010"

    def test_build_single_foreshadowing_multiple_events(self):
        """Build from single foreshadowing with multiple events."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="A mysterious device",
                subtlety=8,
            ),
            TimelineEntry(
                episode="ep012",
                type=ForeshadowingStatus.REINFORCED,
                date=date(2024, 1, 22),
                expression="The device glows",
                subtlety=6,
            ),
        ]
        fs = make_foreshadowing(fs_id="FS-03-rocket", title="Rocket", events=events)
        index = TimelineIndex.build([fs])

        assert index.total_events == 2
        assert index.episode_count == 2
        assert len(index.events_by_episode["ep010"]) == 1
        assert len(index.events_by_episode["ep012"]) == 1

        # last_mention should be the latest episode
        assert index.last_mention["FS-03-rocket"] == "ep012"

    def test_build_multiple_foreshadowings(self):
        """Build from multiple foreshadowings integrates all events."""
        events1 = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="A mysterious device",
                subtlety=8,
            )
        ]
        events2 = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="A strange symbol",
                subtlety=9,
            )
        ]
        fs1 = make_foreshadowing(fs_id="FS-03-rocket", title="Rocket", events=events1)
        fs2 = make_foreshadowing(fs_id="FS-05-symbol", title="Symbol", events=events2)

        index = TimelineIndex.build([fs1, fs2])

        assert index.total_events == 2
        assert index.episode_count == 1  # Both events in same episode
        assert len(index.events_by_episode["ep010"]) == 2
        assert index.last_mention["FS-03-rocket"] == "ep010"
        assert index.last_mention["FS-05-symbol"] == "ep010"


class TestTimelineIndexGetEventsForEpisode:
    """Test TimelineIndex.get_events_for_episode() method."""

    def test_get_events_existing_episode(self):
        """Get events for existing episode returns event list."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="Test",
                subtlety=5,
            )
        ]
        fs = make_foreshadowing(events=events)
        index = TimelineIndex.build([fs])

        result = index.get_events_for_episode("ep010")
        assert len(result) == 1
        assert result[0].episode == "ep010"

    def test_get_events_nonexistent_episode(self):
        """Get events for nonexistent episode returns empty list."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="Test",
                subtlety=5,
            )
        ]
        fs = make_foreshadowing(events=events)
        index = TimelineIndex.build([fs])

        result = index.get_events_for_episode("ep999")
        assert result == []

    def test_get_events_episode_normalization(self):
        """Get events normalizes episode IDs (ep010 and 010 match)."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="Test",
                subtlety=5,
            )
        ]
        fs = make_foreshadowing(events=events)
        index = TimelineIndex.build([fs])

        # Should find the same event with different format
        result1 = index.get_events_for_episode("ep010")
        result2 = index.get_events_for_episode("010")

        assert len(result1) == 1
        assert len(result2) == 1
        assert result1[0].foreshadowing_id == result2[0].foreshadowing_id


class TestTimelineIndexGetSilentForeshadowings:
    """Test TimelineIndex.get_silent_foreshadowings() method."""

    def test_silent_foreshadowings_above_threshold(self):
        """Foreshadowings silent for threshold+ episodes are detected."""
        events = [
            TimelineEntry(
                episode="ep005",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 10),
                expression="Test",
                subtlety=5,
            )
        ]
        fs = make_foreshadowing(fs_id="FS-03-rocket", events=events)
        index = TimelineIndex.build([fs])

        # Current episode is ep010, last mention was ep005, silence = 5
        result = index.get_silent_foreshadowings("ep010", threshold=5)

        assert len(result) == 1
        assert result[0][0] == "FS-03-rocket"
        assert result[0][1] == 5  # episodes_since_last_mention

    def test_silent_foreshadowings_below_threshold(self):
        """Foreshadowings below threshold are not included."""
        events = [
            TimelineEntry(
                episode="ep008",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 10),
                expression="Test",
                subtlety=5,
            )
        ]
        fs = make_foreshadowing(fs_id="FS-03-rocket", events=events)
        index = TimelineIndex.build([fs])

        # Current episode is ep010, last mention was ep008, silence = 2
        result = index.get_silent_foreshadowings("ep010", threshold=5)

        assert len(result) == 0

    def test_silent_foreshadowings_sorted_by_silence_desc(self):
        """Results are sorted by silence (descending)."""
        events1 = [
            TimelineEntry(
                episode="ep003",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 5),
                expression="Test1",
                subtlety=5,
            )
        ]
        events2 = [
            TimelineEntry(
                episode="ep007",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 10),
                expression="Test2",
                subtlety=5,
            )
        ]
        fs1 = make_foreshadowing(fs_id="FS-03-old", events=events1)
        fs2 = make_foreshadowing(fs_id="FS-07-recent", events=events2)
        index = TimelineIndex.build([fs1, fs2])

        result = index.get_silent_foreshadowings("ep010", threshold=3)

        assert len(result) == 2
        # FS-03-old (silence=7) should come first
        assert result[0][0] == "FS-03-old"
        assert result[0][1] == 7
        assert result[1][0] == "FS-07-recent"
        assert result[1][1] == 3


class TestTimelineIndexGetApproachingPayoffs:
    """Test TimelineIndex.get_approaching_payoffs() method."""

    def test_approaching_payoffs_within_threshold(self):
        """Payoffs within threshold episodes are detected."""
        fs = make_foreshadowing(
            fs_id="FS-03-rocket",
            payoff_episode="ep013",
        )
        index = TimelineIndex.build([fs])

        # Current episode is ep010, payoff at ep013, remaining = 3
        result = index.get_approaching_payoffs("ep010", [fs], threshold=3)

        assert len(result) == 1
        assert result[0][0] == "FS-03-rocket"
        assert result[0][1] == 3  # remaining_episodes

    def test_approaching_payoffs_beyond_threshold(self):
        """Payoffs beyond threshold are not included."""
        fs = make_foreshadowing(
            fs_id="FS-03-rocket",
            payoff_episode="ep020",
        )
        index = TimelineIndex.build([fs])

        # Current episode is ep010, payoff at ep020, remaining = 10
        result = index.get_approaching_payoffs("ep010", [fs], threshold=3)

        assert len(result) == 0

    def test_approaching_payoffs_sorted_by_remaining_asc(self):
        """Results are sorted by remaining (ascending)."""
        fs1 = make_foreshadowing(
            fs_id="FS-03-soon",
            payoff_episode="ep011",
        )
        fs2 = make_foreshadowing(
            fs_id="FS-05-later",
            payoff_episode="ep013",
        )
        index = TimelineIndex.build([fs1, fs2])

        result = index.get_approaching_payoffs("ep010", [fs1, fs2], threshold=3)

        assert len(result) == 2
        # FS-03-soon (remaining=1) should come first
        assert result[0][0] == "FS-03-soon"
        assert result[0][1] == 1
        assert result[1][0] == "FS-05-later"
        assert result[1][1] == 3

    def test_approaching_payoffs_without_payoff(self):
        """Foreshadowings without payoff are not included."""
        fs = make_foreshadowing(
            fs_id="FS-03-no-payoff",
            payoff_episode=None,
        )
        index = TimelineIndex.build([fs])

        result = index.get_approaching_payoffs("ep010", [fs], threshold=3)

        assert len(result) == 0


class TestTimelineIndexProperties:
    """Test TimelineIndex properties."""

    def test_total_events_property(self):
        """total_events returns correct count."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="Test1",
                subtlety=5,
            ),
            TimelineEntry(
                episode="ep012",
                type=ForeshadowingStatus.REINFORCED,
                date=date(2024, 1, 22),
                expression="Test2",
                subtlety=5,
            ),
        ]
        fs = make_foreshadowing(events=events)
        index = TimelineIndex.build([fs])

        assert index.total_events == 2

    def test_episode_count_property(self):
        """episode_count returns correct count."""
        events = [
            TimelineEntry(
                episode="ep010",
                type=ForeshadowingStatus.PLANTED,
                date=date(2024, 1, 15),
                expression="Test1",
                subtlety=5,
            ),
            TimelineEntry(
                episode="ep012",
                type=ForeshadowingStatus.REINFORCED,
                date=date(2024, 1, 22),
                expression="Test2",
                subtlety=5,
            ),
        ]
        fs = make_foreshadowing(events=events)
        index = TimelineIndex.build([fs])

        assert index.episode_count == 2


class TestHelperFunctions:
    """Test helper functions."""

    def test_episode_number_extraction(self):
        """_episode_number extracts episode numbers correctly."""
        from src.core.services.timeline_index import _episode_number

        assert _episode_number("ep010") == 10
        assert _episode_number("010") == 10
        assert _episode_number("10") == 10
        assert _episode_number("ep001") == 1
        assert _episode_number("100") == 100

    def test_episode_number_invalid(self):
        """_episode_number returns 0 for invalid input."""
        from src.core.services.timeline_index import _episode_number

        assert _episode_number("invalid") == 0
        assert _episode_number("") == 0

    def test_episodes_match(self):
        """_episodes_match compares episode IDs correctly."""
        from src.core.services.timeline_index import _episodes_match

        assert _episodes_match("ep010", "010")
        assert _episodes_match("ep010", "10")
        assert _episodes_match("010", "10")
        assert not _episodes_match("ep010", "ep011")
