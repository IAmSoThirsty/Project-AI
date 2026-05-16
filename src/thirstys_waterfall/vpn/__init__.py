"""VPN subsystem for Thirstys Waterfall"""

from .vpn_manager import VPNManager
from .multi_hop import MultiHopRouter
from .kill_switch import KillSwitch
from .dns_protection import DNSProtection

__all__ = ["VPNManager", "MultiHopRouter", "KillSwitch", "DNSProtection"]
