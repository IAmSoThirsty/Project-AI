"""
Replay Engine
=============

Forensic replay engine using Temporal workflows.
Enables deterministic replay of build executions for debugging and auditing.
"""

import logging
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from temporalio.client import Client

from .capsule_engine import BuildCapsule, CapsuleEngine

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""
    return _utc_now().isoformat()


class ReplayResult:
    """Result of a build replay operation."""

    def __init__(
        self,
        success: bool,
        capsule_id: str,
        differences: dict[str, Any] | None = None,
        error: str | None = None,
        output_hash: str | None = None,
    ):
        """
        Initialize replay result.

        Args:
            success: Whether replay matched original
            capsule_id: Capsule that was replayed
            differences: Differences from original (if any)
            error: Error message if replay failed
        """
        self.success = success
        self.capsule_id = capsule_id
        self.differences = differences
        self.error = error
        self.timestamp = _utc_now_iso()
        self.output_hash = output_hash


class ReplayEngine:
    """
    Forensic replay engine for deterministic build reproduction.
    Uses Temporal workflows for time-travel debugging.
    """

    def __init__(
        self,
        capsule_engine: CapsuleEngine,
        temporal_client: Client | None = None,
        task_queue: str = "build-replay",
    ):
        """
        Initialize replay engine.

        Args:
            capsule_engine: Capsule engine for build capsules
            temporal_client: Optional Temporal client
            task_queue: Temporal task queue name
        """
        self.capsule_engine = capsule_engine
        self.temporal_client = temporal_client
        self.task_queue = task_queue
        self.replay_history: list[dict[str, Any]] = []
        logger.info("Replay engine initialized with queue: %s", task_queue)

    def replay_build(
        self, capsule_id: str, verify_outputs: bool = True
    ) -> ReplayResult:
        """
        Replay a build from capsule.

        Args:
            capsule_id: Capsule to replay
            verify_outputs: If True, verify output hashes match

        Returns:
            Replay result with differences
        """
        try:
            capsule = self.capsule_engine.capsules.get(capsule_id)
            if not capsule:
                raise ValueError(f"Capsule not found: {capsule_id}")

            # Verify capsule integrity first
            is_valid, error = self.capsule_engine.verify_capsule(
                capsule_id, detailed=True
            )
            if not is_valid:
                return ReplayResult(
                    success=False,
                    capsule_id=capsule_id,
                    error=f"Capsule integrity check failed: {error}",
                    output_hash=capsule.merkle_root,
                )

            # Execute replay workflow if Temporal available
            if self.temporal_client:
                result = self._replay_with_temporal(capsule, verify_outputs)
            else:
                result = self._replay_local(capsule, verify_outputs)

            if not result.output_hash:
                result.output_hash = self._compute_output_hash(capsule, result)

            # Record replay
            self._record_replay(capsule_id, result)

            return result

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error replaying build: %s", e, exc_info=True)
            return ReplayResult(success=False, capsule_id=capsule_id, error=str(e))

    async def replay_build_async(
        self, capsule_id: str, verify_outputs: bool = True
    ) -> ReplayResult:
        """Async wrapper for environments requiring coroutine-based call flow."""
        return await asyncio.to_thread(
            self.replay_build,
            capsule_id,
            verify_outputs,
        )

    def _replay_with_temporal(
        self, capsule: BuildCapsule, verify_outputs: bool
    ) -> ReplayResult:
        """Replay using Temporal workflow."""
        try:
            workflow_id = f"replay-{capsule.capsule_id}-{_utc_now().timestamp()}"

            async def _run_temporal() -> dict[str, Any]:
                handle = await self.temporal_client.start_workflow(
                    "BuildReplayWorkflow",
                    args=[capsule.to_dict(), verify_outputs],
                    id=workflow_id,
                    task_queue=self.task_queue,
                )
                return await handle.result()

            result_dict = asyncio.run(_run_temporal())

            return ReplayResult(
                success=result_dict.get("success", False),
                capsule_id=capsule.capsule_id,
                differences=result_dict.get("differences"),
                error=result_dict.get("error"),
                output_hash=result_dict.get("output_hash", capsule.merkle_root),
            )

        except Exception as e:
            logger.error("Error in Temporal replay: %s", e, exc_info=True)
            return ReplayResult(
                success=False,
                capsule_id=capsule.capsule_id,
                error=f"Temporal replay error: {str(e)}",
            )

    def _replay_local(
        self, capsule: BuildCapsule, verify_outputs: bool
    ) -> ReplayResult:
        """Fallback local replay without Temporal."""
        try:
            differences = {}

            # Verify inputs still exist
            missing_inputs = []
            for input_path in capsule.inputs:
                if not Path(input_path).exists():
                    missing_inputs.append(input_path)

            if missing_inputs:
                differences["missing_inputs"] = missing_inputs

            # Verify input hashes if files exist
            modified_inputs = []
            for input_path, original_hash in capsule.inputs.items():
                path = Path(input_path)
                if path.exists():
                    current_hash = self.capsule_engine._hash_file(path)
                    if current_hash != original_hash:
                        modified_inputs.append(
                            {
                                "path": input_path,
                                "original_hash": original_hash,
                                "current_hash": current_hash,
                            }
                        )

            if modified_inputs:
                differences["modified_inputs"] = modified_inputs

            # Verify outputs if requested
            if verify_outputs:
                missing_outputs = []
                modified_outputs = []

                for output_path, original_hash in capsule.outputs.items():
                    path = Path(output_path)
                    if not path.exists():
                        missing_outputs.append(output_path)
                    else:
                        current_hash = self.capsule_engine._hash_file(path)
                        if current_hash != original_hash:
                            modified_outputs.append(
                                {
                                    "path": output_path,
                                    "original_hash": original_hash,
                                    "current_hash": current_hash,
                                }
                            )

                if missing_outputs:
                    differences["missing_outputs"] = missing_outputs
                if modified_outputs:
                    differences["modified_outputs"] = modified_outputs

            success = not differences

            return ReplayResult(
                success=success,
                capsule_id=capsule.capsule_id,
                differences=differences if differences else None,
                output_hash=self._compute_output_hash(
                    capsule,
                    ReplayResult(
                        success=success,
                        capsule_id=capsule.capsule_id,
                        differences=differences if differences else None,
                    ),
                ),
            )

        except Exception as e:
            logger.error("Error in local replay: %s", e, exc_info=True)
            return ReplayResult(
                success=False,
                capsule_id=capsule.capsule_id,
                error=f"Local replay error: {str(e)}",
            )

    def replay_capsule_chain(
        self, capsule_ids: list[str], stop_on_failure: bool = True
    ) -> list[ReplayResult]:
        """
        Replay a chain of capsules in sequence.

        Args:
            capsule_ids: List of capsule IDs to replay
            stop_on_failure: If True, stop on first failure

        Returns:
            List of replay results
        """
        results = []

        for capsule_id in capsule_ids:
            result = self.replay_build(capsule_id, verify_outputs=True)
            results.append(result)

            if stop_on_failure and not result.success:
                logger.warning(
                    "Stopping chain replay at failed capsule: %s", capsule_id
                )
                break

        return results

    def find_divergence_point(self, capsule_ids: list[str]) -> str | None:
        """
        Find where a capsule chain diverges from expected.

        Args:
            capsule_ids: Ordered list of capsule IDs

        Returns:
            First capsule ID that diverges, or None if all match
        """
        results = self.replay_capsule_chain(capsule_ids, stop_on_failure=False)

        for result in results:
            if not result.success:
                logger.info("Divergence found at capsule: %s", result.capsule_id)
                return result.capsule_id

        return None

    def get_replay_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent replay history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of replay records
        """
        return self.replay_history[-limit:]

    def generate_replay_report(self, replay_result: ReplayResult) -> dict[str, Any]:
        """
        Generate detailed replay report.

        Args:
            replay_result: Replay result to analyze

        Returns:
            Detailed report dictionary
        """
        try:
            capsule = self.capsule_engine.capsules.get(replay_result.capsule_id)

            report = {
                "capsule_id": replay_result.capsule_id,
                "replay_timestamp": replay_result.timestamp,
                "success": replay_result.success,
                "error": replay_result.error,
            }

            if capsule:
                report["capsule_info"] = {
                    "tasks": capsule.tasks,
                    "input_count": len(capsule.inputs),
                    "output_count": len(capsule.outputs),
                    "original_timestamp": capsule.timestamp,
                    "merkle_root": capsule.merkle_root,
                }

            if replay_result.differences:
                report["differences"] = replay_result.differences
                report["difference_count"] = sum(
                    len(v) if isinstance(v, list) else 1
                    for v in replay_result.differences.values()
                )

            return report

        except Exception as e:
            logger.error("Error generating replay report: %s", e, exc_info=True)
            return {"error": str(e)}

    def _record_replay(self, capsule_id: str, result: ReplayResult) -> None:
        """Record replay execution."""
        self.replay_history.append(
            {
                "capsule_id": capsule_id,
                "timestamp": _utc_now_iso(),
                "success": result.success,
                "has_differences": result.differences is not None,
                "error": result.error,
                "output_hash": result.output_hash,
            }
        )

        # Keep last 1000 replays
        if len(self.replay_history) > 1000:
            self.replay_history = self.replay_history[-1000:]

    def forensic_analysis(self, capsule_id: str) -> dict[str, Any]:
        """Compatibility forensic analysis helper for replay diagnostics."""
        capsule = self.capsule_engine.get_capsule(capsule_id)
        if capsule is None:
            raise ValueError(f"Capsule not found: {capsule_id}")

        return {
            "capsule_id": capsule_id,
            "input_analysis": {
                "count": len(capsule.inputs),
                "paths": list(capsule.inputs.keys()),
            },
            "output_analysis": {
                "count": len(capsule.outputs),
                "paths": list(capsule.outputs.keys()),
            },
            "merkle_root": capsule.merkle_root,
        }

    def compare_capsules(self, capsule_id1: str, capsule_id2: str) -> dict[str, Any]:
        """Compatibility comparison helper."""
        diff = self.capsule_engine.compute_capsule_diff(capsule_id1, capsule_id2)
        if "error" in diff:
            return {"differences": [diff["error"]], "similarities": []}

        similarities: list[str] = []
        differences: list[str] = []

        common_tasks = diff.get("tasks", {}).get("common", [])
        if common_tasks:
            similarities.append("common_tasks")

        for section in ("tasks", "inputs", "outputs"):
            section_data = diff.get(section, {})
            for key in ("added", "removed", "modified"):
                if section_data.get(key):
                    differences.append(f"{section}.{key}")

        return {
            "capsule_1": capsule_id1,
            "capsule_2": capsule_id2,
            "differences": differences,
            "similarities": similarities,
            "raw_diff": diff,
        }

    def _compute_output_hash(self, capsule: BuildCapsule, result: ReplayResult) -> str:
        """Compute deterministic replay output hash."""
        payload = {
            "capsule_id": capsule.capsule_id,
            "merkle_root": capsule.merkle_root,
            "success": result.success,
            "differences": result.differences,
            "error": result.error,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()


__all__ = ["ReplayEngine", "ReplayResult"]
