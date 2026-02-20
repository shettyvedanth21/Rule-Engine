import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List
import json

from app.database import execute_query, execute_query_single
from app.models import RULE_TRIGGERS_QUERIES
from app.schemas import RuleTriggerCreate, RuleTriggerUpdate, RuleTriggerResponse

router = APIRouter(prefix="/rule-triggers", tags=["rule-triggers"])


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


@router.get("", response_model=List[RuleTriggerResponse])
async def get_all_rule_triggers():
    """Get all rule triggers."""
    try:
        results = execute_query(RULE_TRIGGERS_QUERIES['get_all'])
        for trigger in results:
            if 'trigger_config' in trigger and trigger['trigger_config']:
                trigger['trigger_config'] = deserialize_config(trigger['trigger_config'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule triggers: {str(e)}"
        )


@router.get("/{trigger_id}", response_model=RuleTriggerResponse)
async def get_rule_trigger_by_id(trigger_id: str):
    """Get a rule trigger by ID."""
    try:
        result = execute_query_single(RULE_TRIGGERS_QUERIES['get_by_id'], (trigger_id,))
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule trigger with id {trigger_id} not found"
            )
        if 'trigger_config' in result and result['trigger_config']:
            result['trigger_config'] = deserialize_config(result['trigger_config'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule trigger: {str(e)}"
        )


@router.post("", response_model=RuleTriggerResponse, status_code=status.HTTP_201_CREATED)
async def create_rule_trigger(trigger: RuleTriggerCreate):
    """Create a new rule trigger."""
    try:
        trigger_id = str(uuid.uuid4())
        
        params = (
            trigger_id,
            trigger.rule_id,
            trigger.trigger_type,
            serialize_config(trigger.trigger_config),
            trigger.is_active
        )
        
        execute_query(RULE_TRIGGERS_QUERIES['create'], params, fetch=False)
        
        # Fetch the created trigger
        result = execute_query_single(RULE_TRIGGERS_QUERIES['get_by_id'], (trigger_id,))
        if result and 'trigger_config' in result and result['trigger_config']:
            result['trigger_config'] = deserialize_config(result['trigger_config'])
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rule trigger: {str(e)}"
        )


@router.put("/{trigger_id}", response_model=RuleTriggerResponse)
async def update_rule_trigger(trigger_id: str, trigger: RuleTriggerUpdate):
    """Update a rule trigger."""
    try:
        # Check if trigger exists
        existing = execute_query_single(RULE_TRIGGERS_QUERIES['get_by_id'], (trigger_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule trigger with id {trigger_id} not found"
            )
        
        # Build update query dynamically
        updates = []
        params = []
        
        if trigger.trigger_type is not None:
            updates.append("trigger_type = %s")
            params.append(trigger.trigger_type)
        if trigger.trigger_config is not None:
            updates.append("trigger_config = %s")
            params.append(serialize_config(trigger.trigger_config))
        if trigger.is_active is not None:
            updates.append("is_active = %s")
            params.append(trigger.is_active)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        params.append(trigger_id)
        
        query = f"UPDATE rule_triggers SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params), fetch=False)
        
        # Fetch updated trigger
        result = execute_query_single(RULE_TRIGGERS_QUERIES['get_by_id'], (trigger_id,))
        if result and 'trigger_config' in result and result['trigger_config']:
            result['trigger_config'] = deserialize_config(result['trigger_config'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rule trigger: {str(e)}"
        )


@router.delete("/{trigger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule_trigger(trigger_id: str):
    """Delete a rule trigger."""
    try:
        # Check if trigger exists
        existing = execute_query_single(RULE_TRIGGERS_QUERIES['get_by_id'], (trigger_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule trigger with id {trigger_id} not found"
            )
        
        execute_query(RULE_TRIGGERS_QUERIES['delete'], (trigger_id,), fetch=False)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rule trigger: {str(e)}"
        )
