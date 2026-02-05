"""Setup Wizard - Complete first-time setup"""
import logging
import os

class SetupWizard:
    def __init__(self, god_tier_encryption):
        self.logger = logging.getLogger(__name__)
        self.god_tier_encryption = god_tier_encryption
        self.setup_file = os.path.expanduser('~/.thirstys_waterfall_setup')

    def is_first_run(self):
        return not os.path.exists(self.setup_file)

    def run_setup(self):
        self.logger.info("THIRSTYS WATERFALL - SETUP WIZARD")

        from .notice_letter import NoticeLetterManager
        notice = NoticeLetterManager()
        if not notice.show_notice_and_get_acceptance():
            return {'setup_complete': False}

        from .captcha_system import AntiBotCaptchaSystem
        captcha = AntiBotCaptchaSystem()
        if not captcha.verify_human()['verified']:
            return {'setup_complete': False}

        from .usage_tutorial import UsageTutorial
        tutorial = UsageTutorial()
        tutorial.show_interactive_tutorial()

        self._complete_setup()
        return {'setup_complete': True}

    def _complete_setup(self):
        with open(self.setup_file, 'w') as f:
            f.write("complete")
