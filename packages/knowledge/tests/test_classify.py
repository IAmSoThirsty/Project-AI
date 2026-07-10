from __future__ import annotations

from knowledge.classify import classify_sensitivity, classify_topic, is_in_scope


def test_offensive_sensitivity_detected() -> None:
    assert classify_sensitivity("The Black Book of Computer Viruses", "") == "offensive"
    assert classify_sensitivity("Shellcoder's Handbook", "buffer overflow") == "offensive"


def test_dual_use_sensitivity_detected() -> None:
    assert classify_sensitivity("Metasploit Penetration Testing", "") == "dual_use"
    assert classify_sensitivity("Kali Linux Cookbook", "exploit") == "dual_use"


def test_educational_is_default() -> None:
    assert classify_sensitivity("Learning Python", "decorators and generators") == "educational"
    assert classify_sensitivity("CISSP Study Guide", "risk management") == "educational"


def test_defensive_guard_overrides_offensive_substring() -> None:
    # "creating security policies" contains an offensive-list substring but is defensive.
    assert classify_sensitivity("CEHv6 Module 49 Creating Security Policies", "") == "educational"


def test_topic_classification() -> None:
    assert classify_topic("Beginning Python", "python programming") == "programming"
    assert classify_topic("CCNA Security", "network router firewall") == "networking"
    assert classify_topic("PHP5 and MySQL Bible", "web development apache") == "web"
    assert classify_topic("The Code Book", "cipher encryption") == "cryptography"
    assert classify_topic("Totally Unknown Title", "nothing matches here zzz") == "general"


def test_out_of_scope_detection() -> None:
    assert is_in_scope("Learning Python", "programming") is True
    assert is_in_scope("Security Analysis - 1934 - Ben Graham Dodd", "") is False
    assert is_in_scope("13 Things The Government Doesn't Want You To Know", "") is False
