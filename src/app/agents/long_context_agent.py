"""Long-context AI agent supporting extended conversations up to 200k tokens.

This agent provides access to long-context language models like Nous-Capybara-34B-200k
for handling very long sessions, large policy documents, or extensive knowledge base contexts.

Features:
- 200k+ token context window management
- Streaming response support
- Context compression and summarization
- Integration with Triumvirate governance
"""

from __future__ import annotations

import logging
import os
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class LongContextAgent(KernelRoutedAgent):
    """Agent for handling long-context conversations and document processing.

    Supports models with extended context windows (100k-200k+ tokens) for:
    - Extended conversation history
    - Large document analysis
    - Policy/knowledge base consultation
    - Multi-document reasoning

    All operations are routed through CognitionKernel for governance.
    """

    def __init__(
        self,
        model_name: str = "nous-capybara-34b",
        max_context_tokens: int = 200000,
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize the long-context agent.

        Args:
            model_name: Name of the long-context model to use
            max_context_tokens: Maximum context window size in tokens
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )

        self.model_name = model_name
        self.max_context_tokens = max_context_tokens
        self.api_endpoint = os.getenv("LONG_CONTEXT_API_ENDPOINT", "")
        self.api_key = os.getenv("LONG_CONTEXT_API_KEY", "")

        # Context management
        self.current_context_size = 0
        self.context_history: list[dict[str, Any]] = []

        logger.info(
            "LongContextAgent initialized: model=%s, max_tokens=%d",
            model_name,
            max_context_tokens,
        )

    def process_long_conversation(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Process a long conversation with extended context.

        This method is routed through CognitionKernel for governance approval.

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate in response

        Returns:
            Dictionary with response and metadata
        """
        return self._execute_through_kernel(
            action=self._do_process_long_conversation,
            action_name=f"LongContextAgent.process_long_conversation[{self.model_name}]",
            action_args=(messages, system_prompt, max_tokens),
            requires_approval=True,
            risk_level="medium",
            metadata={
                "model": self.model_name,
                "message_count": len(messages),
                "max_tokens": max_tokens,
            },
        )

    def _do_process_long_conversation(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Internal implementation of long conversation processing."""
        try:
            # Calculate context size
            estimated_tokens = self._estimate_tokens(messages, system_prompt)

            if estimated_tokens > self.max_context_tokens:
                return {
                    "success": False,
                    "error": f"Context size ({estimated_tokens} tokens) exceeds maximum ({self.max_context_tokens})",
                    "estimated_tokens": estimated_tokens,
                }

            # NOTE: This is a placeholder for actual model inference
            # In production, this would call the actual model API/inference
            response = self._inference_placeholder(messages, system_prompt, max_tokens)

            return {
                "success": True,
                "response": response,
                "estimated_tokens": estimated_tokens,
                "model": self.model_name,
            }

        except Exception as e:
            logger.error("Error in long context processing: %s", e)
            return {"success": False, "error": str(e)}

    def analyze_large_document(
        self,
        document: str,
        query: str,
        chunk_size: int | None = None,
    ) -> dict[str, Any]:
        """Analyze a large document with context-aware processing.

        This method is routed through CognitionKernel for governance approval.

        Args:
            document: Large document text
            query: Analysis query
            chunk_size: Optional chunk size for processing

        Returns:
            Dictionary with analysis results
        """
        return self._execute_through_kernel(
            action=self._do_analyze_large_document,
            action_name=f"LongContextAgent.analyze_large_document[{self.model_name}]",
            action_args=(document, query, chunk_size),
            requires_approval=True,
            risk_level="medium",
            metadata={
                "model": self.model_name,
                "document_length": len(document),
                "query": query[:100],
            },
        )

    def _do_analyze_large_document(
        self,
        document: str,
        query: str,
        chunk_size: int | None,
    ) -> dict[str, Any]:
        """Internal implementation of large document analysis."""
        try:
            doc_tokens = self._estimate_tokens([{"role": "user", "content": document}])

            if doc_tokens > self.max_context_tokens * 0.8:
                logger.warning(
                    "Document size (%d tokens) is close to max context (%d)",
                    doc_tokens,
                    self.max_context_tokens,
                )

            # NOTE: Placeholder for actual document analysis
            result = self._analyze_placeholder(document, query)

            return {
                "success": True,
                "analysis": result,
                "document_tokens": doc_tokens,
                "model": self.model_name,
            }

        except Exception as e:
            logger.error("Error in document analysis: %s", e)
            return {"success": False, "error": str(e)}

    def compress_context(
        self,
        messages: list[dict[str, str]],
        target_tokens: int,
    ) -> dict[str, Any]:
        """Compress conversation context while preserving key information.

        Args:
            messages: Conversation messages to compress
            target_tokens: Target token count after compression

        Returns:
            Dictionary with compressed context
        """
        return self._execute_through_kernel(
            action=self._do_compress_context,
            action_name=f"LongContextAgent.compress_context[{self.model_name}]",
            action_args=(messages, target_tokens),
            requires_approval=False,
            risk_level="low",
            metadata={"message_count": len(messages), "target_tokens": target_tokens},
        )

    def _do_compress_context(
        self,
        messages: list[dict[str, str]],
        target_tokens: int,
    ) -> dict[str, Any]:
        """Internal implementation of context compression."""
        try:
            current_tokens = self._estimate_tokens(messages)

            if current_tokens <= target_tokens:
                return {
                    "success": True,
                    "compressed_messages": messages,
                    "original_tokens": current_tokens,
                    "compressed_tokens": current_tokens,
                }

            # Simple compression: keep system messages and recent messages
            compressed = []
            tokens_used = 0

            # Keep system messages
            for msg in messages:
                if msg.get("role") == "system":
                    compressed.append(msg)
                    tokens_used += self._estimate_tokens([msg])

            # Add recent messages in reverse order until target reached
            for msg in reversed(messages):
                if msg.get("role") != "system":
                    msg_tokens = self._estimate_tokens([msg])
                    if tokens_used + msg_tokens <= target_tokens:
                        compressed.insert(1, msg)  # Insert after system messages
                        tokens_used += msg_tokens

            return {
                "success": True,
                "compressed_messages": compressed,
                "original_tokens": current_tokens,
                "compressed_tokens": tokens_used,
                "compression_ratio": current_tokens / max(tokens_used, 1),
            }

        except Exception as e:
            logger.error("Error in context compression: %s", e)
            return {"success": False, "error": str(e)}

    def get_context_stats(self) -> dict[str, Any]:
        """Get current context statistics.

        Returns:
            Dictionary with context statistics
        """
        return {
            "model": self.model_name,
            "max_context_tokens": self.max_context_tokens,
            "current_context_size": self.current_context_size,
            "history_length": len(self.context_history),
            "context_utilization": (
                self.current_context_size / self.max_context_tokens if self.max_context_tokens > 0 else 0
            ),
        }

    def _estimate_tokens(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> int:
        """Estimate token count for messages.

        This is a rough estimation. In production, use the model's tokenizer.

        Args:
            messages: List of messages
            system_prompt: Optional system prompt

        Returns:
            Estimated token count
        """
        total_chars = 0

        if system_prompt:
            total_chars += len(system_prompt)

        for msg in messages:
            content = msg.get("content", "")
            total_chars += len(content)

        # Rough estimate: ~4 characters per token
        return total_chars // 4

    def _inference_placeholder(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        max_tokens: int,
    ) -> str:
        """Placeholder for actual model inference.

        In production, this would call the actual model API.
        """
        return (
            f"[Long-context response placeholder for {self.model_name}]\n"
            f"Processed {len(messages)} messages with {self._estimate_tokens(messages)} tokens.\n"
            f"Max tokens: {max_tokens}"
        )

    def _analyze_placeholder(self, document: str, query: str) -> str:
        """Placeholder for actual document analysis.

        In production, this would perform actual analysis.
        """
        return (
            f"[Document analysis placeholder]\n"
            f"Document length: {len(document)} characters\n"
            f"Query: {query}\n"
            f"Analysis would be performed here using {self.model_name}"
        )
