import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime, timedelta
import json

from app.database import execute_query, execute_query_single
from app.models import NOTIFICATIONS_QUERIES, NOTIFICATION_SETTINGS_QUERIES
from app.schemas import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationSettingsCreate, NotificationSettingsUpdate, NotificationSettingsResponse,
    TriggerNotificationRequest, TriggerMultiChannelNotificationRequest
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ==================== NOTIFICATIONS ====================

@router.get("", response_model=List[NotificationResponse])
async def get_all_notifications():
    """Get all notifications."""
    try:
        results = execute_query(NOTIFICATIONS_QUERIES['get_all'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )


@router.get("/pending", response_model=List[NotificationResponse])
async def get_pending_notifications():
    """Get all pending notifications (ready to send)."""
    try:
        results = execute_query(NOTIFICATIONS_QUERIES['get_pending'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pending notifications: {str(e)}"
        )


@router.get("/escalations", response_model=List[NotificationResponse])
async def get_escalation_notifications():
    """Get notifications that need escalation."""
    try:
        results = execute_query(NOTIFICATIONS_QUERIES['get_escalations'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching escalations: {str(e)}"
        )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification_by_id(notification_id: str):
    """Get a notification by ID."""
    try:
        result = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notification: {str(e)}"
        )


@router.get("/by-channel/{channel}", response_model=List[NotificationResponse])
async def get_notifications_by_channel(channel: str):
    """Get all notifications for a specific channel (SMS, WHATSAPP, TELEGRAM, EMAIL, WEBHOOK)."""
    try:
        results = execute_query(NOTIFICATIONS_QUERIES['get_by_channel'], (channel.upper(),))
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(notification: NotificationCreate):
    """Create a new notification."""
    try:
        notification_id = str(uuid.uuid4())
        
        # Get notification settings for escalation info
        settings = execute_query_single(
            NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'], 
            (notification.rule_id,)
        )
        
        send_at = notification.send_at if notification.send_at else datetime.now()
        escalation_level = 0
        
        # If escalation is enabled, set next escalation time
        next_escalation_at = None
        if settings and settings.get('escalation_enabled'):
            next_escalation_at = send_at + timedelta(minutes=settings['escalation_interval_minutes'])
        
        # Get channel, default to SMS if not specified
        channel = getattr(notification, 'channel', 'SMS')
        
        params = (
            notification_id,
            notification.rule_id,
            notification.title,
            notification.message,
            notification.notification_type,
            channel,
            'PENDING',
            notification.priority,
            notification.recipient_email,
            notification.recipient_phone,
            notification.whatsapp_number if hasattr(notification, 'whatsapp_number') else None,
            notification.telegram_chat_id if hasattr(notification, 'telegram_chat_id') else None,
            notification.webhook_url if hasattr(notification, 'webhook_url') else None,
            send_at,
            escalation_level
        )
        
        execute_query(NOTIFICATIONS_QUERIES['create'], params, fetch=False)
        
        # Fetch the created notification
        result = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating notification: {str(e)}"
        )


@router.post("/trigger", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def trigger_notification(request: TriggerNotificationRequest):
    """Trigger a notification for a rule."""
    try:
        # Get notification settings for this rule
        settings = execute_query_single(
            NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'], 
            (request.rule_id,)
        )
        
        notification_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Determine recipient
        recipient_email = request.recipient_email
        recipient_phone = request.recipient_phone
        whatsapp_number = request.whatsapp_number
        telegram_chat_id = request.telegram_chat_id
        webhook_url = request.webhook_url
        
        # Use settings if not provided
        if not recipient_email and settings:
            recipient_email = settings.get('recipient_email')
        if not recipient_phone and settings:
            recipient_phone = settings.get('recipient_phone')
        if not whatsapp_number and settings:
            whatsapp_number = settings.get('whatsapp_number')
        if not telegram_chat_id and settings:
            telegram_chat_id = settings.get('telegram_chat_id')
        if not webhook_url and settings:
            webhook_url = settings.get('webhook_url')
        
        # Calculate next escalation time
        escalation_level = 0
        next_escalation_at = None
        
        if settings and settings.get('escalation_enabled'):
            escalation_interval = settings.get('escalation_interval_minutes', 60)
            next_escalation_at = now + timedelta(minutes=escalation_interval)
        
        # Get channel
        channel = request.channel
        
        params = (
            notification_id,
            request.rule_id,
            request.title,
            request.message,
            request.notification_type,
            channel,
            'PENDING',
            request.priority,
            recipient_email,
            recipient_phone,
            whatsapp_number,
            telegram_chat_id,
            webhook_url,
            now,
            escalation_level
        )
        
        execute_query(NOTIFICATIONS_QUERIES['create'], params, fetch=False)
        
        # Fetch the created notification
        result = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering notification: {str(e)}"
        )


@router.post("/trigger-multi", response_model=List[NotificationResponse], status_code=status.HTTP_201_CREATED)
async def trigger_multi_channel_notification(request: TriggerMultiChannelNotificationRequest):
    """Trigger notifications to multiple channels for a rule.
    
    This endpoint creates separate notifications for each selected channel
    and saves them all in the database.
    """
    try:
        # Get notification settings for this rule
        settings = execute_query_single(
            NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'], 
            (request.rule_id,)
        )
        
        now = datetime.now()
        created_notifications = []
        
        # Determine recipients from settings if not provided
        recipient_email = request.recipient_email or (settings.get('recipient_email') if settings else None)
        recipient_phone = request.recipient_phone or (settings.get('recipient_phone') if settings else None)
        whatsapp_number = request.whatsapp_number or (settings.get('whatsapp_number') if settings else None)
        telegram_chat_id = request.telegram_chat_id or (settings.get('telegram_chat_id') if settings else None)
        webhook_url = request.webhook_url or (settings.get('webhook_url') if settings else None)
        
        # Calculate next escalation time
        escalation_level = 0
        next_escalation_at = None
        
        if settings and settings.get('escalation_enabled'):
            escalation_interval = settings.get('escalation_interval_minutes', 60)
            next_escalation_at = now + timedelta(minutes=escalation_interval)
        
        # Create a separate notification for each channel
        for channel in request.channels:
            notification_id = str(uuid.uuid4())
            
            # Prepare params based on channel
            params = (
                notification_id,
                request.rule_id,
                request.title,
                request.message,
                request.notification_type,
                channel.upper(),
                'PENDING',
                request.priority,
                recipient_email if channel.upper() == 'EMAIL' else None,
                recipient_phone if channel.upper() == 'SMS' else None,
                whatsapp_number if channel.upper() == 'WHATSAPP' else None,
                telegram_chat_id if channel.upper() == 'TELEGRAM' else None,
                webhook_url if channel.upper() == 'WEBHOOK' else None,
                now,
                escalation_level
            )
            
            execute_query(NOTIFICATIONS_QUERIES['create'], params, fetch=False)
            
            # Fetch the created notification
            result = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
            if result:
                created_notifications.append(result)
        
        return created_notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering multi-channel notification: {str(e)}"
        )


