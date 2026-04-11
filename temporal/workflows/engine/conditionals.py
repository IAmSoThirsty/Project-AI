"""
Conditional Logic Interpreter

Provides conditional execution support for workflows including:
- If/else branching
- Complex conditions
- Loop constructs
- Dynamic workflow paths
"""

import logging
import operator
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ConditionOperator(Enum):
    """Operators for condition evaluation"""
    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    GE = "ge"  # Greater or equal
    LT = "lt"  # Less than
    LE = "le"  # Less or equal
    IN = "in"  # In collection
    NOT_IN = "not_in"  # Not in collection
    CONTAINS = "contains"  # Contains value
    MATCHES = "matches"  # Regex match
    AND = "and"  # Logical AND
    OR = "or"  # Logical OR
    NOT = "not"  # Logical NOT


class LogicOperator(Enum):
    """Operators for combining conditions"""
    AND = "and"
    OR = "or"


@dataclass
class Condition:
    """
    A single condition for evaluation
    
    Supports comparison operations and nested logical conditions.
    """
    operator: ConditionOperator
    left: Union[str, Any]  # Variable name or value
    right: Optional[Union[str, Any]] = None  # Value or variable
    conditions: Optional[List["Condition"]] = None  # For AND/OR/NOT

    def __post_init__(self):
        """Validate condition structure"""
        logical_ops = {ConditionOperator.AND, ConditionOperator.OR, ConditionOperator.NOT}
        
        if self.operator in logical_ops:
            if not self.conditions:
                raise ValueError(
                    f"Logical operator {self.operator} requires nested conditions"
                )
        else:
            if self.right is None and self.operator != ConditionOperator.NOT:
                raise ValueError(
                    f"Operator {self.operator} requires right operand"
                )


@dataclass
class ConditionalBranch:
    """A conditional branch with condition and action"""
    condition: Optional[Condition]  # None for else branch
    action: str  # Node ID or action to execute
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConditionalLogic:
    """
    Defines conditional execution logic
    
    Supports:
    - If/else if/else chains
    - Multiple branches
    - Default fallback
    """
    branches: List[ConditionalBranch]
    default_action: Optional[str] = None  # Fallback if no condition matches


