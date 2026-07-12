from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.models.analytics_event import AnalyticsEvent, AnalyticsEventType


class AnalyticsRepository:
    async def record(
        self, user_id: PydanticObjectId, event_type: AnalyticsEventType, metadata: dict | None = None
    ) -> None:
        await AnalyticsEvent(user_id=user_id, event_type=event_type, metadata=metadata or {}).insert()

    async def daily_activity_counts(
        self, user_id: PydanticObjectId, since: datetime
    ) -> dict[str, int]:
        """
        Returns {"YYYY-MM-DD": event_count} for this user since `since`,
        used to render the dashboard's weekly activity heatmap.
        """
        pipeline = [
            {"$match": {"user_id": user_id, "created_at": {"$gte": since}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1},
                }
            },
        ]
        results = await AnalyticsEvent.aggregate(pipeline).to_list()
        return {row["_id"]: row["count"] for row in results}

    async def distinct_active_days(self, user_id: PydanticObjectId) -> list[datetime]:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "day": {"$min": "$created_at"},
                }
            },
            {"$sort": {"_id": -1}},
        ]
        results = await AnalyticsEvent.aggregate(pipeline).to_list()
        return [row["day"].replace(tzinfo=timezone.utc) for row in results]
