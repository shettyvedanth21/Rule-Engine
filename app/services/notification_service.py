"""
Notification Service Module
Handles sending notifications via different channels: SMS, WhatsApp, Telegram, Email, Webhook
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
import json

# Configuration - In production, these should be in environment variables
SMS_API_URL = "https://sms.example.com/api/send"  # Replace with actual SMS provider
SMS_API_KEY = "your-sms-api-key"  # Replace with actual key
WHATSAPP_API_URL = "https://api.whatsapp.com/send"  # Replace with actual provider
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"  # Replace with actual token
EMAIL_SMTP_HOST = "smtp.example.com"
EMAIL_SMTP_PORT = 587
EMAIL_USERNAME = "notifications@example.com"
EMAIL_PASSWORD = "your-email-password"
WEBHOOK_TIMEOUT = 10  # seconds


class NotificationService:
    """Service class for sending notifications via different channels"""
    
    @staticmethod
    def send_sms(phone_number: str, message: str, title: str = "") -> Dict[str, Any]:
        """
        Send SMS notification
        
        Args:
            phone_number: Recipient phone number
            message: Message content
            title: Optional title
            
        Returns:
            Dict with success status and details
        """
        try:
            # Construct SMS message (truncate if needed for SMS length limits)
            full_message = f"{title}: {message}" if title else message
            if len(full_message) > 160:
                full_message = full_message[:157] + "..."
            
            # TODO: Replace with actual SMS provider API call
            # Example with generic HTTP API:
            payload = {
                "to": phone_number,
                "message": full_message,
                "api_key": SMS_API_KEY
            }
            
            # Simulated response for testing
            # In production, uncomment actual API call:
            # response = requests.post(SMS_API_URL, json=payload, timeout=10)
            # response.raise_for_status()
            
            return {
                "success": True,
                "channel": "SMS",
                "recipient": phone_number,
                "message": "SMS sent successfully (simulated)",
                "details": payload
            }
        except Exception as e:
            return {
                "success": False,
                "channel": "SMS",
                "recipient": phone_number,
                "error": str(e)
            }
    
    @staticmethod
    def send_whatsapp(whatsapp_number: str, message: str, title: str = "") -> Dict[str, Any]:
        """
        Send WhatsApp notification
        
        Args:
            whatsapp_number: Recipient WhatsApp number
            message: Message content
            title: Optional title
            
        Returns:
            Dict with success status and details
        """
        try:
            full_message = f"*{title}*\n\n{message}" if title else message
            
            # TODO: Replace with actual WhatsApp Business API call
            # Example with WhatsApp Business API:
            payload = {
                "to": whatsapp_number,
                "type": "text",
                "text": {"body": full_message}
            }
            
            # Simulated response for testing
            return {
                "success": True,
                "channel": "WHATSAPP",
                "recipient": whatsapp_number,
                "message": "WhatsApp sent successfully (simulated)",
                "details": payload
            }
        except Exception as e:
            return {
                "success": False,
                "channel": "WHATSAPP",
                "recipient": whatsapp_number,
                "error": str(e)
            }
    
    @staticmethod
    def send_telegram(telegram_chat_id: str, message: str, title: str = "") -> Dict[str, Any]:
        """
        Send Telegram message
        
        Args:
            telegram_chat_id: Recipient Telegram chat ID
            message: Message content
            title: Optional title
            
        Returns:
            Dict with success status and details
        """
        try:
            full_message = f"*{title}*\n\n{message}" if title else message
            
            # Telegram Bot API
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": telegram_chat_id,
                "text": full_message,
                "parse_mode": "Markdown"
            }
            
            # Simulated response for testing
            # In production, uncomment actual API call:
            # response = requests.post(telegram_url, json=payload, timeout=10)
            # response.raise_for_status()
            
            return {
                "success": True,
                "channel": "TELEGRAM",
                "recipient": telegram_chat_id,
                "message": "Telegram message sent successfully (simulated)",
                "details": payload
            }
        except Exception as e:
            return {
                "success": False,
                "channel": "TELEGRAM",
                "recipient": telegram_chat_id,
                "error": str(e)
            }
    
    @staticmethod
    def send_email(recipient_email: str, message: str, title: str = "") -> Dict[str, Any]:
        """
        Send Email notification
        
        Args:
            recipient_email: Recipient email address
            message: Message content
            title: Email subject
            
        Returns:
            Dict with success status and details
        """
        try:
            subject = title or "Rule Alert Notification"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_USERNAME
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Create HTML and plain text versions
            text_content = message
            html_content = f"""
            <html>
                <body>
                    <h2>{subject}</h2>
                    <p>{message.replace(chr(10), '<br>')}</p>
                    <hr>
                    <p><small>This is an automated notification from the Rule Engine.</small></p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # In production, uncomment actual SMTP send:
            # with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as server:
            #     server.starttls()
            #     server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            #     server.send_message(msg)
            
            return {
                "success": True,
                "channel": "EMAIL",
                "recipient": recipient_email,
                "message": "Email sent successfully (simulated)",
                "subject": subject
            }
        except Exception as e:
            return {
                "success": False,
                "channel": "EMAIL",
                "recipient": recipient_email,
                "error": str(e)
            }
    
    @staticmethod
    def send_webhook(webhook_url: str, message: str, title: str = "", 
                     rule_id: str = "", extra_data: Dict = None) -> Dict[str, Any]:
        """
        Send Webhook notification
        
        Args:
            webhook_url: Target webhook URL
            message: Message content
            title: Optional title
            rule_id: Related rule ID
            extra_data: Additional data to send
            
        Returns:
            Dict with success status and details
        """
        try:
            payload = {
                "title": title,
                "message": message,
                "rule_id": rule_id,
                "channel": "WEBHOOK",
                "timestamp": str(__import__('datetime').datetime.now().isoformat())
            }
            
            if extra_data:
                payload.update(extra_data)
            
            # In production, uncomment actual webhook call:
            # response = requests.post(
            #     webhook_url, 
            #     json=payload, 
            #     timeout=WEBHOOK_TIMEOUT,
            #     headers={"Content-Type": "application/json"}
            # )
            # response.raise_for_status()
            
            return {
                "success": True,
                "channel": "WEBHOOK",
                "recipient": webhook_url,
                "message": "Webhook sent successfully (simulated)",
                "payload": payload
            }
        except Exception as e:
            return {
                "success": False,
                "channel": "WEBHOOK",
                "recipient": webhook_url,
                "error": str(e)
            }
    
    @staticmethod
    def send_inapp(inapp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send In-App notification (stored in database for display in UI)
        
        Args:
            inapp_data: Dict with title, message, rule_id, event_id, priority
            
        Returns:
            Dict with success status and details
        """
        try:
            # In-app notifications are stored in the database
            # The actual display would be handled by the frontend
            from app.database import execute_query
            import uuid
            
            notification_id = str(uuid.uuid4())
            
            # Create in-app notification in database
            # This would use a separate inapp_notifications table
            # For now, return success as it would be handled separately
            
            return {
                "success": True,
                "channel": "INAPP",
                "notification_id": notification_id,
                "message": "In-App notification created successfully",
                "data": inapp_data
            }
        except Exception as e:
            return {
                "success": False,
                "channel": "INAPP",
                "error": str(e)
            }
    
    @staticmethod
    def send_notification_by_channel(channel: str, notification_data: Dict) -> Dict[str, Any]:
        """
        Send notification based on channel type
        
        Args:
            channel: Channel type (SMS, WHATSAPP, TELEGRAM, EMAIL, WEBHOOK, INAPP)
            notification_data: Dict containing notification details
            
        Returns:
            Dict with success status and details
        """
        channel = channel.upper()
        
        if channel == "SMS":
            return NotificationService.send_sms(
                phone_number=notification_data.get("recipient_phone", ""),
                message=notification_data.get("message", ""),
                title=notification_data.get("title", "")
            )
        elif channel == "WHATSAPP":
            return NotificationService.send_whatsapp(
                whatsapp_number=notification_data.get("whatsapp_number", ""),
                message=notification_data.get("message", ""),
                title=notification_data.get("title", "")
            )
        elif channel == "TELEGRAM":
            return NotificationService.send_telegram(
                telegram_chat_id=notification_data.get("telegram_chat_id", ""),
                message=notification_data.get("message", ""),
                title=notification_data.get("title", "")
            )
        elif channel == "EMAIL":
            return NotificationService.send_email(
                recipient_email=notification_data.get("recipient_email", ""),
                message=notification_data.get("message", ""),
                title=notification_data.get("title", "")
            )
        elif channel == "WEBHOOK":
            return NotificationService.send_webhook(
                webhook_url=notification_data.get("webhook_url", ""),
                message=notification_data.get("message", ""),
                title=notification_data.get("title", ""),
                rule_id=notification_data.get("rule_id", "")
            )
        elif channel == "INAPP":
            return NotificationService.send_inapp(
                inapp_data=notification_data.get("inapp_data", {})
            )
        else:
            return {
                "success": False,
                "channel": channel,
                "error": f"Unsupported channel: {channel}"
            }
    
    @staticmethod
    def send_multi_channel_notification(channels: List[str], notification_data: Dict) -> List[Dict[str, Any]]:
        """
        Send notification to multiple channels
        
        Args:
            channels: List of channel types
            notification_data: Dict containing notification details
            
        Returns:
            List of results for each channel
        """
        results = []
        for channel in channels:
            result = NotificationService.send_notification_by_channel(channel, notification_data)
            results.append(result)
        return results


# Singleton instance for easy import
notification_service = NotificationService()
