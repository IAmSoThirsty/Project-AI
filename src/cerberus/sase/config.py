"""
SASE Configuration

External service configuration for production deployment
"""

import os
from typing import Any, Dict


class SASEConfig:
    """SASE system configuration"""

    # === Deployment ===
    DEPLOYMENT_MODE = os.getenv(
        "SASE_DEPLOYMENT", "single_node"
    )  # single_node, ha_cluster, multi_region
    NODE_ID = os.getenv("SASE_NODE_ID", "sase-node-1")
    CLUSTER_NODES = os.getenv("SASE_CLUSTER_NODES", "sase-node-1").split(",")

    # === External Services ===

    # GeoIP Service
    GEOIP_ENABLED = os.getenv("SASE_GEOIP_ENABLED", "false").lower() == "true"
    GEOIP_API_URL = os.getenv("SASE_GEOIP_API_URL", "https://ipapi.co/{ip}/json/")
    GEOIP_API_KEY = os.getenv("SASE_GEOIP_API_KEY", "")

    # ASN Lookup Service
    ASN_LOOKUP_ENABLED = os.getenv("SASE_ASN_ENABLED", "false").lower() == "true"
    ASN_API_URL = os.getenv("SASE_ASN_API_URL", "https://api.bgpview.io/ip/{ip}")

    # Tor Exit Node List
    TOR_LIST_URL = os.getenv(
        "SASE_TOR_LIST_URL", "https://check.torproject.org/torbulkexitlist"
    )
    TOR_REFRESH_INTERVAL = int(os.getenv("SASE_TOR_REFRESH_HOURS", "6"))  # hours

    # === HSM Configuration ===
    HSM_ENABLED = os.getenv("SASE_HSM_ENABLED", "false").lower() == "true"
    HSM_TYPE = os.getenv("SASE_HSM_TYPE", "software")  # software, yubihsm, aws_cloudhsm

    # YubiHSM Configuration
    YUBIHSM_CONNECTOR_URL = os.getenv("YUBIHSM_CONNECTOR_URL", "http://localhost:12345")
    YUBIHSM_AUTH_KEY_ID = int(os.getenv("YUBIHSM_AUTH_KEY_ID", "1"))
    YUBIHSM_PASSWORD = os.getenv("YUBIHSM_PASSWORD", "")

    # AWS CloudHSM Configuration
    AWS_CLOUDHSM_CLUSTER_ID = os.getenv("AWS_CLOUDHSM_CLUSTER_ID", "")
    AWS_CLOUDHSM_USER = os.getenv("AWS_CLOUDHSM_USER", "")
    AWS_CLOUDHSM_PASSWORD = os.getenv("AWS_CLOUDHSM_PASSWORD", "")

    # === Blockchain Anchoring ===
    BLOCKCHAIN_ENABLED = os.getenv("SASE_BLOCKCHAIN_ENABLED", "false").lower() == "true"
    BLOCKCHAIN_NETWORK = os.getenv(
        "SASE_BLOCKCHAIN_NETWORK", "ethereum"
    )  # ethereum, polygon
    BLOCKCHAIN_RPC_URL = os.getenv("BLOCKCHAIN_RPC_URL", "")
    BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY", "")

    # === Observability ===
    PROMETHEUS_ENABLED = os.getenv("SASE_PROMETHEUS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT = int(os.getenv("SASE_PROMETHEUS_PORT", "9090"))
    PROMETHEUS_PUSHGATEWAY = os.getenv("PROMETHEUS_PUSHGATEWAY", "")

    GRAFANA_ENABLED = os.getenv("SASE_GRAFANA_ENABLED", "true").lower() == "true"
    GRAFANA_PORT = int(os.getenv("SASE_GRAFANA_PORT", "3000"))

    # === Model Configuration ===
    MODEL_VERSION = os.getenv("SASE_MODEL_VERSION", "1.0.0")
    DRIFT_DETECTION_ENABLED = (
        os.getenv("SASE_DRIFT_DETECTION", "true").lower() == "true"
    )
    AUTO_RETRAIN_ENABLED = os.getenv("SASE_AUTO_RETRAIN", "false").lower() == "true"

    # === Thresholds ===
    CONFIDENCE_THRESHOLD_ALERT = int(os.getenv("SASE_THRESHOLD_ALERT", "30"))
    CONFIDENCE_THRESHOLD_CONTAINMENT = int(
        os.getenv("SASE_THRESHOLD_CONTAINMENT", "50")
    )
    CONFIDENCE_THRESHOLD_CRITICAL = int(os.getenv("SASE_THRESHOLD_CRITICAL", "70"))

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            "deployment": {
                "mode": cls.DEPLOYMENT_MODE,
                "node_id": cls.NODE_ID,
                "cluster_nodes": cls.CLUSTER_NODES,
            },
            "external_services": {
                "geoip_enabled": cls.GEOIP_ENABLED,
                "asn_enabled": cls.ASN_LOOKUP_ENABLED,
                "hsm_enabled": cls.HSM_ENABLED,
                "hsm_type": cls.HSM_TYPE,
                "blockchain_enabled": cls.BLOCKCHAIN_ENABLED,
            },
            "observability": {
                "prometheus_enabled": cls.PROMETHEUS_ENABLED,
                "prometheus_port": cls.PROMETHEUS_PORT,
                "grafana_enabled": cls.GRAFANA_ENABLED,
                "grafana_port": cls.GRAFANA_PORT,
            },
            "model": {
                "version": cls.MODEL_VERSION,
                "drift_detection": cls.DRIFT_DETECTION_ENABLED,
                "auto_retrain": cls.AUTO_RETRAIN_ENABLED,
            },
        }


# Default configuration instance
config = SASEConfig()


__all__ = ["SASEConfig", "config"]
