import asyncio
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger("monitoring_scheduler")

class MonitoringBackgroundScheduler:
    """
    Lightweight, native async background scheduler for YojnaSarthi scheme monitoring.
    Runs periodically without blocking FastAPI or requiring external task brokers.
    """

    def __init__(self, interval_seconds: int = 86400):  # Default: daily check
        self.interval_seconds = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._is_running = False
        self._last_run: Optional[str] = None

    def start(self):
        """Starts the background monitoring loop."""
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Monitoring Background Scheduler started (Interval: {self.interval_seconds}s).")

    def stop(self):
        """Stops the scheduler gracefully."""
        self._is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("Monitoring Background Scheduler stopped.")

    async def _run_loop(self):
        # Initial polite delay on startup so the app is fully ready
        await asyncio.sleep(5)
        
        while self._is_running:
            try:
                from .monitor_service import monitor_service
                logger.info("Scheduler triggering periodic scheme monitoring cycle...")
                report = await monitor_service.run_monitoring_cycle()
                self._last_run = report.get("cycle_completed_at")
                logger.info(f"Monitoring cycle finished: {report.get('success_count')} succeeded, {report.get('changes_detected')} changes.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background monitoring run: {e}")

            # Sleep until next interval
            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

    def get_status(self):
        return {
            "is_running": self._is_running,
            "interval_seconds": self.interval_seconds,
            "last_run": self._last_run,
            "next_run": "Scheduled in periodic cycle" if self._is_running else "Stopped"
        }

monitoring_scheduler = MonitoringBackgroundScheduler()

