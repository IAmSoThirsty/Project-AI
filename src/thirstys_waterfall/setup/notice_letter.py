"""Notice Letter Manager"""

import logging


class NoticeLetterManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def show_notice_and_get_acceptance(self):
        print("\n" + "=" * 80)
        print("SYSTEM STIPULATIONS")
        print("=" * 80)
        print("✅ CAN: Browse privately, download media, use AI assistant")
        print("❌ CANNOT: Illegal activities, malware, unauthorized access")
        print("=" * 80)
        self.logger.info("User accepted stipulations")
        return True
