import asyncio
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from app.core.logger import get_logger

logger = get_logger("amras.production.queue")


class QueueItem(BaseModel):
    job_id: int
    project_id: int
    queue_name: str
    priority: int = 0
    status: str = "queued"
    retry_count: int = 0


class QueueManagerAgent:
    """
    Queue Manager Agent
    Responsibilities: Manage Render Queue, OCR Queue, Narration Queue, Download Queue, Publishing Queue.
    """

    def __init__(self) -> None:
        self.queues: Dict[str, List[QueueItem]] = {"render": [], "ocr": [], "narration": [], "download": [], "publishing": []}
        self.is_running: Dict[str, bool] = {}

    async def enqueue(self, item: QueueItem) -> Dict[str, Any]:
        """Adds an item to the specified queue."""
        if item.queue_name not in self.queues:
            self.queues[item.queue_name] = []
        self.queues[item.queue_name].append(item)
        # Re-sort queue by priority (higher number = higher priority)
        self.queues[item.queue_name].sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"Enqueued job {item.job_id} in {item.queue_name} queue.")
        return {"status": "enqueued", "job_id": item.job_id}

    async def dequeue_highest_priority(self, queue_name: str) -> Optional[QueueItem]:
        """Dequeues the highest priority item from the queue."""
        if queue_name in self.queues and self.queues[queue_name]:
            item = self.queues[queue_name].pop(0)
            item.status = "running"
            logger.info(f"Dequeued job {item.job_id} from {queue_name}.")
            return item
        return None

    async def requeue_failed(self, item: QueueItem, max_retries: int = 3) -> bool:
        """Requeues a failed item if it hasn't exceeded max retries."""
        if item.retry_count < max_retries:
            item.retry_count += 1
            item.status = "queued"
            await self.enqueue(item)
            logger.warning(f"Requeued job {item.job_id} for retry {item.retry_count}/{max_retries}.")
            return True
        logger.error(f"Job {item.job_id} failed after {max_retries} retries.")
        item.status = "failed"
        return False

    async def get_queue_status(self, queue_name: str) -> List[QueueItem]:
        """Gets the status of a specific queue."""
        return self.queues.get(queue_name, [])

    async def update_priority(self, job_id: int, queue_name: str, new_priority: int) -> bool:
        """Updates the priority of a job in the queue."""
        for item in self.queues.get(queue_name, []):
            if item.job_id == job_id:
                item.priority = new_priority
                self.queues[queue_name].sort(key=lambda x: x.priority, reverse=True)
                return True
        return False

    async def start_worker(self, queue_name: str) -> None:
        """Starts a background worker loop for a specific queue."""
        self.is_running[queue_name] = True
        logger.info(f"Started worker for {queue_name} queue.")
        while self.is_running.get(queue_name, False):
            item = await self.dequeue_highest_priority(queue_name)
            if item:
                # Simulate processing
                await asyncio.sleep(0.1)
                logger.info(f"Processed job {item.job_id} from {queue_name}.")
            else:
                await asyncio.sleep(1)

    async def stop_workers(self) -> None:
        """Gracefully shuts down all workers."""
        for queue_name in list(self.is_running.keys()):
            self.is_running[queue_name] = False
        logger.info("All workers stopped.")

    async def stop_worker(self, queue_name: str) -> None:
        """Gracefully shuts down a specific worker."""
        if queue_name in self.is_running:
            self.is_running[queue_name] = False
            logger.info(f"Worker for {queue_name} stopped.")
