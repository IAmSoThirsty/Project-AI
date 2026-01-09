#!/usr/bin/env python3
"""
Command-line interface for DeepSeek V3.2 inference.

Usage:
    # Simple completion
    python -m scripts.deepseek_v32_cli "Your prompt here"

    # Chat mode
    python -m scripts.deepseek_v32_cli --mode chat "Hello, how are you?"

    # With custom parameters
    python -m scripts.deepseek_v32_cli --temperature 0.8 --max-tokens 256 "Explain quantum computing"

    # Multi-turn chat (interactive)
    python -m scripts.deepseek_v32_cli --mode chat --interactive
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from app.core.deepseek_v32_inference import DeepSeekV32  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_result(result: dict, mode: str) -> None:
    """Pretty print inference result.

    Args:
        result: Result dictionary from DeepSeek
        mode: Inference mode (completion or chat)
    """
    if not result["success"]:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return

    print("\n" + "=" * 60)
    print(f"✅ DeepSeek V3.2 Response ({mode} mode)")
    print("=" * 60)

    if mode == "completion":
        print(f"\nPrompt: {result.get('prompt', '')}")
        print(f"\nGenerated:\n{result.get('text', '')}")
    elif mode == "chat":
        # Extract only the new response (after the prompt)
        full_text = result.get('text', '')
        print(f"\nAssistant: {full_text}")

    print("\n" + "=" * 60)
    print(f"Model: {result.get('model', 'N/A')}")
    print("=" * 60 + "\n")


def interactive_chat(deepseek: DeepSeekV32, args: argparse.Namespace) -> None:
    """Run interactive chat session.

    Args:
        deepseek: Initialized DeepSeek instance
        args: Command-line arguments
    """
    print("\n" + "=" * 60)
    print("🤖 DeepSeek V3.2 Interactive Chat")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'clear' to clear conversation history")
    print("Type 'info' to see model information")
    print("=" * 60 + "\n")

    messages = []

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == "clear":
                messages = []
                print("\n🗑️  Conversation history cleared\n")
                continue

            if user_input.lower() == "info":
                info = deepseek.get_model_info()
                print("\n📊 Model Information:")
                print(json.dumps(info, indent=2))
                print()
                continue

            # Add user message
            messages.append({"role": "user", "content": user_input})

            # Generate response
            print("\n🤔 Thinking...", end="", flush=True)
            result = deepseek.generate_chat(
                messages=messages,
                max_new_tokens=args.max_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
            )
            print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear "Thinking..."

            if not result["success"]:
                print(f"❌ Error: {result.get('error', 'Unknown error')}\n")
                # Remove last user message on error
                messages.pop()
                continue

            # Extract assistant response
            assistant_text = result.get("text", "")
            print(f"Assistant: {assistant_text}\n")

            # Add assistant message to history
            messages.append({"role": "assistant", "content": assistant_text})

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Type 'exit' to quit or continue chatting.\n")
        except Exception as e:
            logger.error(f"Error in interactive chat: {e}")
            print(f"\n❌ Unexpected error: {e}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DeepSeek V3.2 Mixture-of-Experts Language Model CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple completion
  %(prog)s "Explain machine learning"

  # Chat mode with custom temperature
  %(prog)s --mode chat --temperature 0.9 "Tell me a story"

  # Interactive chat session
  %(prog)s --mode chat --interactive

  # With custom model and parameters
  %(prog)s --model deepseek-ai/deepseek-v3 --max-tokens 512 "Your prompt"
        """,
    )

    # Main arguments
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",
        help="Input prompt (required unless --interactive)",
    )

    # Mode selection
    parser.add_argument(
        "--mode",
        type=str,
        choices=["completion", "chat"],
        default="completion",
        help="Inference mode (default: completion)",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive chat session (only for chat mode)",
    )

    # Model configuration
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Hugging Face model name (default: deepseek-ai/deepseek-v3)",
    )

    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "mps", "cpu"],
        default=None,
        help="Device for inference (default: auto-detect)",
    )

    # Generation parameters
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum tokens to generate (default: 512)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature 0.0-2.0 (default: 0.7)",
    )

    parser.add_argument(
        "--top-p",
        type=float,
        default=0.9,
        help="Nucleus sampling threshold (default: 0.9)",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=50,
        help="Top-k sampling parameter (default: 50)",
    )

    parser.add_argument(
        "--no-sample",
        action="store_true",
        help="Use greedy decoding instead of sampling",
    )

    # Content filter
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Disable content filtering",
    )

    # Output options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if not args.interactive and not args.prompt:
        parser.error("Prompt is required unless --interactive is specified")

    if args.interactive and args.mode != "chat":
        parser.error("--interactive can only be used with --mode chat")

    try:
        # Initialize DeepSeek
        print("🚀 Initializing DeepSeek V3.2...", flush=True)
        deepseek = DeepSeekV32(
            model_name=args.model,
            device=args.device,
            max_length=args.max_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            top_k=args.top_k,
        )

        # Disable content filter if requested
        if args.no_filter:
            deepseek.content_filter_enabled = False

        # Interactive mode
        if args.interactive:
            interactive_chat(deepseek, args)
            return

        # Single inference
        if args.mode == "completion":
            result = deepseek.generate_completion(
                prompt=args.prompt,
                max_new_tokens=args.max_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
                do_sample=not args.no_sample,
            )
        else:  # chat mode
            messages = [{"role": "user", "content": args.prompt}]
            result = deepseek.generate_chat(
                messages=messages,
                max_new_tokens=args.max_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                top_k=args.top_k,
                do_sample=not args.no_sample,
            )

        # Output result
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(result, args.mode)

        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception("Fatal error")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
