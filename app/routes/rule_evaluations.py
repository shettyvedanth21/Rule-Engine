import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List
import json

from app.database import execute_query, execute_query_single
from app.models import RULE_EVALUATIONS_QUERIES
from app.schemas import RuleEvaluationCreate, RuleEvaluationUpdate, RuleEvaluationResponse

router = APIRouter(prefix="/rule-evaluations", tags=["rule-evaluations"])


def serialize_details(data):
    """Serialize dict to JSON string for database."""
    if data is None:
        return None
    if isinstance(data, str):
        return data
    return json.dumps(data)


def deserialize_details(data_str):
    """Deserialize JSON string from database to dict."""
    if data_str is None:
        return None
    if isinstance(data_str, dict):
        return data_str
    try:
        return json.loads(data_str)
    except:
        return data_str


@router.get("", response_model=List[RuleEvaluationResponse])
async def get_all_rule_evaluations():
    """Get all rule evaluations."""
    try:
        results = execute_query(RULE_EVALUATIONS_QUERIES['get_all'])
        for evaluation in results:
            if 'details' in evaluation and evaluation['details']:
                evaluation['details'] = deserialize_details(evaluation['details'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule evaluations: {str(e)}"
        )


@router.get("/{evaluation_id}", response_model=RuleEvaluationResponse)
async def get_rule_evaluation_by_id(evaluation_id: str):
    """Get a rule evaluation by ID."""
    try:
        result = execute_query_single(RULE_EVALUATIONS_QUERIES['get_by_id'], (evaluation_id,))
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule evaluation with id {evaluation_id} not found"
            )
        if 'details' in result and result['details']:
            result['details'] = deserialize_details(result['details'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rule evaluation: {str(e)}"
        )


@router.post("", response_model=RuleEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_rule_evaluation(evaluation: RuleEvaluationCreate):
    """Create a new rule evaluation."""
    try:
        evaluation_id = str(uuid.uuid4())
        
        params = (
            evaluation_id,
            evaluation.rule_id,
            evaluation.result,
            serialize_details(evaluation.details)
        )
        
        execute_query(RULE_EVALUATIONS_QUERIES['create'], params, fetch=False)
        
        # Fetch the created evaluation
        result = execute_query_single(RULE_EVALUATIONS_QUERIES['get_by_id'], (evaluation_id,))
        if result and 'details' in result and result['details']:
            result['details'] = deserialize_details(result['details'])
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rule evaluation: {str(e)}"
        )


@router.put("/{evaluation_id}", response_model=RuleEvaluationResponse)
async def update_rule_evaluation(evaluation_id: str, evaluation: RuleEvaluationUpdate):
    """Update a rule evaluation."""
    try:
        # Check if evaluation exists
        existing = execute_query_single(RULE_EVALUATIONS_QUERIES['get_by_id'], (evaluation_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule evaluation with id {evaluation_id} not found"
            )
        
        # Build update query dynamically
        updates = []
        params = []
        
        if evaluation.result is not None:
            updates.append("result = %s")
            params.append(evaluation.result)
        if evaluation.details is not None:
            updates.append("details = %s")
            params.append(serialize_details(evaluation.details))
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        params.append(evaluation_id)
        
        query = f"UPDATE rule_evaluations SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params), fetch=False)
        
        # Fetch updated evaluation
        result = execute_query_single(RULE_EVALUATIONS_QUERIES['get_by_id'], (evaluation_id,))
        if result and 'details' in result and result['details']:
            result['details'] = deserialize_details(result['details'])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating rule evaluation: {str(e)}"
        )


@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule_evaluation(evaluation_id: str):
    """Delete a rule evaluation."""
    try:
        # Check if evaluation exists
        existing = execute_query_single(RULE_EVALUATIONS_QUERIES['get_by_id'], (evaluation_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule evaluation with id {evaluation_id} not found"
            )
        
        execute_query(RULE_EVALUATIONS_QUERIES['delete'], (evaluation_id,), fetch=False)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting rule evaluation: {str(e)}"
        )
