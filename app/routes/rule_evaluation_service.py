"""
Rule Evaluation and Trigger Service
Main entry point for evaluating rules against incoming data
"""

import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.database import execute_query, execute_query_single
from app.models import (
    RULES_QUERIES, 
    RULE_EVENTS_QUERIES,
    NOTIFICATION_SETTINGS_QUERIES
)
from app.services.rule_evaluator import RuleEvaluator
from app.services.notification_dispatcher import NotificationDispatcher

router = APIRouter(prefix="/rules", tags=["rule-evaluation"])


# Supported notification channels
SUPPORTED_CHANNELS = ["EMAIL", "SMS", "WHATSAPP", "TELEGRAM", "WEBHOOK", "INAPP"]


@router.post("/evaluate")
async def evaluate_rules(data: Dict[str, Any], event_id: Optional[str] = None):
    """
    Evaluate incoming data against all active rules and trigger notifications.
    
    This is the main endpoint for the rule engine.
    It evaluates all active rules against the incoming data and triggers
    notifications for rules that match.
    
    Request body:
    {
        "temperature": 96,
        "humidity": 80,
        "status": "active",
        // ... any other data fields
    }
    
    Query params:
    - event_id: Optional unique identifier for this event (generated if not provided)
    """
    try:
        if event_id is None:
            event_id = str(uuid.uuid4())
        
        # Get all active rules
        rules = execute_query(RULES_QUERIES['get_active'])
        
        if not rules:
            return {
                "success": True,
                "message": "No active rules found",
                "event_id": event_id,
                "matched_rules": []
            }
        
        matched_rules = []
        results = []
        
        for rule in rules:
            # Check debounce
            debounce_seconds = rule.get('debounce_seconds', 60)
            if NotificationDispatcher.check_debounce(rule['id'], debounce_seconds):
                results.append({
                    "rule_id": rule['id'],
                    "rule_name": rule['name'],
                    "matched": False,
                    "reason": "debounced"
                })
                continue
            
            # Evaluate the rule
            is_match = RuleEvaluator.evaluate_rule(rule, data)
            
            if is_match:
                matched_rules.append(rule)
                
                # Get notification settings for this rule
                settings = execute_query_single(
                    NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'],
                    (rule['id'],)
                )
                
                if settings:
                    # Determine which channels to notify
                    channels = _get_channels_from_settings(settings)
                    
                    if channels:
                        # Dispatch notifications
                        dispatcher = NotificationDispatcher()
                        dispatch_result = dispatcher.dispatch(
                            rule=rule,
                            data=data,
                            event_id=event_id,
                            channels=channels
                        )
                        
                        results.append({
                            "rule_id": rule['id'],
                            "rule_name": rule['name'],
                            "matched": True,
                            "state": "TRIGGERED",
                            "channels": channels,
                            "notification_result": dispatch_result
                        })
                    else:
                        results.append({
                            "rule_id": rule['id'],
                            "rule_name": rule['name'],
                            "matched": True,
                            "state": "TRIGGERED",
                            "channels": [],
                            "notification_result": "No channels configured"
                        })
                else:
                    results.append({
                        "rule_id": rule['id'],
                        "rule_name": rule['name'],
                        "matched": True,
                        "state": "TRIGGERED",
                        "notification_result": "No notification settings"
                    })
            else:
                results.append({
                    "rule_id": rule['id'],
                    "rule_name": rule['name'],
                    "matched": False,
                    "reason": "condition_not_met"
                })
        
        return {
            "success": True,
            "event_id": event_id,
            "data": data,
            "total_rules": len(rules),
            "matched_count": len(matched_rules),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating rules: {str(e)}"
        )


