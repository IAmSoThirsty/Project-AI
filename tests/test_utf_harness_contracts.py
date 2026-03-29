from __future__ import annotations

from app.core.battery_harness import BatteryServant
from app.core.master_harness import MasterOrchestrator
from app.core.ndt_harness import NDTServant


class RecordingBridge:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def execute_thirsty_file_with_contract(self, relative_path: str, context: dict):
        self.calls.append((relative_path, context))
        if relative_path.endswith("battery_passport.thirst"):
            return {"passport_record": {"health": {"status": "OPERATIONAL"}}}
        if relative_path.endswith("network_twin.thirsty"):
            return {
                "ndt_synchronized_record": {
                    "performance": {"loss": 0.00001},
                    "verdict": "SYNCHRONIZED_SUCCESS",
                }
            }
        if relative_path.endswith("metatheoretical_kernel.thirsty"):
            return {
                "world_model": "Ontological-Sovereignty",
                "kernel_action": "SOVEREIGN_EXECUTION",
                "theoretical_consensus": {"planned_action": "SOVEREIGN_EXECUTION"},
            }
        raise AssertionError(f"Unexpected path: {relative_path}")


def test_battery_servant_uses_contract_execution():
    bridge = RecordingBridge()
    servant = BatteryServant()
    servant.bridge = bridge

    result = servant.simulate_telemetry(3.7, 45.0, 500)

    assert result["passport_record"]["health"]["status"] == "OPERATIONAL"
    assert bridge.calls == [
        (
            "src/app/core/battery_passport.thirst",
            {"data": {"voltage": 3.7, "temperature": 45.0, "cycles": 500}},
        )
    ]


def test_ndt_servant_uses_contract_execution():
    bridge = RecordingBridge()
    servant = NDTServant()
    servant.bridge = bridge

    result = servant.run_protocol_test(["node-01", "node-02"], "RDMA")

    assert result["ndt_synchronized_record"]["verdict"] == "SYNCHRONIZED_SUCCESS"
    assert bridge.calls == [
        (
            "src/app/core/network_twin.thirsty",
            {
                "config": {
                    "nodes": ["node-01", "node-02"],
                    "target_protocol": "RDMA",
                }
            },
        )
    ]


def test_master_orchestrator_uses_contract_execution_for_all_phases():
    bridge = RecordingBridge()
    orchestrator = MasterOrchestrator()
    orchestrator.bridge = bridge

    orchestrator.synchronize_framework()

    assert [path for path, _context in bridge.calls] == [
        "src/app/core/battery_passport.thirst",
        "src/app/core/network_twin.thirsty",
        "src/app/core/metatheoretical_kernel.thirsty",
    ]
