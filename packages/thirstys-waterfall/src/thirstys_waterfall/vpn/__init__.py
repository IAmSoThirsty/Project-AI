"""VPN subsystem for Thirstys Waterfall"""

from .dns_protection import DNSProtection
from .kill_switch import KillSwitch
from .multi_hop import MultiHopRouter
from .vpn_manager import VPNManager

__all__ = ["DNSProtection", "KillSwitch", "MultiHopRouter", "VPNManager"]
