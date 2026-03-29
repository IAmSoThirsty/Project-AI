# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / dns_test_harness.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign-Native / DNS Test Harness v2.1                         #


import requests
from tools.kernel_bonder import KernelBonder

bonder = KernelBonder()

def doh_query(domain: str):
    """Live DNS-over-HTTPS query for OctoReflex interception testing"""
    print(f"--- [LIVE DoH] Querying: {domain} ---")
    try:
        r = requests.get(f"https://cloudflare-dns.com/dns-query?name={domain}", 
                         headers={"accept": "application/dns-json"})
        return r.json().get("Answer", [{}])[0].get("data", "NXDOMAIN")
    except Exception as e:
        print(f"⚠️ DoH Error: {e}")
        return "NXDOMAIN"

def run_test(domain: str, leaf: str = "leaf_group_01"):
    raw = doh_query(domain)
    # Manual trigger of Shadow Thirst for verification
    force_failure = False
    if "malicious" in domain:
        force_failure = True
        
    result = bonder.inhale({"domain": domain, "response": raw, "force_failure": force_failure}, leaf)
    bonder.exhale(result)

if __name__ == "__main__":
    run_test("zenodo.org")
    run_test("malicious-phish.example")
