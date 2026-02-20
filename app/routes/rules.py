import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List
import json

from app.database import execute_query, execute_query_single
from app.models import RULES_QUERIES
from app.schemas import RuleCreate, RuleUpdate, RuleResponse

router = APIRouter(prefix="/rules", tags=["rules"])


def serialize_condition(data):
    """Serialize dict to JSON string for database."""
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return json.dumps(data)


def deserialize_condition(data_str):
    """Deserialize JSON string from database to dict."""
    if data_str is None:
        return None
    if isinstance(data_str, dict):
        return data_str
    try:
        return json.loads(data_str)
    except:
        return data_str


@router.get("", response_model=List[RuleResponse])
async def get_all_rules():
    """Get all rules."""
    try:
        results = execute_query(RULES_QUERIES['get_all'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rules: {str(e)}"
        )


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule_by_id(rule_id: str):
    """Get a rule by ID."""
    try:
        result = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with id {rule_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule: {str(e)}"
        )


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: RuleCreate):
    """Create a new rule."""
    try:
        rule_id = str(uuid.uuid4())
        
        params = (
            rule_id,
            rule.name,
            rule.description,
            serialize_condition(rule.condition),
            rule.is_active,
            rule.priority
        )
        
        execute_query(RULES_QUERIES['create'], params, fetch=False)
        
        # Fetch the created rule
        result = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rule: {str(e)}"
        )


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: str, rule: RuleUpdate):
    """Update a rule."""
    try:
        # Check if rule exists
        existing = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with id {rule_id} not found"
            )
        
        # Build update query dynamically
        updates = []
        params = []
        
        if rule.name is not None:
            updates.append("name = %s")
            params.append(rule.name)
        if rule.description is not None:
            updates.append("description = %s")
            params.append(rule.description)
        if rule.condition is not None:
            updates.append("`condition` = %s")
            params.append(serialize_condition(rule.condition))
        if rule.is_active is not None:
            updates.append("is_active = %s")
            params.append(rule.is_active)
        if rule.priority is not None:
            updates.append("priority = %s")
            params.append(rule.priority)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        params.append(rule_id)
        
        query = f"UPDATE rules SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params), fetch=False)
        
        # Fetch updated rule
        result = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rule: {str(e)}"
        )


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: str):
    """Delete a rule."""
    try:
        # Check if rule exists
        existing = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with id {rule_id} not found"
            )
        
        execute_query(RULES_QUERIES['delete'], (rule_id,), fetch=False)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rule: {str(e)}"
        )
