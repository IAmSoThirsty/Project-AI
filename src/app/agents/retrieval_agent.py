"""Retrieval / Vector QA Agent

Builds embeddings (placeholder) and provides retrieve function for QA.

All indexing and retrieval operations route through CognitionKernel.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class RetrievalAgent(KernelRoutedAgent):
    """Handles document indexing and retrieval for QA.

    All operations route through CognitionKernel for governance.
    """

    def __init__(
        self, data_dir: str = "data", kernel: CognitionKernel | None = None
    ) -> None:
        """Initialize the retrieval agent.

        Args:
            data_dir: Data directory for storing index
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Retrieval is typically low risk
        )

        self.data_dir = data_dir
        self.index_path = os.path.join(data_dir, "vectors", "index.json")
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        if not os.path.exists(self.index_path):
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def index_documents(self, docs: list[dict[str, Any]]) -> dict[str, Any]:
        """Index documents for retrieval.

        Routes through kernel for tracking and governance.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self._do_index_documents,
            action_name="RetrievalAgent.index_documents",
            action_args=(docs,),
            requires_approval=False,
            risk_level="low",
            metadata={"doc_count": len(docs), "operation": "index"},
        )

    def _do_index_documents(self, docs: list[dict[str, Any]]) -> dict[str, Any]:
        """Internal implementation of document indexing."""
        try:
            with open(self.index_path, encoding="utf-8") as f:
                current = json.load(f)
            current.extend(docs)
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)
            return {"success": True, "indexed": len(docs)}
        except Exception as e:
            logger.exception("Indexing failed: %s", e)
            return {"success": False, "error": str(e)}

    def retrieve(self, query: str, top_k: int = 3) -> dict[str, Any]:
        """Retrieve documents matching query.

        Routes through kernel for tracking and governance.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self._do_retrieve,
            action_name="RetrievalAgent.retrieve",
            action_args=(query, top_k),
            requires_approval=False,
            risk_level="low",
            metadata={"query": query, "top_k": top_k, "operation": "retrieve"},
        )

    def _do_retrieve(self, query: str, top_k: int = 3) -> dict[str, Any]:
        """Internal implementation of document retrieval."""
        try:
            with open(self.index_path, encoding="utf-8") as f:
                current = json.load(f)
            # naive retrieval using substring match
            hits = [d for d in current if query.lower() in json.dumps(d).lower()]
            return {"success": True, "results": hits[:top_k]}
        except Exception as e:
            logger.exception("Retrieval failed: %s", e)
            return {"success": False, "error": str(e)}
