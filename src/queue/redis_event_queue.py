from datetime import datetime, timezone

from redis.asyncio import Redis

from src.models.scheduled_event import ScheduledEvent

QUEUE_KEY = "event_queue"
UTC = timezone.utc


class RedisEventQueue:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def add_event(self, event: ScheduledEvent) -> None:
        score = event.scheduled_for.astimezone(UTC).timestamp()
        await self.redis.zadd(QUEUE_KEY, {str(event.id): score})

    async def remove_event(self, event_id: int) -> None:
        await self.redis.zrem(QUEUE_KEY, str(event_id))

    async def pop_due_event_ids(self, limit: int = 50) -> list[int]:
        now = datetime.now(tz=UTC).timestamp()
        results = await self.redis.zrangebyscore(
            QUEUE_KEY, min="-inf", max=now, start=0, num=limit
        )
        if not results:
            return []
        await self.redis.zrem(QUEUE_KEY, *results)
        return [int(event_id) for event_id in results]

    async def load_pending_events(self, events: list[ScheduledEvent]) -> None:
        if not events:
            return
        mapping = {
            str(event.id): event.scheduled_for.astimezone(UTC).timestamp()
            for event in events
        }
        await self.redis.zadd(QUEUE_KEY, mapping)
