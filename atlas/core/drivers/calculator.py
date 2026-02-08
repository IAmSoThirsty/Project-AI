"""
Drivers Module for PROJECT ATLAS

Loads driver formulas from configuration, executes formula-based calculations
for influence scores, implements all influence drivers with deterministic evaluation.

Production-grade with full error handling, logging, and audit trail integration.
"""

import ast
import logging
import math
import operator
from datetime import datetime
from typing import Any

from atlas.audit.trail import AuditCategory, AuditLevel, AuditTrail, get_audit_trail
from atlas.config.loader import ConfigLoader, get_config_loader
from atlas.schemas.validator import SchemaValidator, get_schema_validator

logger = logging.getLogger(__name__)


class DriverError(Exception):
    """Raised when driver calculation fails."""
    pass


class FormulaError(Exception):
    """Raised when formula evaluation fails."""
    pass


class DriverCalculator:
    """
    Production-grade driver calculator for PROJECT ATLAS.
    
    Loads formulas from drivers.yaml, executes calculations for influence scores,
    implements all influence drivers with deterministic evaluation.
    """

    # Safe operators for formula evaluation
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Safe functions for formula evaluation
    SAFE_FUNCTIONS = {
        "sum": sum,
        "min": min,
        "max": max,
        "abs": abs,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "sin": math.sin,
        "cos": math.cos,
        "pow": pow,
    }

    def __init__(self,
                 config_loader: ConfigLoader | None = None,
                 schema_validator: SchemaValidator | None = None,
                 audit_trail: AuditTrail | None = None):
        """
        Initialize driver calculator.
        
        Args:
            config_loader: Configuration loader (uses global if None)
            schema_validator: Schema validator (uses global if None)
            audit_trail: Audit trail (uses global if None)
        """
        self.config = config_loader or get_config_loader()
        self.validator = schema_validator or get_schema_validator()
        self.audit = audit_trail or get_audit_trail()

        # Load driver configurations
        self.drivers_config = self.config.get("drivers")
        self.influence_drivers = self.drivers_config.get("influence_drivers", {})
        self.projection_drivers = self.drivers_config.get("projection_drivers", {})
        self.relationship_drivers = self.drivers_config.get("relationship_drivers", {})
        self.scenario_drivers = self.drivers_config.get("scenario_drivers", {})
        self.temporal_drivers = self.drivers_config.get("temporal_drivers", {})

        # Validate driver configuration
        self._validate_driver_config()

        # Track calculation statistics
        self._stats = {
            "calculations_performed": 0,
            "formulas_evaluated": 0,
            "errors_encountered": 0
        }

        logger.info("DriverCalculator initialized successfully")

        self.audit.log_event(
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFORMATIONAL,
            operation="driver_calculator_initialized",
            actor="DRIVERS_MODULE",
            details={
                "drivers_loaded": len(self.influence_drivers),
                "config_hash": self.config.get_hash("drivers")
            }
        )

    def calculate_influence_score(self, entity_data: dict[str, Any]) -> dict[str, Any]:
        """
        Calculate composite influence score for an entity.
        
        Args:
            entity_data: Entity data with driver inputs
            
        Returns:
            Dictionary with driver scores and composite influence
            
        Raises:
            DriverError: If calculation fails
        """
        try:
            self._stats["calculations_performed"] += 1

            entity_id = entity_data.get("id", "unknown")

            # Log calculation start
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="calculate_influence_start",
                actor="DRIVERS_MODULE",
                details={"entity_id": entity_id}
            )

            driver_scores = {}
            total_weight = 0.0
            weighted_sum = 0.0

            # Calculate each influence driver
            for driver_name, driver_config in self.influence_drivers.items():
                try:
                    score = self._calculate_driver(
                        driver_name,
                        driver_config,
                        entity_data
                    )

                    weight = driver_config.get("weight", 0.0)
                    driver_scores[driver_name] = {
                        "value": score,
                        "weight": weight,
                        "weighted_value": score * weight
                    }

                    total_weight += weight
                    weighted_sum += score * weight

                except Exception as e:
                    logger.error("Failed to calculate driver %s: %s", driver_name, e)
                    driver_scores[driver_name] = {
                        "value": 0.0,
                        "weight": driver_config.get("weight", 0.0),
                        "weighted_value": 0.0,
                        "error": str(e)
                    }

            # Validate weights sum to 1.0
            if not (0.99 <= total_weight <= 1.01):
                logger.warning("Driver weights sum to %s, expected 1.0", total_weight)

            # Calculate composite influence
            composite_influence = weighted_sum / total_weight if total_weight > 0 else 0.0

            # Apply constraints
            composite_influence = max(0.0, min(1.0, composite_influence))

            result = {
                "entity_id": entity_id,
                "composite_influence": composite_influence,
                "driver_scores": driver_scores,
                "calculation_metadata": {
                    "calculated_at": datetime.utcnow().isoformat(),
                    "calculator_version": "1.0.0",
                    "total_weight": total_weight,
                    "config_hash": self.config.get_hash("drivers")
                }
            }

            # Log success
            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.STANDARD,
                operation="calculate_influence_success",
                actor="DRIVERS_MODULE",
                details={
                    "entity_id": entity_id,
                    "composite_influence": composite_influence
                }
            )

            return result

        except Exception as e:
            self._stats["errors_encountered"] += 1
            logger.error("Failed to calculate influence score: %s", e)

            self.audit.log_event(
                category=AuditCategory.OPERATION,
                level=AuditLevel.HIGH_PRIORITY,
                operation="calculate_influence_failed",
                actor="DRIVERS_MODULE",
                details={"error": str(e), "entity_id": entity_data.get("id", "unknown")}
            )

            raise DriverError(f"Failed to calculate influence score: {e}") from e

    def calculate_projection_drivers(self,
                                     current_state: dict[str, Any],
                                     history: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Calculate projection drivers for timeline evolution.
        
        Args:
            current_state: Current entity state
            history: Historical state data
            
        Returns:
            Dictionary with projection driver values
        """
        try:
            projection_values = {}

            for driver_name, driver_config in self.projection_drivers.items():
                try:
                    value = self._calculate_projection_driver(
                        driver_name,
                        driver_config,
                        current_state,
                        history
                    )

                    # Apply constraints
                    constraints = driver_config.get("constraints", {})
                    min_val = constraints.get("min", float("-inf"))
                    max_val = constraints.get("max", float("inf"))
                    value = max(min_val, min(max_val, value))

                    projection_values[driver_name] = value

                except Exception as e:
                    logger.error("Failed to calculate projection driver %s: %s", driver_name, e)
                    projection_values[driver_name] = 0.0

            return {
                "projection_drivers": projection_values,
                "calculated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Failed to calculate projection drivers: %s", e)
            raise DriverError(f"Failed to calculate projection drivers: {e}") from e

    def calculate_relationship_strength(self,
                                        entity1: dict[str, Any],
                                        entity2: dict[str, Any],
                                        relationship_type: str) -> float:
        """
        Calculate relationship strength between two entities.
        
        Args:
            entity1: First entity data
            entity2: Second entity data
            relationship_type: Type of relationship (cooperation, competition, conflict)
            
        Returns:
            Relationship strength value
        """
        try:
            if relationship_type not in self.relationship_drivers:
                logger.warning("Unknown relationship type: %s", relationship_type)
                return 0.5

            driver_config = self.relationship_drivers[relationship_type]

            # Build context for formula evaluation
            context = {
                "entity1": entity1,
                "entity2": entity2,
                "shared_interests": self._calculate_shared_interests(entity1, entity2),
                "mutual_benefit": self._calculate_mutual_benefit(entity1, entity2),
                "trust": entity1.get("trust_scores", {}).get(entity2.get("id"), 0.5),
                "conflicting_interests": self._calculate_conflicting_interests(entity1, entity2),
                "resource_overlap": self._calculate_resource_overlap(entity1, entity2),
                "competition": 0.5,  # Placeholder
                "tension": entity1.get("tensions", {}).get(entity2.get("id"), 0.0),
                "cooperation": 0.5  # Placeholder
            }

            # Evaluate formula
            formula = driver_config.get("formula", "0.5")
            strength = self._evaluate_formula(formula, context)

            # Normalize to [0, 1]
            strength = max(0.0, min(1.0, strength))

            return strength

        except Exception as e:
            logger.error("Failed to calculate relationship strength: %s", e)
            return 0.5

    def _calculate_driver(self,
                          driver_name: str,
                          driver_config: dict[str, Any],
                          entity_data: dict[str, Any]) -> float:
        """
        Calculate a single influence driver.
        
        Args:
            driver_name: Name of driver
            driver_config: Driver configuration
            entity_data: Entity data
            
        Returns:
            Driver score between 0.0 and 1.0
        """
        formula = driver_config.get("formula", "0.0")
        inputs = driver_config.get("inputs", [])
        normalization = driver_config.get("normalization", "min_max")

        # Extract input values from entity data
        context = {}
        for input_name in inputs:
            # Try to get value from entity attributes
            value = entity_data.get("attributes", {}).get(input_name, 0.0)

            # Try alternate locations
            if value == 0.0:
                value = entity_data.get(input_name, 0.0)

            # Convert to float
            try:
                context[input_name] = float(value)
            except (ValueError, TypeError):
                logger.warning("Could not convert %s to float: %s", input_name, value)
                context[input_name] = 0.0

        # Evaluate formula
        try:
            score = self._evaluate_formula(formula, context)
            self._stats["formulas_evaluated"] += 1
        except Exception as e:
            logger.error("Formula evaluation failed for %s: %s", driver_name, e)
            raise FormulaError(f"Formula evaluation failed: {e}") from e

        # Apply normalization
        if normalization == "min_max":
            constraints = driver_config.get("constraints", {})
            min_val = constraints.get("min", 0.0)
            max_val = constraints.get("max", 1.0)
            score = max(min_val, min(max_val, score))

        return score

    def _calculate_projection_driver(self,
                                     driver_name: str,
                                     driver_config: dict[str, Any],
                                     current_state: dict[str, Any],
                                     history: list[dict[str, Any]]) -> float:
        """Calculate a projection driver value."""
        formula = driver_config.get("formula", "0.0")

        # Build context with current and historical data
        context = {
            "current_influence": current_state.get("influence", 0.5),
            "previous_influence": history[-1].get("influence", 0.5) if history else 0.5,
            "velocity_factor": driver_config.get("velocity_factor", 0.1),
            "decay_rate": driver_config.get("decay_rate", 0.05),
            "time_elapsed": 1.0,  # Time units
        }

        # Add history-based calculations
        if history:
            influences = [h.get("influence", 0.5) for h in history]
            context["stddev"] = self._calculate_stddev(influences) if len(influences) > 1 else 0.0
            context["volatility_multiplier"] = driver_config.get("volatility_multiplier", 1.5)

        # Evaluate formula
        value = self._evaluate_formula(formula, context)

        return value

    def _evaluate_formula(self, formula: str, context: dict[str, Any]) -> float:
        """
        Safely evaluate a mathematical formula.
        
        Args:
            formula: Formula string
            context: Variable values
            
        Returns:
            Evaluated result
            
        Raises:
            FormulaError: If evaluation fails
        """
        try:
            # Replace parentheses in formula for parsing
            formula = formula.strip()

            # Add safe functions to context
            eval_context = dict(context)
            eval_context["sum"] = sum
            eval_context["min"] = min
            eval_context["max"] = max
            eval_context["abs"] = abs
            eval_context["sqrt"] = math.sqrt
            eval_context["stddev"] = self._calculate_stddev

            # Parse the formula into AST
            try:
                tree = ast.parse(formula, mode='eval')
            except SyntaxError as e:
                raise FormulaError(f"Invalid formula syntax: {e}")

            # Evaluate safely
            result = self._eval_node(tree.body, eval_context)

            # Ensure numeric result
            if not isinstance(result, (int, float)):
                raise FormulaError(f"Formula result is not numeric: {result}")

            return float(result)

        except Exception as e:
            logger.error("Formula evaluation failed: %s, error: %s", formula, e)
            raise FormulaError(f"Formula evaluation failed: {e}") from e

    def _eval_node(self, node: ast.AST, context: dict[str, Any]) -> Any:
        """
        Recursively evaluate an AST node.
        
        Args:
            node: AST node
            context: Variable values
            
        Returns:
            Evaluation result
        """
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Num):  # Python < 3.8
            return node.n

        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            elif node.id in self.SAFE_FUNCTIONS:
                return self.SAFE_FUNCTIONS[node.id]
            else:
                raise FormulaError(f"Undefined variable: {node.id}")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)
            op_type = type(node.op)

            if op_type not in self.SAFE_OPERATORS:
                raise FormulaError(f"Unsupported operator: {op_type}")

            op_func = self.SAFE_OPERATORS[op_type]

            # Handle division by zero
            if op_type == ast.Div and right == 0:
                logger.warning("Division by zero in formula, returning 0")
                return 0.0

            return op_func(left, right)

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            op_type = type(node.op)

            if op_type not in self.SAFE_OPERATORS:
                raise FormulaError(f"Unsupported unary operator: {op_type}")

            return self.SAFE_OPERATORS[op_type](operand)

        elif isinstance(node, ast.Call):
            func = self._eval_node(node.func, context)
            args = [self._eval_node(arg, context) for arg in node.args]

            if func not in self.SAFE_FUNCTIONS.values():
                raise FormulaError("Unsafe function call")

            return func(*args)

        elif isinstance(node, ast.List):
            return [self._eval_node(elem, context) for elem in node.elts]

        else:
            raise FormulaError(f"Unsupported node type: {type(node)}")

    def _calculate_stddev(self, values: list[float]) -> float:
        """Calculate standard deviation of values."""
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _calculate_shared_interests(self, entity1: dict[str, Any], entity2: dict[str, Any]) -> float:
        """Calculate shared interests between entities."""
        topics1 = set(entity1.get("topics", []))
        topics2 = set(entity2.get("topics", []))

        if not topics1 or not topics2:
            return 0.0

        intersection = len(topics1 & topics2)
        union = len(topics1 | topics2)

        return intersection / union if union > 0 else 0.0

    def _calculate_mutual_benefit(self, entity1: dict[str, Any], entity2: dict[str, Any]) -> float:
        """Calculate mutual benefit score."""
        # Simplified calculation based on influence alignment
        influence1 = entity1.get("influence", 0.5)
        influence2 = entity2.get("influence", 0.5)

        # Both high influence = high mutual benefit
        return (influence1 + influence2) / 2.0

    def _calculate_conflicting_interests(self, entity1: dict[str, Any], entity2: dict[str, Any]) -> float:
        """Calculate conflicting interests between entities."""
        # Inverse of shared interests
        return 1.0 - self._calculate_shared_interests(entity1, entity2)

    def _calculate_resource_overlap(self, entity1: dict[str, Any], entity2: dict[str, Any]) -> float:
        """Calculate resource overlap between entities."""
        # Simplified: based on jurisdiction overlap
        juris1 = entity1.get("jurisdiction", "")
        juris2 = entity2.get("jurisdiction", "")

        return 1.0 if juris1 == juris2 else 0.3

    def _validate_driver_config(self) -> None:
        """Validate driver configuration integrity."""
        # Validate influence drivers weights sum to 1.0
        total_weight = sum(
            driver.get("weight", 0.0)
            for driver in self.influence_drivers.values()
        )

        if not (0.99 <= total_weight <= 1.01):
            logger.warning("Influence driver weights sum to %s, expected 1.0", total_weight)

        # Validate all drivers have required fields
        for driver_name, driver_config in self.influence_drivers.items():
            if "formula" not in driver_config:
                raise DriverError(f"Driver {driver_name} missing formula")
            if "weight" not in driver_config:
                raise DriverError(f"Driver {driver_name} missing weight")

    def get_statistics(self) -> dict[str, Any]:
        """Get calculation statistics."""
        return dict(self._stats)

    def reset_statistics(self) -> None:
        """Reset statistics counters."""
        self._stats = {
            "calculations_performed": 0,
            "formulas_evaluated": 0,
            "errors_encountered": 0
        }


if __name__ == "__main__":
    # Test driver calculator
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        calculator = DriverCalculator()

        # Test entity data
        entity_data = {
            "id": "TEST-ORG-001",
            "name": "Test Organization",
            "attributes": {
                "gdp": 0.8,
                "market_cap": 0.7,
                "trade_volume": 0.6,
                "currency_strength": 0.75,
                "budget": 0.7,
                "personnel": 0.6,
                "technology": 0.8,
                "readiness": 0.75,
                "diplomatic_relations": 0.7,
                "treaty_power": 0.6,
                "soft_power": 0.65,
                "rd_spending": 0.8,
                "patent_count": 0.7,
                "innovation_index": 0.75,
                "media_reach": 0.6,
                "narrative_strength": 0.7,
                "censorship_power": 0.4,
                "internal_stability": 0.8,
                "public_trust": 0.7,
                "unity_index": 0.75
            }
        }

        # Calculate influence score
        result = calculator.calculate_influence_score(entity_data)

        print("Influence Calculation Result:")
        print(f"Composite Influence: {result['composite_influence']:.4f}")
        print("\nDriver Scores:")
        for driver_name, scores in result['driver_scores'].items():
            print(f"  {driver_name}: {scores['value']:.4f} (weighted: {scores['weighted_value']:.4f})")

        # Test projection drivers
        current_state = {"influence": 0.7}
        history = [{"influence": 0.65}, {"influence": 0.68}]

        projection = calculator.calculate_projection_drivers(current_state, history)
        print("\nProjection Drivers:")
        for driver_name, value in projection['projection_drivers'].items():
            print(f"  {driver_name}: {value:.4f}")

        # Print statistics
        print("\nStatistics:")
        import json
        print(json.dumps(calculator.get_statistics(), indent=2))

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise
