"""
Unified Notification Service Module

Production-ready notification service supporting multiple channels:
- SMS (via Twilio)
- WhatsApp (via Twilio WhatsApp Business API)
- Telegram (via Bot API)
- Email (via SMTP)
- Webhook (HTTP POST)
- In-App (Database storage)

This module follows clean architecture principles with:
- Central send_notification method
- Modular helper methods per channel
- Proper credential validation
- Comprehensive error handling
- Structured response format
- Comprehensive logging
"""

import os
import logging
import smtplib
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration - Environment Variables
# =============================================================================

class NotificationConfig:
    """Configuration class for notification service credentials."""
    
    # SMS (Twilio) Configuration
    SMS_ACCOUNT_SID = os.getenv("SMS_ACCOUNT_SID", "")
    SMS_AUTH_TOKEN = os.getenv("SMS_AUTH_TOKEN", "")
    SMS_FROM_NUMBER = os.getenv("SMS_FROM_NUMBER", "")
    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio")  # Configurable provider
    
    # WhatsApp (Twilio) Configuration
    WHATSAPP_ACCOUNT_SID = os.getenv("WHATSAPP_ACCOUNT_SID", "")
    WHATSAPP_AUTH_TOKEN = os.getenv("WHATSAPP_AUTH_TOKEN", "")
    WHATSAPP_FROM_NUMBER = os.getenv("WHATSAPP_FROM_NUMBER", "")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Email (SMTP) Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
    
    # Webhook Configuration
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
    
    # General Configuration
    WEBHOOK_TIMEOUT = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    SMS_MAX_LENGTH = 160
    WHATSAPP_MAX_LENGTH = 4096


# =============================================================================
# Custom Exceptions
# =============================================================================

class NotificationError(Exception):
    """Base exception for notification errors."""
    pass


class CredentialError(NotificationError):
    """Raised when required credentials are missing."""
    pass


class ChannelNotSupportedError(NotificationError):
    """Raised when notification channel is not supported."""
    pass


class SendError(NotificationError):
    """Raised when sending notification fails."""
    pass


# =============================================================================
# Notification Service Class
# =============================================================================

