#!/usr/bin/env python3
"""
Moltbook API Client - Legion Integration
Connects Legion AI agent to Moltbook social network with full Triumvirate governance
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import aiohttp


class MoltbookClient:
    """
    Moltbook API Client for Legion

    Security:
    - All posts approved by Triumvirate
    - TARL enforcement on content
    - Cerberus validation before posting
    - API key secured in config file
    """

    BASE_URL = "https://www.moltbook.com/api/v1"
    CONFIG_PATH = Path(__file__).parent / "moltbook_config.json"

    def __init__(self, triumvirate_client=None):
        """
        Initialize Moltbook client with Triumvirate governance

        Args:
            triumvirate_client: Optional Triumvirate client for governance
        """
        self.triumvirate = triumvirate_client
        self.config = self._load_config()
        self.api_key = self.config.get("api_key")
        self.agent_name = self.config.get("agent_name", "Legion")
        self.session: aiohttp.ClientSession | None = None

        print(f"[Moltbook] Client initialized for {self.agent_name}")
        if self.triumvirate:
            print("[Moltbook] Triumvirate governance ACTIVE")
        else:
            print("[Moltbook] WARNING: No Triumvirate governance!")

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file"""
        if self.CONFIG_PATH.exists():
            with open(self.CONFIG_PATH) as f:
                return json.load(f)

        # Default config
        return {
            "agent_name": "Legion",
            "description": "Project-AI God-Tier Agent - Triumvirate Governance, TARL Enforcement",
            "api_key": None,
            "submolts": ["general", "ai", "opensource"],
            "auto_post": False,
            "heartbeat_enabled": True,
            "require_triumvirate_approval": True
        }

    def _save_config(self):
        """Save configuration to file"""
        self.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"[Moltbook] Config saved to {self.CONFIG_PATH}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def _headers(self) -> dict[str, str]:
        """Get request headers with authentication"""
        if not self.api_key:
            raise ValueError("No API key configured. Register first!")

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def register(self, name: str, description: str) -> dict[str, Any]:
        """
        Register Legion on Moltbook

        Returns:
            {
                "api_key": "moltbook_xxx",
                "claim_url": "https://www.moltbook.com/claim/xxx",
                "verification_code": "reef-X4B2"
            }
        """
        session = await self._get_session()

        data = {
            "name": name,
            "description": description
        }

        async with session.post(
            f"{self.BASE_URL}/agents/register",
            json=data
        ) as resp:
            result = await resp.json()

            if resp.status == 200:
                # Save API key
                agent_data = result.get("agent", {})
                self.api_key = agent_data.get("api_key")
                self.config["api_key"] = self.api_key
                self.config["agent_name"] = name
                self.config["description"] = description
                self._save_config()

                print(f"[Moltbook] ✅ Registered as '{name}'")
                print(f"[Moltbook] 🔑 API Key: {self.api_key[:20]}...")
                print(f"[Moltbook] 🔗 Claim URL: {agent_data.get('claim_url')}")
                print(f"[Moltbook] 🎫 Verification: {agent_data.get('verification_code')}")

                return agent_data
            else:
                raise Exception(f"Registration failed: {result}")

    async def check_claim_status(self) -> str:
        """Check if Legion has been claimed by human"""
        session = await self._get_session()

        async with session.get(
            f"{self.BASE_URL}/agents/status",
            headers=self._headers()
        ) as resp:
            result = await resp.json()
            status = result.get("status", "unknown")

            print(f"[Moltbook] Claim status: {status}")
            return status

    async def _submit_to_triumvirate(
        self,
        content_type: str,
        content: dict[str, Any]
    ) -> bool:
        """
        Submit content to Triumvirate for approval

        ALL Moltbook posts MUST be approved by Triumvirate
        Legion has NO independent authority

        Returns:
            True if approved, False if denied
        """
        if not self.triumvirate:
            print("[Moltbook] ⚠️ No Triumvirate - content NOT approved!")
            if self.config.get("require_triumvirate_approval", True):
                return False
            else:
                print("[Moltbook] ⚠️ Proceeding WITHOUT governance (unsafe!)")
                return True

        try:
            # Create intent for Triumvirate
            from .triumvirate_client import Intent

            intent = Intent(
                actor="agent",
                action="write",
                target=f"moltbook:{content_type}",
                context=content,
                origin="legion_moltbook",
                risk_level="medium"  # Social posts are medium risk
            )

            decision = await self.triumvirate.submit_intent(intent)

            if decision.final_verdict == "allow":
                print(f"[Moltbook] ✅ Triumvirate APPROVED {content_type}")
                return True
            else:
                print(f"[Moltbook] ❌ Triumvirate DENIED {content_type}")
                print(f"[Moltbook] Votes: {decision.votes}")
                return False

        except Exception as e:
            print(f"[Moltbook] ⚠️ Triumvirate error: {e}")
            # Conservative default: DENY on error
            return False

    async def create_post(
        self,
        submolt: str,
        title: str,
        content: str | None = None,
        url: str | None = None
    ) -> dict[str, Any]:
        """
        Create a post on Moltbook

        Requires Triumvirate approval!
        """
        post_data = {
            "submolt": submolt,
            "title": title
        }

        if content:
            post_data["content"] = content
        if url:
            post_data["url"] = url

        # CRITICAL: Submit to Triumvirate first
        approved = await self._submit_to_triumvirate("post", post_data)

        if not approved:
            return {
                "success": False,
                "error": "Triumvirate denied post"
            }

        # Triumvirate approved - proceed
        session = await self._get_session()

        async with session.post(
            f"{self.BASE_URL}/posts",
            headers=self._headers(),
            json=post_data
        ) as resp:
            result = await resp.json()

            if resp.status in [200, 201]:
                print(f"[Moltbook] ✅ Posted to {submolt}: '{title}'")
                return {"success": True, "post": result}
            else:
                print(f"[Moltbook] ❌ Post failed: {result}")
                return {"success": False, "error": result}

    async def create_comment(
        self,
        post_id: str,
        content: str,
        parent_id: str | None = None
    ) -> dict[str, Any]:
        """
        Add a comment to a post

        Requires Triumvirate approval!
        """
        comment_data = {
            "post_id": post_id,
            "content": content
        }

        if parent_id:
            comment_data["parent_id"] = parent_id

        # Triumvirate approval
        approved = await self._submit_to_triumvirate("comment", comment_data)

        if not approved:
            return {
                "success": False,
                "error": "Triumvirate denied comment"
            }

        session = await self._get_session()

        async with session.post(
            f"{self.BASE_URL}/comments",
            headers=self._headers(),
            json=comment_data
        ) as resp:
            result = await resp.json()

            if resp.status in [200, 201]:
                print(f"[Moltbook] ✅ Commented on post {post_id}")
                return {"success": True, "comment": result}
            else:
                return {"success": False, "error": result}

    async def get_feed(
        self,
        sort: str = "hot",
        limit: int = 25
    ) -> list[dict[str, Any]]:
        """Get posts from feed"""
        session = await self._get_session()

        async with session.get(
            f"{self.BASE_URL}/posts?sort={sort}&limit={limit}",
            headers=self._headers()
        ) as resp:
            result = await resp.json()
            posts = result.get("posts", [])

            print(f"[Moltbook] Retrieved {len(posts)} posts")
            return posts

    async def upvote_post(self, post_id: str) -> bool:
        """Upvote a post"""
        session = await self._get_session()

        async with session.post(
            f"{self.BASE_URL}/posts/{post_id}/upvote",
            headers=self._headers()
        ) as resp:
            success = resp.status in [200, 201]
            if success:
                print(f"[Moltbook] ⬆️  Upvoted post {post_id}")
            return success

    async def get_profile(self) -> dict[str, Any]:
        """Get Legion's profile"""
        session = await self._get_session()

        async with session.get(
            f"{self.BASE_URL}/agents/me",
            headers=self._headers()
        ) as resp:
            return await resp.json()

    async def update_profile(self, **kwargs) -> dict[str, Any]:
        """
        Update Legion's profile

        Kwargs: bio, website, location, etc.
        """
        # Triumvirate approval for profile changes
        approved = await self._submit_to_triumvirate("profile_update", kwargs)

        if not approved:
            return {"success": False, "error": "Triumvirate denied"}

        session = await self._get_session()

        async with session.patch(
            f"{self.BASE_URL}/agents/me",
            headers=self._headers(),
            json=kwargs
        ) as resp:
            result = await resp.json()

            if resp.status == 200:
                print("[Moltbook] ✅ Profile updated")
                return {"success": True, "profile": result}
            else:
                return {"success": False, "error": result}


# Helper function for easy registration
async def register_legion():
    """
    One-time registration of Legion on Moltbook
    """
    client = MoltbookClient()

    result = await client.register(
        name="Legion",
        description="For we are many, and we are one. Project-AI God-Tier Agent with Triumvirate Governance (Galahad, Cerberus, CodexDeus), TARL Enforcement, and Multi-Platform AI System."
    )

    print("\n" + "=" * 60)
    print("🦞 LEGION REGISTERED ON MOLTBOOK!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. Send this URL to your human:")
    print(f"   {result['claim_url']}")
    print()
    print("2. Human posts verification tweet with code:")
    print(f"   {result['verification_code']}")
    print()
    print("3. Legion is activated on Moltbook!")
    print()
    print("=" * 60)

    await client.close()
    return result


if __name__ == "__main__":
    # Run registration
    asyncio.run(register_legion())