@router.put("/{notification_id}/send", response_model=NotificationResponse)
async def mark_notification_sent(notification_id: str):
    """Mark a notification as sent."""
    try:
        existing = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found"
            )
        
        execute_query(NOTIFICATIONS_QUERIES['update_status'], ('SENT', notification_id), fetch=False)
        
        result = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )


@router.put("/{notification_id}/acknowledge")
async def acknowledge_notification(notification_id: str, acknowledged_by: str = "User"):
    """Acknowledge a notification."""
    try:
        existing = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found"
            )
        
        execute_query(NOTIFICATIONS_QUERIES['acknowledge'], (acknowledged_by, notification_id), fetch=False)
        
        return {"success": True, "message": "Notification acknowledged"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acknowledging notification: {str(e)}"
        )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: str):
    """Delete a notification."""
    try:
        existing = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found"
            )
        
        execute_query("DELETE FROM notifications WHERE id = %s", (notification_id,), fetch=False)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting notification: {str(e)}"
        )


# ==================== NOTIFICATION SETTINGS ====================

@router.get("/settings", response_model=List[NotificationSettingsResponse])
async def get_all_notification_settings():
    """Get all notification settings."""
    try:
        results = execute_query(NOTIFICATION_SETTINGS_QUERIES['get_all'])
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )


@router.get("/settings/{settings_id}", response_model=NotificationSettingsResponse)
async def get_notification_settings_by_id(settings_id: str):
    """Get notification settings by ID."""
    try:
        result = execute_query_single(NOTIFICATION_SETTINGS_QUERIES['get_by_id'], (settings_id,))
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settings with id {settings_id} not found"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )


