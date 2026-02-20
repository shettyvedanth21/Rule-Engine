from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime


# ============== RULES SCHEMAS ==============
class RuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    condition: Optional[str] = None
    is_active: bool = True
    priority: int = 0


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    condition: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class RuleResponse(RuleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============== RULE_ACTIONS SCHEMAS ==============
class RuleActionBase(BaseModel):
    rule_id: str = Field(..., min_length=36, max_length=36)
    action_type: str = Field(..., min_length=1, max_length=100)
    action_config: Optional[str] = None


class RuleActionCreate(RuleActionBase):
    pass


class RuleActionUpdate(BaseModel):
    action_type: Optional[str] = Field(None, min_length=1, max_length=100)
    action_config: Optional[str] = None


class RuleActionResponse(RuleActionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============== RULE_EVALUATIONS SCHEMAS ==============
class RuleEvaluationBase(BaseModel):
    rule_id: str = Field(..., min_length=36, max_length=36)
    result: bool
    details: Optional[str] = None


class RuleEvaluationCreate(RuleEvaluationBase):
    pass


class RuleEvaluationUpdate(BaseModel):
    result: Optional[bool] = None
    details: Optional[str] = None


class RuleEvaluationResponse(RuleEvaluationBase):
    id: str
    evaluated_at: datetime

    model_config = {"from_attributes": True}


# ============== RULE_TRIGGERS SCHEMAS ==============
class RuleTriggerBase(BaseModel):
    rule_id: str = Field(..., min_length=36, max_length=36)
    trigger_type: str = Field(..., min_length=1, max_length=100)
    trigger_config: Optional[str] = None
    is_active: bool = True


class RuleTriggerCreate(RuleTriggerBase):
    pass


class RuleTriggerUpdate(BaseModel):
    trigger_type: Optional[str] = Field(None, min_length=1, max_length=100)
    trigger_config: Optional[str] = None
    is_active: Optional[bool] = None


class RuleTriggerResponse(RuleTriggerBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============== GENERIC RESPONSE SCHEMAS ==============
class MessageResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


# ============== NOTIFICATION SCHEMAS ==============
class NotificationBase(BaseModel):
    rule_id: str = Field(..., min_length=36, max_length=36)
    title: str = Field(..., min_length=1, max_length=255)
    message: str
    notification_type: str = "INFO"
    channel: str = Field(..., description="SMS, WHATSAPP, TELEGRAM, EMAIL, WEBHOOK")
    priority: str = "MEDIUM"
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None


class NotificationCreate(NotificationBase):
    send_at: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    status: Optional[str] = None
    acknowledged_by: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: str
    status: str
    triggered_at: datetime
    send_at: datetime
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    escalation_level: int
    next_escalation_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============== NOTIFICATION SETTINGS SCHEMAS ==============
class NotificationSettingsBase(BaseModel):
    rule_id: str = Field(..., min_length=36, max_length=36)
    notification_type: str = "EMAIL"
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
    push_token: Optional[str] = None
    send_interval_minutes: int = 60
    escalation_enabled: bool = True
    escalation_interval_minutes: int = 60
    max_escalations: int = 3


class NotificationSettingsCreate(NotificationSettingsBase):
    pass


class NotificationSettingsUpdate(BaseModel):
    notification_type: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
    push_token: Optional[str] = None
    send_interval_minutes: Optional[int] = None
    escalation_enabled: Optional[bool] = None
    escalation_interval_minutes: Optional[int] = None
    max_escalations: Optional[int] = None
    is_active: Optional[bool] = None


class NotificationSettingsResponse(NotificationSettingsBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============== NOTIFICATION SCHEDULE SCHEMAS ==============
class TriggerNotificationRequest(BaseModel):
    rule_id: str
    title: str
    message: str
    priority: str = "MEDIUM"
    notification_type: str = "ALERT"
    channel: str = Field(..., description="SMS, WHATSAPP, TELEGRAM, EMAIL, WEBHOOK")
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None


# New schema for triggering notifications to multiple channels
class TriggerMultiChannelNotificationRequest(BaseModel):
    rule_id: str
    title: str
    message: str
    priority: str = "MEDIUM"
    notification_type: str = "ALERT"
    channels: List[str] = Field(..., description="List of channels: SMS, WHATSAPP, TELEGRAM, EMAIL, WEBHOOK")
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    whatsapp_number: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