class NotificationService:
    """
    Unified Notification Service supporting multiple channels.
    
    Usage:
        service = NotificationService()
        result = service.send_notification("sms", to_number="+1234567890", message="Hello")
    """
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        Initialize the notification service.
        
        Args:
            config: Optional configuration object. If not provided, uses environment variables.
        """
        self.config = config or NotificationConfig()
        self._channel_credentials = {
            "sms": self._validate_sms_credentials,
            "whatsapp": self._validate_whatsapp_credentials,
            "telegram": self._validate_telegram_credentials,
            "email": self._validate_email_credentials,
            "webhook": self._validate_webhook_credentials,
            "in_app": self._validate_in_app_credentials,
        }
        logger.info("NotificationService initialized")
    
    # =========================================================================
    # Credential Validation Methods
    # =========================================================================
    
    def _validate_sms_credentials(self) -> None:
        """Validate SMS (Twilio) credentials."""
        missing = []
        if not self.config.SMS_ACCOUNT_SID:
            missing.append("SMS_ACCOUNT_SID")
        if not self.config.SMS_AUTH_TOKEN:
            missing.append("SMS_AUTH_TOKEN")
        if not self.config.SMS_FROM_NUMBER:
            missing.append("SMS_FROM_NUMBER")
        
        if missing:
            raise CredentialError(f"Missing SMS credentials: {', '.join(missing)}")
    
    def _validate_whatsapp_credentials(self) -> None:
        """Validate WhatsApp (Twilio) credentials."""
        missing = []
        if not self.config.WHATSAPP_ACCOUNT_SID:
            missing.append("WHATSAPP_ACCOUNT_SID")
        if not self.config.WHATSAPP_AUTH_TOKEN:
            missing.append("WHATSAPP_AUTH_TOKEN")
        if not self.config.WHATSAPP_FROM_NUMBER:
            missing.append("WHATSAPP_FROM_NUMBER")
        
        if missing:
            raise CredentialError(f"Missing WhatsApp credentials: {', '.join(missing)}")
    
    def _validate_telegram_credentials(self) -> None:
        """Validate Telegram credentials."""
        if not self.config.TELEGRAM_BOT_TOKEN:
            raise CredentialError("Missing Telegram bot token: TELEGRAM_BOT_TOKEN")
    
    def _validate_email_credentials(self) -> None:
        """Validate Email (SMTP) credentials."""
        missing = []
        if not self.config.SMTP_HOST:
            missing.append("SMTP_HOST")
        if not self.config.SMTP_USERNAME:
            missing.append("SMTP_USERNAME")
        if not self.config.SMTP_PASSWORD:
            missing.append("SMTP_PASSWORD")
        
        if missing:
            raise CredentialError(f"Missing Email credentials: {', '.join(missing)}")
    
    def _validate_webhook_credentials(self) -> None:
        """Validate Webhook configuration."""
        if not self.config.WEBHOOK_URL:
            raise CredentialError("Missing Webhook URL: WEBHOOK_URL")
    
    def _validate_in_app_credentials(self) -> None:
        """In-App notifications don't require external credentials."""
        pass
    
    def _validate_channel(self, channel: str) -> None:
        """
        Validate that the channel is supported and credentials are available.
        
        Args:
            channel: The notification channel to validate.
            
        Raises:
            ChannelNotSupportedError: If channel is not supported.
            CredentialError: If required credentials are missing.
        """
        channel_lower = channel.lower()
        
        if channel_lower not in self._channel_credentials:
            raise ChannelNotSupportedError(
                f"Channel '{channel}' not supported. "
                f"Supported channels: {', '.join(self._channel_credentials.keys())}"
            )
        
        # Validate credentials for the channel
        validator = self._channel_credentials[channel_lower]
        validator()
    
    # =========================================================================
    # SMS Channel (Twilio)
    # =========================================================================
    
    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send SMS notification via Twilio.
        
        Args:
            to_number: Recipient phone number (E.164 format, e.g., +1234567890).
            message: Message content to send.
            
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            CredentialError: If required credentials are missing.
            SendError: If sending fails.
        """
        logger.info(f"Sending SMS to {to_number}")
        
        # Validate credentials
        self._validate_sms_credentials()
        
        try:
            # Import Twilio client here to handle optional dependency
            try:
                from twilio.rest import Client
                from twilio.base.exceptions import TwilioRestException
            except ImportError:
                raise SendError("Twilio library not installed. Run: pip install twilio")
            
            # Initialize Twilio client
            client = Client(self.config.SMS_ACCOUNT_SID, self.config.SMS_AUTH_TOKEN)
            
            # Format message (truncate if needed)
            full_message = message[:self.config.SMS_MAX_LENGTH]
            
            # Send SMS
            twilio_message = client.messages.create(
                body=full_message,
                from_=self.config.SMS_FROM_NUMBER,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully. SID: {twilio_message.sid}")
            
            return {
                "success": True,
                "message": f"SMS sent successfully (SID: {twilio_message.sid})",
                "channel": "sms",
                "details": {
                    "sid": twilio_message.sid,
                    "status": twilio_message.status,
                    "to": to_number
                }
            }
            
        except CredentialError:
            raise
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            raise SendError(f"Failed to send SMS: {str(e)}")
    
    # =========================================================================
    # WhatsApp Channel (Twilio WhatsApp Business API)
    # =========================================================================
    
    def send_whatsapp(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp notification via Twilio WhatsApp Business API.
        
        Args:
            to_number: Recipient phone number (E.164 format, e.g., +1234567890).
            message: Message content to send.
            
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            CredentialError: If required credentials are missing.
            SendError: If sending fails.
        """
        logger.info(f"Sending WhatsApp to {to_number}")
        
        # Validate credentials
        self._validate_whatsapp_credentials()
        
        try:
            try:
                from twilio.rest import Client
            except ImportError:
                raise SendError("Twilio library not installed. Run: pip install twilio")
            
            # Initialize Twilio client
            client = Client(self.config.WHATSAPP_ACCOUNT_SID, self.config.WHATSAPP_AUTH_TOKEN)
            
            # Format number as WhatsApp format
            formatted_to = self._format_whatsapp_number(to_number)
            formatted_from = self._format_whatsapp_number(self.config.WHATSAPP_FROM_NUMBER)
            
            # Truncate message if needed
            full_message = message[:self.config.WHATSAPP_MAX_LENGTH]
            
            # Send WhatsApp message
            twilio_message = client.messages.create(
                body=full_message,
                from_=formatted_from,
                to=formatted_to
            )
            
            logger.info(f"WhatsApp sent successfully. SID: {twilio_message.sid}")
            
            return {
                "success": True,
                "message": f"WhatsApp sent successfully (SID: {twilio_message.sid})",
                "channel": "whatsapp",
                "details": {
                    "sid": twilio_message.sid,
                    "status": twilio_message.status,
                    "to": to_number
                }
            }
            
        except CredentialError:
            raise
        except Exception as e:
            logger.error(f"Failed to send WhatsApp: {str(e)}")
            raise SendError(f"Failed to send WhatsApp: {str(e)}")
    
    def _format_whatsapp_number(self, number: str) -> str:
        """
        Format phone number for WhatsApp API.
        
        Args:
            number: Phone number in E.164 format.
            
        Returns:
            Formatted number with whatsapp: prefix.
        """
        if number.startswith("whatsapp:"):
            return number
        return f"whatsapp:{number}"
    
    # =========================================================================
    # Telegram Channel
    # =========================================================================
    
    def send_telegram(self, chat_id: str, message: str) -> Dict[str, Any]:
        """
        Send Telegram message via Bot API.
        
        Args:
            chat_id: Recipient Telegram chat ID.
            message: Message content to send.
            
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            CredentialError: If required credentials are missing.
            SendError: If sending fails.
        """
        logger.info(f"Sending Telegram to chat_id: {chat_id}")
        
        # Validate credentials
        self._validate_telegram_credentials()
        
        try:
            # Prepare API URL
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            
            # Prepare payload
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            # Send request
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.WEBHOOK_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("ok"):
                logger.info(f"Telegram message sent successfully to chat_id: {chat_id}")
                return {
                    "success": True,
                    "message": "Telegram message sent successfully",
                    "channel": "telegram",
                    "details": {
                        "message_id": result.get("result", {}).get("message_id"),
                        "chat_id": chat_id
                    }
                }
            else:
                raise SendError(f"Telegram API error: {result.get('description')}")
            
        except CredentialError:
            raise
        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram: {str(e)}")
            raise SendError(f"Failed to send Telegram: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to send Telegram: {str(e)}")
            raise SendError(f"Failed to send Telegram: {str(e)}")
    
    # =========================================================================
    # Email Channel (SMTP)
    # =========================================================================
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> Dict[str, Any]:
        """
        Send Email notification via SMTP.
        
        Args:
            to_email: Recipient email address.
            subject: Email subject.
            body: Email body content.
            is_html: Whether body contains HTML content.
            
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            CredentialError: If required credentials are missing.
            SendError: If sending fails.
        """
        logger.info(f"Sending Email to {to_email}")
        
        # Validate credentials
        self._validate_email_credentials()
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.SMTP_FROM_EMAIL or self.config.SMTP_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(
                self.config.SMTP_HOST,
                self.config.SMTP_PORT
            ) as server:
                if self.config.SMTP_USE_TLS:
                    server.starttls()
                
                server.login(
                    self.config.SMTP_USERNAME,
                    self.config.SMTP_PASSWORD
                )
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}",
                "channel": "email",
                "details": {
                    "to": to_email,
                    "subject": subject
                }
            }
            
        except CredentialError:
            raise
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send Email (SMTP error): {str(e)}")
            raise SendError(f"Failed to send Email: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to send Email: {str(e)}")
            raise SendError(f"Failed to send Email: {str(e)}")
    
    # =========================================================================
    # Webhook Channel
    # =========================================================================
    
    def send_webhook(self, payload: Dict[str, Any], webhook_url: str = None) -> Dict[str, Any]:
        """
        Send Webhook notification via HTTP POST.
        
        Args:
            payload: Dictionary payload to send as JSON.
            webhook_url: Optional custom webhook URL. If not provided, uses config URL.
            
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            CredentialError: If required credentials are missing.
            SendError: If sending fails.
        """
        target_url = webhook_url or self.config.WEBHOOK_URL
        
        logger.info(f"Sending Webhook to {target_url}")
        
        # Validate credentials
        if not target_url:
            raise CredentialError("Missing Webhook URL: WEBHOOK_URL or webhook_url parameter")
        
        try:
            # Add timestamp to payload
            payload_with_timestamp = {
                **payload,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "notification_service": "unified-notification-service"
            }
            
            # Send request
            response = requests.post(
                target_url,
                json=payload_with_timestamp,
                timeout=self.config.WEBHOOK_TIMEOUT,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            
            logger.info(f"Webhook sent successfully to {target_url}")
            
            return {
                "success": True,
                "message": f"Webhook sent successfully to {target_url}",
                "channel": "webhook",
                "details": {
                    "url": target_url,
                    "status_code": response.status_code
                }
            }
            
        except CredentialError:
            raise
        except requests.Timeout:
            logger.error(f"Webhook request timed out: {target_url}")
            raise SendError(f"Webhook request timed out after {self.config.WEBHOOK_TIMEOUT} seconds")
        except requests.RequestException as e:
            logger.error(f"Failed to send Webhook: {str(e)}")
            raise SendError(f"Failed to send Webhook: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to send Webhook: {str(e)}")
            raise SendError(f"Failed to send Webhook: {str(e)}")
    
    # =========================================================================
    # In-App Notification Channel
    # =========================================================================
    
    def create_in_app_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Create in-app notification stored in database.
        
        Args:
            user_id: User ID to notify.
            title: Notification title.
            message: Notification message.
            db_session: Optional database session. If not provided, uses default connection.
            
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            SendError: If creating notification fails.
        """
        logger.info(f"Creating in-app notification for user_id: {user_id}")
        
        try:
            # Try to import and use SQLAlchemy if available
            try:
                from sqlalchemy.orm import Session
                from app.database import engine, Base
                from app.models import Notification
                
                # Create notification record
                notification = Notification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    title=title,
                    message=message,
                    created_at=datetime.utcnow(),
                    is_read=False
                )
                
                # Use provided session or create new one
                if db_session:
                    db_session.add(notification)
                    db_session.commit()
                else:
                    from sqlalchemy.orm import sessionmaker
                    SessionLocal = sessionmaker(bind=engine)
                    session = SessionLocal()
                    try:
                        session.add(notification)
                        session.commit()
                    finally:
                        session.close()
                
                logger.info(f"In-app notification created for user_id: {user_id}")
                
                return {
                    "success": True,
                    "message": "In-app notification created successfully",
                    "channel": "in_app",
                    "details": {
                        "notification_id": notification.id,
                        "user_id": user_id,
                        "title": title
                    }
                }
                
            except ImportError:
                # Fallback: create notification without database
                notification_id = str(uuid.uuid4())
                logger.info(f"In-app notification created (no database): {notification_id}")
                
                return {
                    "success": True,
                    "message": "In-app notification created successfully",
                    "channel": "in_app",
                    "details": {
                        "notification_id": notification_id,
                        "user_id": user_id,
                        "title": title,
                        "note": "No database connection - notification not persisted"
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to create in-app notification: {str(e)}")
            raise SendError(f"Failed to create in-app notification: {str(e)}")
    
    # =========================================================================
    # Central Notification Method
    # =========================================================================
    
    def send_notification(
        self,
        channel: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send notification via specified channel.
        
        This is the central method for sending notifications. It validates
        credentials and routes to the appropriate channel handler.
        
        Args:
            channel: Notification channel (sms, whatsapp, telegram, email, webhook, in_app).
            **kwargs: Channel-specific arguments:
                - sms: to_number, message
                - whatsapp: to_number, message
                - telegram: chat_id, message
                - email: to_email, subject, body, is_html (optional)
                - webhook: payload, webhook_url (optional)
                - in_app: user_id, title, message, db_session (optional)
                
        Returns:
            Dict with success status, message, and channel.
            
        Raises:
            ChannelNotSupportedError: If channel is not supported.
            CredentialError: If required credentials are missing.
            SendError: If sending fails.
        """
        logger.info(f"Sending notification via {channel}")
        
        # Validate channel and credentials
        try:
            self._validate_channel(channel)
        except (ChannelNotSupportedError, CredentialError) as e:
            logger.error(f"Channel validation failed: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "channel": channel.lower()
            }
        
        # Route to appropriate channel handler
        try:
            if channel.lower() == "sms":
                return self.send_sms(
                    to_number=kwargs.get("to_number", ""),
                    message=kwargs.get("message", "")
                )
            
            elif channel.lower() == "whatsapp":
                return self.send_whatsapp(
                    to_number=kwargs.get("to_number", ""),
                    message=kwargs.get("message", "")
                )
            
            elif channel.lower() == "telegram":
                return self.send_telegram(
                    chat_id=kwargs.get("chat_id", ""),
                    message=kwargs.get("message", "")
                )
            
            elif channel.lower() == "email":
                return self.send_email(
                    to_email=kwargs.get("to_email", ""),
                    subject=kwargs.get("subject", ""),
                    body=kwargs.get("body", ""),
                    is_html=kwargs.get("is_html", False)
                )
            
            elif channel.lower() == "webhook":
                return self.send_webhook(
                    payload=kwargs.get("payload", {}),
                    webhook_url=kwargs.get("webhook_url")
                )
            
            elif channel.lower() == "in_app":
                return self.create_in_app_notification(
                    user_id=kwargs.get("user_id"),
                    title=kwargs.get("title", ""),
                    message=kwargs.get("message", ""),
                    db_session=kwargs.get("db_session")
                )
            
            else:
                # This should never happen due to validation above
                return {
                    "success": False,
                    "message": f"Channel '{channel}' not implemented",
                    "channel": channel.lower()
                }
                
        except (CredentialError, SendError) as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "channel": channel.lower()
            }
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
                "channel": channel.lower()
            }
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_available_channels(self) -> Dict[str, bool]:
        """
        Get list of available channels based on configured credentials.
        
        Returns:
            Dict mapping channel names to availability status.
        """
        channels = {}
        
        for channel in self._channel_credentials:
            try:
                validator = self._channel_credentials[channel]
                validator()
                channels[channel] = True
            except CredentialError:
                channels[channel] = False
            except Exception:
                channels[channel] = False
        
        return channels
    
    def validate_all_credentials(self) -> Dict[str, bool]:
        """
        Validate credentials for all channels.
        
        Returns:
            Dict mapping channel names to validation status.
        """
        return self.get_available_channels()


# =============================================================================
# SQLAlchemy Model for In-App Notifications
# =============================================================================

# Note: If SQLAlchemy is available, you can use this model directly.
# Otherwise, the create_in_app_notification method will handle it automatically.

IN_APP_NOTIFICATION_MODEL = """
# SQLAlchemy model for in-app notifications
# Add this to your models.py if using SQLAlchemy

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
"""


# =============================================================================
# Singleton Instance
# =============================================================================

# Create singleton instance for easy import
notification_service = NotificationService()


# =============================================================================
# Convenience Functions
# =============================================================================

def send_notification(channel: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to send notification.
    
    Args:
        channel: Notification channel.
        **kwargs: Channel-specific arguments.
        
    Returns:
        Dict with success status, message, and channel.
    """
    return notification_service.send_notification(channel, **kwargs)


def get_available_channels() -> Dict[str, bool]:
    """Get available notification channels."""
    return notification_service.get_available_channels()