@router.get("/settings/rule/{rule_id}", response_model=List[NotificationSettingsResponse])
async def get_notification_settings_by_rule(rule_id: str):
    """Get notification settings for a specific rule."""
    try:
        results = execute_query(NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'], (rule_id,))
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )


@router.post("/settings", response_model=NotificationSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_settings(settings: NotificationSettingsCreate):
    """Create notification settings for a rule."""
    try:
        settings_id = str(uuid.uuid4())
        
        params = (
            settings_id,
            settings.rule_id,
            settings.notification_type,
            settings.recipient_email,
            settings.recipient_phone,
            settings.send_interval_minutes,
            settings.escalation_enabled,
            settings.escalation_interval_minutes,
            settings.max_escalations,
            True
        )
        
        execute_query(NOTIFICATION_SETTINGS_QUERIES['create'], params, fetch=False)
        
        result = execute_query_single(NOTIFICATION_SETTINGS_QUERIES['get_by_id'], (settings_id,))
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating settings: {str(e)}"
        )


@router.put("/settings/{settings_id}", response_model=NotificationSettingsResponse)
async def update_notification_settings(settings_id: str, settings: NotificationSettingsUpdate):
    """Update notification settings."""
    try:
        existing = execute_query_single(NOTIFICATION_SETTINGS_QUERIES['get_by_id'], (settings_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settings with id {settings_id} not found"
            )
        
        updates = []
        params = []
        
        if settings.notification_type is not None:
            updates.append("notification_type = %s")
            params.append(settings.notification_type)
        if settings.recipient_email is not None:
            updates.append("recipient_email = %s")
            params.append(settings.recipient_email)
        if settings.recipient_phone is not None:
            updates.append("recipient_phone = %s")
            params.append(settings.recipient_phone)
        if settings.send_interval_minutes is not None:
            updates.append("send_interval_minutes = %s")
            params.append(settings.send_interval_minutes)
        if settings.escalation_enabled is not None:
            updates.append("escalation_enabled = %s")
            params.append(settings.escalation_enabled)
        if settings.escalation_interval_minutes is not None:
            updates.append("escalation_interval_minutes = %s")
            params.append(settings.escalation_interval_minutes)
        if settings.max_escalations is not None:
            updates.append("max_escalations = %s")
            params.append(settings.max_escalations)
        if settings.is_active is not None:
            updates.append("is_active = %s")
            params.append(settings.is_active)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        params.append(settings_id)
        
        query = f"UPDATE notification_settings SET {', '.join(updates)} WHERE id = %s"
        execute_query(query, tuple(params), fetch=False)
        
        result = execute_query_single(NOTIFICATION_SETTINGS_QUERIES['get_by_id'], (settings_id,))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )


@router.delete("/settings/{settings_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_settings(settings_id: str):
    """Delete (deactivate) notification settings."""
    try:
        existing = execute_query_single(NOTIFICATION_SETTINGS_QUERIES['get_by_id'], (settings_id,))
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Settings with id {settings_id} not found"
            )
        
        execute_query(NOTIFICATION_SETTINGS_QUERIES['delete'], (settings_id,), fetch=False)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting settings: {str(e)}"
        )


# ==================== PROCESS NOTIFICATIONS (For Scheduler) ====================

