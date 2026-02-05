"""Tab Manager with isolation"""

from typing import Dict, Any, Optional, List
import uuid
import logging


class TabManager:
    """
    Manages browser tabs with complete isolation.
    Each tab has separate storage, cookies, and execution context.
    """

    def __init__(self, isolation_enabled: bool = True):
        self.isolation_enabled = isolation_enabled
        self.logger = logging.getLogger(__name__)
        self._tabs: Dict[str, Dict[str, Any]] = {}

    def create_tab(self, url: Optional[str] = None) -> str:
        """
        Create new isolated tab.

        Returns:
            Tab ID
        """
        tab_id = str(uuid.uuid4())

        self._tabs[tab_id] = {
            'id': tab_id,
            'url': url or 'about:blank',
            'title': 'New Tab',
            'isolated': self.isolation_enabled,
            'config': {},
            'storage': {},  # Empty - no persistent storage
            'cookies': {},  # Empty - no cookies
            'history': []   # Empty - no history
        }

        self.logger.debug(f"Created tab: {tab_id}")
        return tab_id

    def close_tab(self, tab_id: str):
        """Close tab and destroy all its data"""
        if tab_id in self._tabs:
            # Clear all tab data
            self._tabs[tab_id]['storage'].clear()
            self._tabs[tab_id]['cookies'].clear()
            self._tabs[tab_id]['history'].clear()

            # Remove tab
            del self._tabs[tab_id]
            self.logger.debug(f"Closed tab: {tab_id}")

    def close_all_tabs(self):
        """Close all tabs"""
        tab_ids = list(self._tabs.keys())
        for tab_id in tab_ids:
            self.close_tab(tab_id)

    def navigate(self, tab_id: str, url: str) -> bool:
        """
        Navigate tab to URL.
        History is NOT stored in incognito mode.

        Returns:
            True if navigation successful
        """
        if tab_id not in self._tabs:
            return False

        tab = self._tabs[tab_id]
        tab['url'] = url

        # Don't store in history (privacy-first)
        self.logger.debug(f"Tab {tab_id} navigated to {url} (not stored in history)")

        return True

    def get_tab(self, tab_id: str) -> Optional[Dict[str, Any]]:
        """Get tab information"""
        return self._tabs.get(tab_id)

    def get_all_tabs(self) -> List[Dict[str, Any]]:
        """Get all tabs"""
        return list(self._tabs.values())

    def set_tab_config(self, tab_id: str, config: Dict[str, Any]):
        """Set tab configuration"""
        if tab_id in self._tabs:
            self._tabs[tab_id]['config'].update(config)

    def is_isolated(self, tab_id: str) -> bool:
        """Check if tab is isolated"""
        if tab_id in self._tabs:
            return self._tabs[tab_id]['isolated']
        return False
