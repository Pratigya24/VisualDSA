from beanie import PydanticObjectId

from app.models.topic import Topic
from app.services.topic_service import TopicService, UNLOCK_THRESHOLD


def _make_topic(prerequisite_ids: list[PydanticObjectId]) -> Topic:
    return Topic.model_construct(
        id=PydanticObjectId(),
        name="Test Topic",
        slug="test-topic",
        description="",
        order=1,
        prerequisite_ids=prerequisite_ids,
        icon=None,
    )


def _service() -> TopicService:
    # _is_unlocked touches no repository, so None stand-ins are sufficient
    # for testing this pure decision function in isolation.
    return TopicService(topic_repository=None, algorithm_repository=None, progress_repository=None)  # type: ignore[arg-type]


def test_topic_with_no_prerequisites_is_always_unlocked():
    service = _service()
    topic = _make_topic(prerequisite_ids=[])
    assert service._is_unlocked(topic, {}) is True


def test_topic_locked_when_prerequisite_below_threshold():
    service = _service()
    prereq_id = PydanticObjectId()
    topic = _make_topic(prerequisite_ids=[prereq_id])
    # 1 of 5 solved = 20%, below the 50% unlock threshold.
    stats = {prereq_id: (5, 1)}
    assert service._is_unlocked(topic, stats) is False


def test_topic_unlocked_when_prerequisite_meets_threshold():
    service = _service()
    prereq_id = PydanticObjectId()
    topic = _make_topic(prerequisite_ids=[prereq_id])
    # 2 of 4 solved = exactly 50%, meeting the unlock threshold.
    stats = {prereq_id: (4, 2)}
    assert service._is_unlocked(topic, stats) is True


def test_topic_unlocked_when_all_multiple_prerequisites_met():
    service = _service()
    prereq_a, prereq_b = PydanticObjectId(), PydanticObjectId()
    topic = _make_topic(prerequisite_ids=[prereq_a, prereq_b])
    stats = {prereq_a: (4, 2), prereq_b: (10, 5)}
    assert service._is_unlocked(topic, stats) is True


def test_topic_locked_if_any_prerequisite_unmet():
    service = _service()
    prereq_a, prereq_b = PydanticObjectId(), PydanticObjectId()
    topic = _make_topic(prerequisite_ids=[prereq_a, prereq_b])
    stats = {prereq_a: (4, 3), prereq_b: (10, 1)}
    assert service._is_unlocked(topic, stats) is False


def test_prerequisite_with_zero_algorithms_does_not_block_unlock():
    service = _service()
    prereq_id = PydanticObjectId()
    topic = _make_topic(prerequisite_ids=[prereq_id])
    stats = {prereq_id: (0, 0)}
    assert service._is_unlocked(topic, stats) is True