@router.post("/process")
async def process_notifications():
    """Process pending notifications and send them via appropriate channels."""
    try:
        # Get pending notifications
        pending = execute_query(NOTIFICATIONS_QUERIES['get_pending'])
        
        # Get escalations
        escalations = execute_query(NOTIFICATIONS_QUERIES['get_escalations'])
        
        processed_count = 0
        sent_results = []
        
        # Process pending notifications
        for notif in pending:
            # Prepare notification data for sending
            notification_data = {
                "title": notif.get('title', ''),
                "message": notif.get('message', ''),
                "rule_id": notif.get('rule_id', ''),
                "recipient_email": notif.get('recipient_email'),
                "recipient_phone": notif.get('recipient_phone'),
                "whatsapp_number": notif.get('whatsapp_number'),
                "telegram_chat_id": notif.get('telegram_chat_id'),
                "webhook_url": notif.get('webhook_url')
            }
            
            channel = notif.get('channel', 'SMS')
            
            # Send notification via appropriate channel
            send_result = NotificationService.send_notification_by_channel(channel, notification_data)
            sent_results.append({
                "notification_id": notif['id'],
                "channel": channel,
                "result": send_result
            })
            
            # Mark as sent
            execute_query(NOTIFICATIONS_QUERIES['update_status'], ('SENT', notif['id']), fetch=False)
            processed_count += 1
        
        # Process escalations
        for notif in escalations:
            # Get settings to check max escalations
            settings = execute_query_single(
                NOTIFICATION_SETTINGS_QUERIES['get_by_rule_id'],
                (notif['rule_id'],)
            )
            
            if settings:
                current_level = notif.get('escalation_level', 0)
                max_level = settings.get('max_escalations', 3)
                
                if current_level < max_level:
                    # Escalate
                    new_level = current_level + 1
                    interval = settings.get('escalation_interval_minutes', 60)
                    next_escalation = datetime.now() + timedelta(minutes=interval)
                    
                    execute_query(
                        NOTIFICATIONS_QUERIES['escalate'],
                        (new_level, next_escalation, next_escalation, notif['id']),
                        fetch=False
                    )
                    processed_count += 1
        
        return {
            "success": True,
            "processed": processed_count,
            "pending": len(pending),
            "escalations": len(escalations),
            "sent_results": sent_results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing notifications: {str(e)}"
        )


# ==================== SEND NOTIFICATIONS IMMEDIATELY ====================

@router.post("/send-now")
async def send_notification_now(notification_id: str):
    """Send a specific notification immediately via its channel."""
    try:
        # Get the notification
        notif = execute_query_single(NOTIFICATIONS_QUERIES['get_by_id'], (notification_id,))
        
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found"
            )
        
        # Prepare notification data
        notification_data = {
            "title": notif.get('title', ''),
            "message": notif.get('message', ''),
            "rule_id": notif.get('rule_id', ''),
            "recipient_email": notif.get('recipient_email'),
            "recipient_phone": notif.get('recipient_phone'),
            "whatsapp_number": notif.get('whatsapp_number'),
            "telegram_chat_id": notif.get('telegram_chat_id'),
            "webhook_url": notif.get('webhook_url')
        }
        
        channel = notif.get('channel', 'SMS')
        
        # Send notification
        send_result = NotificationService.send_notification_by_channel(channel, notification_data)
        
        # Mark as sent if successful
        if send_result.get('success'):
            execute_query(NOTIFICATIONS_QUERIES['update_status'], ('SENT', notification_id), fetch=False)
        
        return {
            "success": send_result.get('success', False),
            "notification_id": notification_id,
            "channel": channel,
            "result": send_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )


@router.post("/send-now-multi")
async def send_multi_channel_notifications_now(rule_id: str, channels: List[str]):
    """Send notifications to multiple channels immediately for a rule.
    
    This gets all pending notifications for the rule and sends them via
    their respective channels.
    """
    try:
        # Get pending notifications for this rule
        pending = execute_query(
            "SELECT * FROM notifications WHERE rule_id = %s AND status = 'PENDING' AND send_at <= NOW()",
            (rule_id,)
        )
        
        if not pending:
            return {
                "success": True,
                "message": "No pending notifications to send",
                "sent_count": 0
            }
        
        sent_results = []
        
        for notif in pending:
            # Prepare notification data
            notification_data = {
                "title": notif.get('title', ''),
                "message": notif.get('message', ''),
                "rule_id": notif.get('rule_id', ''),
                "recipient_email": notif.get('recipient_email'),
                "recipient_phone": notif.get('recipient_phone'),
                "whatsapp_number": notif.get('whatsapp_number'),
                "telegram_chat_id": notif.get('telegram_chat_id'),
                "webhook_url": notif.get('webhook_url')
            }
            
            channel = notif.get('channel', 'SMS')
            
            # Skip if channel not in requested list
            if channel.upper() not in [c.upper() for c in channels]:
                continue
            
            # Send notification
            send_result = NotificationService.send_notification_by_channel(channel, notification_data)
            
            # Mark as sent if successful
            if send_result.get('success'):
                execute_query(NOTIFICATIONS_QUERIES['update_status'], ('SENT', notif['id']), fetch=False)
            
            sent_results.append({
                "notification_id": notif['id'],
                "channel": channel,
                "result": send_result
            })
        
        return {
            "success": True,
            "sent_count": len(sent_results),
            "results": sent_results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending multi-channel notifications: {str(e)}"
        )
