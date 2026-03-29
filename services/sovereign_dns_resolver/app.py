# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / app.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / app.py



from flask import Flask, request, jsonify
import requests
from tools.kernel_bonder import KernelBonder

app = Flask(__name__)
bonder = KernelBonder()

@app.route('/dns-query', methods=['GET'])
def doh():
    domain = request.args.get('name')
    if not domain:
        return jsonify({"error": "name parameter required"}), 400
    
    # Live DoH request
    try:
        raw = requests.get(f"https://cloudflare-dns.com/dns-query?name={domain}", 
                           headers={"accept": "application/dns-json"}).json()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Yggdrasil Inhale
    result = bonder.inhale({"domain": domain, "response": raw}, "leaf_group_01")
    bonder.exhale(result)

    if result.get("status") == "verified":
        return jsonify({"Answer": raw.get("Answer", [])})
    else:
        return jsonify({"status": "deceived", "shadow_thirst": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8053)
