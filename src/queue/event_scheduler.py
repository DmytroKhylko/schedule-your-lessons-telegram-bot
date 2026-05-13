import asyncio
import logging

from src.queue.event_processor import EventProcessor

logger = logging.getLogger(__name__)


class EventScheduler:
    def __init__(
        self,
        processor: EventProcessor,
        poll_interval_seconds: float = 10.0,
    ) -> None:
        self.processor = processor
        self.poll_interval_seconds = poll_interval_seconds
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="event_scheduler")
        logger.info("Event scheduler started")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Event scheduler stopped")

    async def _run(self) -> None:
        while True:
            try:
                await self.processor.process_due_events()
            except Exception:
                logger.exception("Unexpected error in event scheduler")
            await asyncio.sleep(self.poll_interval_seconds)