@router.post("/evaluate/{rule_id}")
async def evaluate_single_rule(rule_id: str, data: Dict[str, Any], event_id: Optional[str] = None):
    """
    Evaluate data against a specific rule.
    
    Path params:
    - rule_id: ID of the rule to evaluate
    
    Request body:
    {
        "temperature": 96,
        // ... data fields
    }
    """
    try:
        if event_id is None:
            event_id = str(uuid.uuid4())
        
        # Get the rule
        rule = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with id {rule_id} not found"
            )
        
        if not rule.get('is_active'):
            return {
                "success": True,
                "rule_id": rule_id,
                "rule_name": rule['name'],
                "matched": False,
                "reason": "rule_inactive"
            }
        
        # Check debounce
        debounce_seconds = rule.get('debounce_seconds', 60)
        if NotificationDispatcher.check_debounce(rule_id, debounce_seconds):
            return {
                "success": True,
                "rule_id": rule_id,
                "rule_name": rule['name'],
                "matched": False,
                "reason": "debounced"
            }
        
        # Evaluate the rule
        is_match = RuleEvaluator.evaluate_rule(rule, data)
        
        if is_match:
            # Get notification settings
            settings = execute_query_single(
                NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'],
                (rule_id,)
            )
            
            channels = _get_channels_from_settings(settings) if settings else []
            
            if channels:
                # Dispatch notifications
                dispatcher = NotificationDispatcher()
                dispatch_result = dispatcher.dispatch(
                    rule=rule,
                    data=data,
                    event_id=event_id,
                    channels=channels
                )
                
                return {
                    "success": True,
                    "rule_id": rule_id,
                    "rule_name": rule['name'],
                    "matched": True,
                    "state": "TRIGGERED",
                    "event_id": event_id,
                    "channels": channels,
                    "notification_result": dispatch_result
                }
            else:
                return {
                    "success": True,
                    "rule_id": rule_id,
                    "rule_name": rule['name'],
                    "matched": True,
                    "state": "TRIGGERED",
                    "event_id": event_id,
                    "notification_result": "No channels configured"
                }
        
        return {
            "success": True,
            "rule_id": rule_id,
            "rule_name": rule['name'],
            "matched": False,
            "reason": "condition_not_met"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating rule: {str(e)}"
        )


@router.post("/trigger-now")
async def trigger_rule_now(
    rule_id: str, 
    data: Dict[str, Any], 
    channels: List[str] = None,
    event_id: Optional[str] = None
):
    """
    Trigger a rule immediately without evaluating conditions.
    
    This is useful for testing or manual triggering.
    
    Path params:
    - rule_id: ID of the rule to trigger
    
    Query params:
    - channels: Optional list of channels to notify (if not specified, uses rule settings)
    """
    try:
        if event_id is None:
            event_id = str(uuid.uuid4())
        
        # Get the rule
        rule = execute_query_single(RULES_QUERIES['get_by_id'], (rule_id,))
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule with id {rule_id} not found"
            )
        
        # Determine channels
        if channels:
            # Validate channels
            invalid_channels = [c for c in channels if c.upper() not in SUPPORTED_CHANNELS]
            if invalid_channels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid channels: {invalid_channels}. Supported: {SUPPORTED_CHANNELS}"
                )
            channels = [c.upper() for c in channels]
        else:
            # Get from settings
            settings = execute_query_single(
                NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'],
                (rule_id,)
            )
            channels = _get_channels_from_settings(settings) if settings else []
        
        if not channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No notification channels configured for this rule"
            )
        
        # Dispatch notifications
        dispatcher = NotificationDispatcher()
        result = dispatcher.dispatch(
            rule=rule,
            data=data,
            event_id=event_id,
            channels=channels
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering rule: {str(e)}"
        )


def _get_channels_from_settings(settings: Dict[str, Any]) -> List[str]:
    """Extract enabled channels from notification settings."""
    channels = []
    
    if settings.get('recipient_email'):
        channels.append('EMAIL')
    if settings.get('recipient_phone'):
        channels.append('SMS')
    if settings.get('whatsapp_number'):
        channels.append('WHATSAPP')
    if settings.get('telegram_chat_id'):
        channels.append('TELEGRAM')
    if settings.get('webhook_url'):
        channels.append('WEBHOOK')
    
    # In-app is always available if rule has settings
    if settings:
        channels.append('INAPP')
    
    return channels
