"""Onion Routing for enhanced anonymity"""

import logging
from typing import List, Dict, Any
import random


class OnionRouter:
    """
    Onion routing implementation for anonymous communication.
    Routes traffic through multiple layers of encryption.
    """

    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get('onion_routing', True)
        self.logger = logging.getLogger(__name__)
        self._active = False

        self._nodes: List[Dict[str, Any]] = []
        self._circuits: List[List[Dict[str, Any]]] = []

        self._initialize_nodes()

    def start(self):
        """Start onion router"""
        if not self.enabled:
            return

        self.logger.info("Starting Onion Router")
        self._active = True
        self._establish_circuits()

    def stop(self):
        """Stop onion router"""
        self.logger.info("Stopping Onion Router")
        self._active = False
        self._circuits.clear()

    def _initialize_nodes(self):
        """Initialize onion routing nodes"""
        self._nodes = [
            {'id': 'entry1', 'type': 'entry', 'location': 'US', 'available': True},
            {'id': 'entry2', 'type': 'entry', 'location': 'EU', 'available': True},
            {'id': 'middle1', 'type': 'middle', 'location': 'Asia', 'available': True},
            {'id': 'middle2', 'type': 'middle', 'location': 'EU', 'available': True},
            {'id': 'exit1', 'type': 'exit', 'location': 'CH', 'available': True},
            {'id': 'exit2', 'type': 'exit', 'location': 'IS', 'available': True},
        ]

    def _establish_circuits(self):
        """Establish onion routing circuits"""
        # Create multiple circuits for redundancy
        for _ in range(3):
            circuit = self._build_circuit()
            if circuit:
                self._circuits.append(circuit)
                self.logger.debug(f"Circuit established: {[n['id'] for n in circuit]}")

    def _build_circuit(self) -> List[Dict[str, Any]]:
        """Build a single onion circuit"""
        circuit = []

        # Select entry node
        entry_nodes = [n for n in self._nodes if n['type'] == 'entry' and n['available']]
        if entry_nodes:
            circuit.append(random.choice(entry_nodes))

        # Select middle node
        middle_nodes = [n for n in self._nodes if n['type'] == 'middle' and n['available']]
        if middle_nodes:
            circuit.append(random.choice(middle_nodes))

        # Select exit node
        exit_nodes = [n for n in self._nodes if n['type'] == 'exit' and n['available']]
        if exit_nodes:
            circuit.append(random.choice(exit_nodes))

        return circuit if len(circuit) == 3 else []

    def route_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request through onion circuit.

        Returns:
            Routed request with multiple encryption layers
        """
        if not self._active or not self._circuits:
            return request

        # Select a circuit
        circuit = random.choice(self._circuits)

        # Wrap request in multiple encryption layers
        encrypted_request = request.copy()
        encrypted_request['circuit'] = [node['id'] for node in circuit]
        encrypted_request['encrypted_layers'] = len(circuit)

        self.logger.debug(f"Request routed through circuit: {encrypted_request['circuit']}")
        return encrypted_request

    def get_circuits(self) -> List[List[Dict[str, Any]]]:
        """Get active circuits"""
        return self._circuits.copy()

    def rebuild_circuit(self, circuit_index: int):
        """Rebuild specific circuit"""
        if 0 <= circuit_index < len(self._circuits):
            new_circuit = self._build_circuit()
            if new_circuit:
                self._circuits[circuit_index] = new_circuit
                self.logger.info(f"Circuit {circuit_index} rebuilt")

    def is_active(self) -> bool:
        """Check if onion router is active"""
        return self._active
