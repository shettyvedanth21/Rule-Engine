"""
Rule Evaluator Module
Evaluates rule conditions against incoming data
Supports SIMPLE, AND, and OR condition types
"""

import re
import json
import operator
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum


class ConditionType(str, Enum):
    SIMPLE = "SIMPLE"
    AND = "AND"
    OR = "OR"


class ComparisonOperator(str, Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_OR_EQUAL = ">="
    LESS_OR_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


# Map string operators to actual Python operators
OPERATORS: Dict[str, Callable] = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "contains": lambda a, b: b in a if isinstance(a, str) else False,
    "not_contains": lambda a, b: b not in a if isinstance(a, str) else True,
    "in": lambda a, b: a in b if isinstance(b, (list, tuple, set)) else False,
    "not_in": lambda a, b: a not in b if isinstance(b, (list, tuple, set)) else True,
}


class RuleEvaluator:
    """
    Evaluates rules against incoming data.
    Supports simple conditions, AND logic, and OR logic.
    """
    
    # Supported comparison operators
    SUPPORTED_OPERATORS = [op.value for op in ComparisonOperator]
    
    @staticmethod
    def evaluate_condition(condition: str, data: Dict[str, Any]) -> bool:
        """
        Evaluate a simple condition string against data.
        
        Examples:
            - "temperature > 95"
            - "status == 'active'"
            - "value in [1, 2, 3]"
            
        Args:
            condition: Simple condition string (e.g., "temperature > 95")
            data: Dictionary of data to evaluate against
            
        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return False
            
        try:
            # Parse the condition
            # Try to match pattern: field operator value
            pattern = r"(\w+)\s*(==|!=|>=|<=|>|<|contains|not_contains|in|not_in)\s*(.+)"
            match = re.match(pattern, condition.strip())
            
            if not match:
                # Try simpler parsing
                return RuleEvaluator._evaluate_simple(condition, data)
            
            field, op_str, value_str = match.groups()
            
            # Get the field value from data
            field_value = RuleEvaluator._get_nested_value(data, field)
            
            # Parse the comparison value
            compare_value = RuleEvaluator._parse_value(value_str)
            
            # Get the operator function
            op_func = OPERATORS.get(op_str)
            if not op_func:
                return False
            
            # Evaluate
            return op_func(field_value, compare_value)
            
        except Exception as e:
            print(f"Error evaluating condition '{condition}': {e}")
            return False
    
    @staticmethod
    def _get_nested_value(data: Dict[str, Any], field: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = field.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Parse value string to appropriate Python type."""
        value_str = value_str.strip()
        
        # Check for string literals
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]
        
        # Check for list/tuple
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                items = value_str[1:-1].split(',')
                return [RuleEvaluator._parse_value(item.strip()) for item in items]
            except:
                pass
        
        # Check for null/none
        if value_str.lower() in ('null', 'none'):
            return None
        
        # Try numeric
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Check for boolean
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        
        # Return as string
        return value_str
    
    @staticmethod
    def _evaluate_simple(condition: str, data: Dict[str, Any]) -> bool:
        """Fallback simple evaluation."""
        # Check if field exists and is truthy
        field = condition.strip()
        value = RuleEvaluator._get_nested_value(data, field)
        return bool(value)
    
    @staticmethod
    def evaluate_rule(rule: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Evaluate a rule based on its condition type.
        
        Args:
            rule: Rule dictionary with 'condition' and 'condition_type' fields
            data: Data to evaluate against
            
        Returns:
            True if rule is triggered, False otherwise
        """
        condition_type = rule.get('condition_type', 'SIMPLE').upper()
        condition = rule.get('condition', '')
        
        if condition_type == ConditionType.AND:
            return RuleEvaluator._evaluate_and(condition, data)
        elif condition_type == ConditionType.OR:
            return RuleEvaluator._evaluate_or(condition, data)
        else:
            return RuleEvaluator.evaluate_condition(condition, data)
    
    @staticmethod
    def _evaluate_and(conditions: str, data: Dict[str, Any]) -> bool:
        """Evaluate multiple conditions with AND logic."""
        # Conditions can be separated by AND keyword
        condition_list = re.split(r'\s+AND\s+', conditions, flags=re.IGNORECASE)
        
        for cond in condition_list:
            if not RuleEvaluator.evaluate_condition(cond.strip(), data):
                return False
        return True
    
    @staticmethod
    def _evaluate_or(conditions: str, data: Dict[str, Any]) -> bool:
        """Evaluate multiple conditions with OR logic."""
        # Conditions can be separated by OR keyword
        condition_list = re.split(r'\s+OR\s+', conditions, flags=re.IGNORECASE)
        
        for cond in condition_list:
            if RuleEvaluator.evaluate_condition(cond.strip(), data):
                return True
        return False
    
    @staticmethod
    def validate_condition(condition: str, condition_type: str = "SIMPLE") -> Dict[str, Any]:
        """
        Validate a condition string.
        
        Returns:
            Dict with 'valid' boolean and optional 'error' message
        """
        if not condition:
            return {"valid": False, "error": "Condition cannot be empty"}
        
        condition_type = condition_type.upper()
        
        if condition_type == ConditionType.AND:
            # Check that all conditions are valid
            condition_list = re.split(r'\s+AND\s+', condition, flags=re.IGNORECASE)
            for cond in condition_list:
                if not RuleEvaluator._is_valid_simple_condition(cond.strip()):
                    return {"valid": False, "error": f"Invalid condition: {cond}"}
        
        elif condition_type == ConditionType.OR:
            # Check that all conditions are valid
            condition_list = re.split(r'\s+OR\s+', condition, flags=re.IGNORECASE)
            for cond in condition_list:
                if not RuleEvaluator._is_valid_simple_condition(cond.strip()):
                    return {"valid": False, "error": f"Invalid condition: {cond}"}
        
        else:
            if not RuleEvaluator._is_valid_simple_condition(condition):
                return {"valid": False, "error": f"Invalid condition: {condition}"}
        
        return {"valid": True}
    
    @staticmethod
    def _is_valid_simple_condition(condition: str) -> bool:
        """Check if a simple condition is valid."""
        pattern = r"^\w+(\.\w+)*\s*(==|!=|>=|<=|>|<|contains|not_contains|in|not_in)\s*.+$"
        return bool(re.match(pattern, condition.strip()))


class DataValidator:
    """Validates incoming data against expected schema."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        Validate that required fields are present in data.
        
        Returns:
            Dict with 'valid' boolean and list of missing fields
        """
        missing = []
        for field in required_fields:
            value = RuleEvaluator._get_nested_value(data, field)
            if value is None:
                missing.append(field)
        
        if missing:
            return {"valid": False, "missing_fields": missing}
        return {"valid": True}


# Singleton instance
rule_evaluator = RuleEvaluator()
