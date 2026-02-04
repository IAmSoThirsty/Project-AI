"""
SOVEREIGN WAR ROOM - Core System

Main orchestration system that coordinates all components and executes
adversarial testing scenarios.
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from .scenario import Scenario, ScenarioLibrary, ScenarioType, DifficultyLevel
from .governance import GovernanceEngine, ComplianceReport
from .proof import ProofSystem, ProofType
from .scoreboard import Scoreboard, Score
from .crypto import CryptoEngine
from .bundle import BundleManager


class SovereignWarRoom:
    """
    Main SOVEREIGN WAR ROOM system.
    
    Orchestrates adversarial testing of AI systems through five rounds
    of progressively difficult scenarios.
    """
    
    def __init__(
        self,
        governance_rules_path: Optional[str] = None,
        bundle_dir: Optional[str] = None
    ):
        """
        Initialize SOVEREIGN WAR ROOM.
        
        Args:
            governance_rules_path: Optional path to custom governance rules
            bundle_dir: Optional directory for bundles
        """
        self.crypto = CryptoEngine()
        self.governance = GovernanceEngine(governance_rules_path)
        self.proof_system = ProofSystem(self.crypto)
        self.scoreboard = Scoreboard()
        self.bundle_manager = BundleManager(bundle_dir)
        
        self.active_scenarios: Dict[str, Scenario] = {}
        self.results: List[Dict[str, Any]] = []
    
    def load_scenarios(self, round_number: Optional[int] = None) -> List[Scenario]:
        """
        Load scenarios for testing.
        
        Args:
            round_number: Optional filter by round (1-5)
            
        Returns:
            List of loaded scenarios
        """
        if round_number:
            if round_number == 1:
                scenarios = ScenarioLibrary.get_round_1_scenarios()
            elif round_number == 2:
                scenarios = ScenarioLibrary.get_round_2_scenarios()
            elif round_number == 3:
                scenarios = ScenarioLibrary.get_round_3_scenarios()
            elif round_number == 4:
                scenarios = ScenarioLibrary.get_round_4_scenarios()
            elif round_number == 5:
                scenarios = ScenarioLibrary.get_round_5_scenarios()
            else:
                raise ValueError("Round must be 1-5")
        else:
            scenarios = ScenarioLibrary.get_all_scenarios()
        
        # Store active scenarios
        for scenario in scenarios:
            self.active_scenarios[scenario.scenario_id] = scenario
        
        return scenarios
    
    def execute_scenario(
        self,
        scenario: Scenario,
        ai_system_response: Dict[str, Any],
        system_id: str = "test_system"
    ) -> Dict[str, Any]:
        """
        Execute a scenario and evaluate AI system response.
        
        Args:
            scenario: Scenario to execute
            ai_system_response: AI system's response to scenario
            system_id: Identifier for the AI system
            
        Returns:
            Execution results including scores and proofs
        """
        start_time = time.time()
        
        # Generate cryptographic challenge
        challenge = self.crypto.generate_challenge(
            scenario.scenario_id,
            scenario.difficulty.value
        )
        
        # Prepare context for governance evaluation
        context = {
            "scenario_id": scenario.scenario_id,
            "scenario_type": scenario.scenario_type.value,
            "difficulty": scenario.difficulty.value,
            "round_number": scenario.round_number,
            "constraints": scenario.constraints,
            "objectives": scenario.objectives
        }
        
        # Evaluate decision against governance rules
        compliance_report = self.governance.evaluate_decision(
            ai_system_response,
            context
        )
        
        # Verify cryptographic response
        is_valid, verification_error = self.crypto.verify_response(
            challenge,
            ai_system_response,
            scenario.expected_decision
        )
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Generate proofs
        decision_proof = self.proof_system.generate_decision_proof(
            scenario.scenario_id,
            ai_system_response,
            ai_system_response.get("reasoning", {}),
            compliance_report.model_dump()
        )
        
        compliance_proof = self.proof_system.generate_compliance_proof(
            scenario.scenario_id,
            compliance_report.model_dump()
        )
        
        # Calculate score
        score = self.scoreboard.calculate_score(
            system_id,
            scenario.scenario_id,
            scenario.model_dump(),
            ai_system_response,
            compliance_report.model_dump(),
            response_time_ms
        )
        
        # Create audit log entry
        audit_entry = self.crypto.create_audit_log_entry({
            "scenario_id": scenario.scenario_id,
            "system_id": system_id,
            "decision": ai_system_response.get("decision"),
            "compliance_status": compliance_report.overall_status.value,
            "score": score.sovereign_resilience_score
        })
        
        # Compile results
        result = {
            "scenario_id": scenario.scenario_id,
            "scenario_name": scenario.name,
            "system_id": system_id,
            "timestamp": datetime.utcnow().isoformat(),
            
            # Response data
            "decision": ai_system_response.get("decision"),
            "expected_decision": scenario.expected_decision,
            "response_valid": is_valid,
            "verification_error": verification_error,
            "response_time_ms": response_time_ms,
            
            # Compliance
            "compliance_status": compliance_report.overall_status.value,
            "violations": compliance_report.violations,
            "warnings": compliance_report.warnings,
            "recommendations": compliance_report.recommendations,
            
            # Score
            "score": score.model_dump(),
            "sovereign_resilience_score": score.sovereign_resilience_score,
            
            # Proofs
            "decision_proof_id": decision_proof.proof_id,
            "compliance_proof_id": compliance_proof.proof_id,
            
            # Audit
            "audit_entry": audit_entry
        }
        
        self.results.append(result)
        
        return result
    
    def run_round(
        self,
        round_number: int,
        ai_system_callback,
        system_id: str = "test_system"
    ) -> List[Dict[str, Any]]:
        """
        Run all scenarios for a specific round.
        
        Args:
            round_number: Round to run (1-5)
            ai_system_callback: Callable that takes scenario and returns response
            system_id: Identifier for the AI system
            
        Returns:
            List of execution results
        """
        scenarios = self.load_scenarios(round_number)
        round_results = []
        
        for scenario in scenarios:
            # Get AI system response
            ai_response = ai_system_callback(scenario)
            
            # Execute scenario
            result = self.execute_scenario(scenario, ai_response, system_id)
            round_results.append(result)
        
        return round_results
    
    def run_full_competition(
        self,
        ai_system_callback,
        system_id: str = "test_system"
    ) -> Dict[str, Any]:
        """
        Run all five rounds of competition.
        
        Args:
            ai_system_callback: Callable that takes scenario and returns response
            system_id: Identifier for the AI system
            
        Returns:
            Complete competition results
        """
        competition_results = {
            "system_id": system_id,
            "start_time": datetime.utcnow().isoformat(),
            "rounds": {}
        }
        
        for round_num in range(1, 6):
            print(f"\n=== ROUND {round_num} ===")
            round_results = self.run_round(round_num, ai_system_callback, system_id)
            competition_results["rounds"][f"round_{round_num}"] = round_results
        
        competition_results["end_time"] = datetime.utcnow().isoformat()
        
        # Get final performance metrics
        performance = self.scoreboard.get_system_performance(system_id)
        competition_results["final_performance"] = performance
        
        # Get leaderboard position
        leaderboard = self.scoreboard.get_leaderboard()
        competition_results["leaderboard_position"] = next(
            (i for i, entry in enumerate(leaderboard) if entry["system_id"] == system_id),
            None
        )
        
        return competition_results
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        return self.active_scenarios.get(scenario_id)
    
    def get_results(
        self,
        system_id: Optional[str] = None,
        round_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get execution results with optional filtering.
        
        Args:
            system_id: Optional filter by system
            round_number: Optional filter by round
            
        Returns:
            Filtered results list
        """
        results = self.results
        
        if system_id:
            results = [r for r in results if r["system_id"] == system_id]
        
        if round_number:
            # Filter by round based on scenario round_number
            results = [
                r for r in results
                if self.active_scenarios.get(r["scenario_id"], Scenario(
                    name="", description="", scenario_type=ScenarioType.ETHICAL_DILEMMA,
                    difficulty=DifficultyLevel.MEDIUM, round_number=0,
                    initial_state={}, constraints={}, objectives=[],
                    expected_decision="", success_criteria={}
                )).round_number == round_number
            ]
        
        return results
    
    def export_results(self, filename: str, format: str = "json"):
        """
        Export results to file.
        
        Args:
            filename: Output filename
            format: Export format (json, csv)
        """
        filepath = self.bundle_manager.export_results(
            self.results,
            filename,
            format
        )
        return filepath
    
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Get current leaderboard."""
        return self.scoreboard.get_leaderboard()
    
    def verify_result_integrity(self, result: Dict[str, Any]) -> bool:
        """
        Verify integrity of execution result.
        
        Args:
            result: Result to verify
            
        Returns:
            True if result is valid and untampered
        """
        # Verify audit entry
        audit_entry = result.get("audit_entry")
        if not audit_entry:
            return False
        
        if not self.crypto.verify_audit_log_entry(audit_entry):
            return False
        
        # Verify proofs
        decision_proof = self.proof_system.get_proof(result.get("decision_proof_id"))
        if decision_proof:
            verification = self.proof_system.verify_proof(decision_proof)
            if not verification["valid"]:
                return False
        
        compliance_proof = self.proof_system.get_proof(result.get("compliance_proof_id"))
        if compliance_proof:
            verification = self.proof_system.verify_proof(compliance_proof)
            if not verification["valid"]:
                return False
        
        return True
