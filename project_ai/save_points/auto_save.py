#!/usr/bin/env python3
"""
Auto-Save Service - Background 15-minute rotation
Runs as a background task to create rotating auto-saves
"""

import asyncio
import logging

from project_ai.save_points.save_manager import SavePointsManager

logger = logging.getLogger(__name__)


class AutoSaveService:
    """Background service for automatic save creation"""

    def __init__(self, interval_minutes: int = 15):
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.save_manager = SavePointsManager()
        self.task: asyncio.Task | None = None
        self.running = False

    async def start(self):
        """Start the auto-save service"""
        if self.running:
            logger.warning("Auto-save service already running")
            return

        self.running = True
        self.task = asyncio.create_task(self._auto_save_loop())
        logger.info("Auto-save service started (interval: %s minutes)", self.interval_minutes)

    async def stop(self):
        """Stop the auto-save service"""
        if not self.running:
            return

        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info("Auto-save service stopped")

    async def _auto_save_loop(self):
        """Main auto-save loop"""
        while self.running:
            try:
                await asyncio.sleep(self.interval_seconds)

                if self.running:
                    logger.info("Creating auto-save...")
                    self.save_manager.create_auto_save()
                    logger.info("Auto-save completed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-save loop: {e}", exc_info=True)
                # Continue running even if one save fails

    def get_stats(self) -> dict:
        """Get auto-save service statistics"""
        return {
            "running": self.running,
            "interval_minutes": self.interval_minutes,
            "next_save_in_seconds": self.interval_seconds if self.running else None,
            "save_points": self.save_manager.list_save_points(),
        }


# Global instance
_auto_save_service: AutoSaveService | None = None


def get_auto_save_service() -> AutoSaveService:
    """Get or create the global auto-save service instance"""
    global _auto_save_service
    if _auto_save_service is None:
        _auto_save_service = AutoSaveService()
    return _auto_save_service
