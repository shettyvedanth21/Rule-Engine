import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List
import json

from app.database import execute_query, execute_query_single
from app.models import RULE_ACTIONS_QUERIES
from app.schemas import RuleActionCreate, RuleActionUpdate, RuleActionResponse

router = APIRouter(prefix="/rule-actions", tags=["rule-actions"])


def serialize_config(config):
    """Serialize config dict to JSON string for database."""
    if config is None:
        return None
    if isinstance(config, str):
        return config
    return json.dumps(config)


def deserialize_config(config_str):
    """Deserialize JSON string from database to dict."""
    if config_str is None:
        return None
    if isinstance(config_str, dict):
        return config_str
    try:
        return json.loads(config_str)
    except:
        return config_str


@router.get("", response_model=List[RuleActionResponse])
async def get_all_rule_actions():
    """Get all rule actions."""
    try:
        results = execute_query(RULE_ACTIONS_QUERIES['get_all'])
        for action in results:
            if 'action_config' in action and action['action_config']:
                action['action_config'] = deserialize_config(action['action_config'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule actions: {str(e)}"
        )


@router.get("/{action_id}", response_model=RuleActionResponse)
async def get_rule_action_by_id(action_id: str):
    """Get a rule action by ID."""
    try:
        result = execute_query_single(RULE_ACTIONS_QUERIES['get_by_id'], (action_id,))
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule action with id {action_id} not found"
            )
        if 'action_config' in result and result['action_config']:
            result['action_config'] = deserialize_config(result['action_config'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule action: {str(e)}"
        )


@router.post("", response_model=RuleActionResponse, status_code=status.HTTP_201_CREATED)
async def create_rule_action(action: RuleActionCreate):
    """Create a new rule action."""
    try:
        action_id = str(uuid.uuid4())
        
        params = (
            action_id,
            action.rule_id,
            action.action_type,
            serialize_config(action.action_config)
        )
        
        execute_query(RULE_ACTIONS_QUERIES['create'], params, fetch=False)
        
        # Fetch the created action
        result = execute_query_single(RULE_ACTIONS_QUERIES['get_by_id'], (action_id,))
        if result and 'action_config' in result and result['action_config']:
            result['action_config'] = deserialize_config(result['action_config'])
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rule action: {str(e)}"
        )


@router.put("/{action_id}", response_model=RuleActionResponse)
async def update_rule_action(action_id: str, action: RuleActionUpdate):
    """Update a rule action."""
    try:
        # Check if action exists
        existing = execute_query_single(RULE_ACTIONS_QUERIES['get_by_id'], (action_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule action with id {action_id} not found"
            )
        
        # Build update query dynamically
        updates = []
        params = []
        
        if action.action_type is not None:
            updates.append("action_type = %s")
            params.append(action.action_type)
        if action.action_config is not None:
            updates.append("action_config = %s")
            params.append(serialize_config(action.action_config))
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        params.append(action_id)
        
        query = f"UPDATE rule_actions SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params), fetch=False)
        
        # Fetch updated action
        result = execute_query_single(RULE_ACTIONS_QUERIES['get_by_id'], (action_id,))
        if result and 'action_config' in result and result['action_config']:
            result['action_config'] = deserialize_config(result['action_config'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rule action: {str(e)}"
        )


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule_action(action_id: str):
    """Delete a rule action."""
    try:
        # Check if action exists
        existing = execute_query_single(RULE_ACTIONS_QUERIES['get_by_id'], (action_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule action with id {action_id} not found"
            )
        
        execute_query(RULE_ACTIONS_QUERIES['delete'], (action_id,), fetch=False)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rule action: {str(e)}"
        )