class ConditionalInterpreter:
    """
    Interprets and evaluates conditional logic
    
    Evaluates conditions against context and determines execution path.
    """

    OPERATORS = {
        ConditionOperator.EQ: operator.eq,
        ConditionOperator.NE: operator.ne,
        ConditionOperator.GT: operator.gt,
        ConditionOperator.GE: operator.ge,
        ConditionOperator.LT: operator.lt,
        ConditionOperator.LE: operator.le,
    }

    def __init__(self):
        self.evaluation_log: List[Dict[str, Any]] = []

    def evaluate(
        self,
        logic: ConditionalLogic,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """
        Evaluate conditional logic and return action to execute
        
        Args:
            logic: Conditional logic to evaluate
            context: Variable context for evaluation
            
        Returns:
            Action ID to execute, or None
        """
        logger.info("Evaluating conditional logic")

        for idx, branch in enumerate(logic.branches):
            logger.debug(f"Evaluating branch {idx}")

            # Else branch (no condition)
            if branch.condition is None:
                logger.info(f"Taking else branch: {branch.action}")
                self._log_evaluation(idx, None, True, branch.action)
                return branch.action

            # Evaluate condition
            result = self._evaluate_condition(branch.condition, context)
            self._log_evaluation(idx, branch.condition, result, branch.action)

            if result:
                logger.info(f"Condition met, taking action: {branch.action}")
                return branch.action

        # No condition matched, use default
        if logic.default_action:
            logger.info(f"No condition matched, using default: {logic.default_action}")
            return logic.default_action

        logger.info("No condition matched and no default action")
        return None

    def _evaluate_condition(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a single condition"""
        # Handle logical operators
        if condition.operator == ConditionOperator.AND:
            return all(
                self._evaluate_condition(c, context)
                for c in condition.conditions
            )
        
        if condition.operator == ConditionOperator.OR:
            return any(
                self._evaluate_condition(c, context)
                for c in condition.conditions
            )
        
        if condition.operator == ConditionOperator.NOT:
            return not self._evaluate_condition(condition.conditions[0], context)

        # Resolve operands
        left_value = self._resolve_value(condition.left, context)
        right_value = self._resolve_value(condition.right, context)

        # Handle special operators
        if condition.operator == ConditionOperator.IN:
            return left_value in right_value

        if condition.operator == ConditionOperator.NOT_IN:
            return left_value not in right_value

        if condition.operator == ConditionOperator.CONTAINS:
            return right_value in left_value

        if condition.operator == ConditionOperator.MATCHES:
            import re
            return bool(re.match(str(right_value), str(left_value)))

        # Handle comparison operators
        op_func = self.OPERATORS.get(condition.operator)
        if not op_func:
            raise ValueError(f"Unknown operator: {condition.operator}")

        try:
            return op_func(left_value, right_value)
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}", exc_info=True)
            return False

    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """
        Resolve a value from context or return literal
        
        Supports:
        - Variable references: "$variable_name"
        - Nested paths: "$object.field.subfield"
        - Literal values
        """
        if not isinstance(value, str):
            return value

        if not value.startswith("$"):
            return value

        # Extract variable path
        path = value[1:]  # Remove $
        parts = path.split(".")

        # Navigate context
        result = context
        for part in parts:
            if isinstance(result, dict):
                result = result.get(part)
            elif hasattr(result, part):
                result = getattr(result, part)
            else:
                logger.warning(f"Could not resolve path: {path}")
                return None

        return result

    def _log_evaluation(
        self,
        branch_idx: int,
        condition: Optional[Condition],
        result: bool,
        action: str,
    ) -> None:
        """Log condition evaluation for debugging"""
        self.evaluation_log.append({
            "branch_index": branch_idx,
            "condition": str(condition) if condition else "else",
            "result": result,
            "action": action,
        })


class LoopConstruct:
    """
    Loop construct for iterative execution
    
    Supports:
    - For-each loops
    - While loops
    - Do-while loops
    - Break conditions
    """

    def __init__(
        self,
        loop_type: str,
        condition: Optional[Condition] = None,
        items: Optional[List[Any]] = None,
        max_iterations: int = 1000,
    ):
        """
        Initialize loop construct
        
        Args:
            loop_type: Type of loop ("foreach", "while", "do-while")
            condition: Condition for while loops
            items: Items for foreach loops
            max_iterations: Maximum iterations to prevent infinite loops
        """
        self.loop_type = loop_type
        self.condition = condition
        self.items = items
        self.max_iterations = max_iterations
        self.iteration_count = 0

    async def execute(
        self,
        action: Callable,
        context: Dict[str, Any],
        interpreter: ConditionalInterpreter,
    ) -> List[Any]:
        """
        Execute loop with given action
        
        Args:
            action: Action to execute each iteration
            context: Execution context
            interpreter: Conditional interpreter for evaluation
            
        Returns:
            List of results from each iteration
        """
        results = []
        self.iteration_count = 0

        if self.loop_type == "foreach":
            results = await self._execute_foreach(action, context)
        elif self.loop_type == "while":
            results = await self._execute_while(action, context, interpreter)
        elif self.loop_type == "do-while":
            results = await self._execute_do_while(action, context, interpreter)
        else:
            raise ValueError(f"Unknown loop type: {self.loop_type}")

        logger.info(
            f"Loop completed: {self.iteration_count} iterations, "
            f"{len(results)} results"
        )
        return results

    async def _execute_foreach(
        self,
        action: Callable,
        context: Dict[str, Any],
    ) -> List[Any]:
        """Execute foreach loop"""
        if not self.items:
            return []

        results = []
        for item in self.items:
            if self.iteration_count >= self.max_iterations:
                logger.warning(f"Max iterations reached: {self.max_iterations}")
                break

            # Add current item to context
            loop_context = {**context, "item": item, "index": self.iteration_count}
            
            # Execute action
            result = await action(loop_context)
            results.append(result)
            self.iteration_count += 1

        return results

    async def _execute_while(
        self,
        action: Callable,
        context: Dict[str, Any],
        interpreter: ConditionalInterpreter,
    ) -> List[Any]:
        """Execute while loop"""
        if not self.condition:
            raise ValueError("While loop requires a condition")

        results = []
        while self.iteration_count < self.max_iterations:
            # Evaluate condition
            if not interpreter._evaluate_condition(self.condition, context):
                break

            # Execute action
            loop_context = {**context, "iteration": self.iteration_count}
            result = await action(loop_context)
            results.append(result)
            self.iteration_count += 1

        return results

    async def _execute_do_while(
        self,
        action: Callable,
        context: Dict[str, Any],
        interpreter: ConditionalInterpreter,
    ) -> List[Any]:
        """Execute do-while loop (execute at least once)"""
        if not self.condition:
            raise ValueError("Do-while loop requires a condition")

        results = []
        while self.iteration_count < self.max_iterations:
            # Execute action
            loop_context = {**context, "iteration": self.iteration_count}
            result = await action(loop_context)
            results.append(result)
            self.iteration_count += 1

            # Evaluate condition
            if not interpreter._evaluate_condition(self.condition, context):
                break

        return results
