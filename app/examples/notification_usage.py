"""
Notification Service Usage Examples

This file demonstrates how to use the Unified Notification Service
in various scenarios.

Prerequisites:
    1. Copy .env.example to .env and configure your credentials
    2. Install dependencies: pip install -r requirements.txt

Run these examples:
    python -m app.examples.notification_usage
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.notification_service import (
    NotificationService,
    send_notification,
    get_available_channels
)


def example_send_sms():
    """Example: Send SMS notification"""
    print("\n" + "="*60)
    print("Example: Sending SMS")
    print("="*60)
    
    service = NotificationService()
    
    result = service.send_notification(
        "sms",
        to_number="+1234567890",
        message="Hello! This is a test SMS notification."
    )
    
    print(f"Result: {result}")
    return result


def example_send_whatsapp():
    """Example: Send WhatsApp notification"""
    print("\n" + "="*60)
    print("Example: Sending WhatsApp")
    print("="*60)
    
    service = NotificationService()
    
    result = service.send_notification(
        "whatsapp",
        to_number="+1234567890",
        message="Hello! This is a test WhatsApp message."
    )
    
    print(f"Result: {result}")
    return result


def example_send_telegram():
    """Example: Send Telegram message"""
    print("\n" + "="*60)
    print("Example: Sending Telegram")
    print("="*60)
    
    service = NotificationService()
    
    result = service.send_notification(
        "telegram",
        chat_id="123456789",
        message="*Hello!*\nThis is a test Telegram message."
    )
    
    print(f"Result: {result}")
    return result


def example_send_email():
    """Example: Send Email notification"""
    print("\n" + "="*60)
    print("Example: Sending Email")
    print("="*60)
    
    service = NotificationService()
    
    result = service.send_notification(
        "email",
        to_email="user@example.com",
        subject="Test Notification",
        body="This is a test email notification.\n\nBest regards,\nNotification Service"
    )
    
    print(f"Result: {result}")
    return result


def example_send_html_email():
    """Example: Send HTML Email notification"""
    print("\n" + "="*60)
    print("Example: Sending HTML Email")
    print("="*60)
    
    service = NotificationService()
    
    html_body = """
    <html>
        <body>
            <h2>Test Notification</h2>
            <p>This is an <strong>HTML</strong> email notification.</p>
            <hr>
            <p><small>Sent via Notification Service</small></p>
        </body>
    </html>
    """
    
    result = service.send_email(
        to_email="user@example.com",
        subject="Test HTML Email",
        body=html_body,
        is_html=True
    )
    
    print(f"Result: {result}")
    return result


def example_send_webhook():
    """Example: Send Webhook notification"""
    print("\n" + "="*60)
    print("Example: Sending Webhook")
    print("="*60)
    
    service = NotificationService()
    
    payload = {
        "event": "notification",
        "data": {
            "title": "Test Webhook",
            "message": "This is a test webhook notification",
            "user_id": 123
        }
    }
    
    result = service.send_webhook(payload=payload)
    
    print(f"Result: {result}")
    return result


def example_send_custom_webhook():
    """Example: Send Webhook to custom URL"""
    print("\n" + "="*60)
    print("Example: Sending Custom Webhook")
    print("="*60)
    
    service = NotificationService()
    
    payload = {
        "event": "custom_event",
        "data": {
            "message": "Custom webhook payload"
        }
    }
    
    # Override default webhook URL
    result = service.send_webhook(
        payload=payload,
        webhook_url="https://example.com/my-webhook"
    )
    
    print(f"Result: {result}")
    return result


def example_create_in_app_notification():
    """Example: Create in-app notification"""
    print("\n" + "="*60)
    print("Example: Creating In-App Notification")
    print("="*60)
    
    service = NotificationService()
    
    result = service.send_notification(
        "in_app",
        user_id=1,
        title="Test Notification",
        message="This is a test in-app notification."
    )
    
    print(f"Result: {result}")
    return result


def example_check_available_channels():
    """Example: Check which channels are available"""
    print("\n" + "="*60)
    print("Example: Checking Available Channels")
    print("="*60)
    
    service = NotificationService()
    channels = service.get_available_channels()
    
    print("Available channels:")
    for channel, available in channels.items():
        status = "✓ Available" if available else "✗ Not configured"
        print(f"  {channel}: {status}")
    
    return channels


def example_use_convenience_function():
    """Example: Use convenience function"""
    print("\n" + "="*60)
    print("Example: Using Convenience Function")
    print("="*60)
    
    # Using the module-level convenience function
    result = send_notification(
        "sms",
        to_number="+1234567890",
        message="Hello from convenience function!"
    )
    
    print(f"Result: {result}")
    return result


def example_advanced_usage():
    """Example: Advanced usage with custom configuration"""
    print("\n" + "="*60)
    print("Example: Advanced Usage with Custom Config")
    print("="*60)
    
    from app.services.notification_service import NotificationConfig
    
    # Create custom configuration
    custom_config = NotificationConfig()
    custom_config.SMS_ACCOUNT_SID = os.getenv("CUSTOM_SMS_ACCOUNT_SID", "")
    custom_config.SMS_AUTH_TOKEN = os.getenv("CUSTOM_SMS_AUTH_TOKEN", "")
    custom_config.SMS_FROM_NUMBER = os.getenv("CUSTOM_SMS_FROM_NUMBER", "")
    
    # Use custom configuration
    service = NotificationService(config=custom_config)
    
    # Check available channels with custom config
    channels = service.get_available_channels()
    print(f"Available channels with custom config: {channels}")
    
    return channels


def example_error_handling():
    """Example: Proper error handling"""
    print("\n" + "="*60)
    print("Example: Error Handling")
    print("="*60)
    
    service = NotificationService()
    
    # Try to send SMS without credentials (will fail gracefully)
    result = service.send_notification(
        "sms",
        to_number="+1234567890",
        message="Test message"
    )
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    
    return result


def example_multi_channel():
    """Example: Send to multiple channels"""
    print("\n" + "="*60)
    print("Example: Multi-Channel Notification")
    print("="*60)
    
    service = NotificationService()
    
    # Define channels to notify
    channels = ["email", "in_app"]
    
    results = []
    for channel in channels:
        try:
            if channel == "email":
                result = service.send_notification(
                    channel,
                    to_email="user@example.com",
                    subject="Multi-channel Test",
                    body="This message is sent via multiple channels."
                )
            elif channel == "in_app":
                result = service.send_notification(
                    channel,
                    user_id=1,
                    title="Multi-channel Test",
                    message="This message is sent via multiple channels."
                )
            
            results.append(result)
            print(f"{channel}: {result.get('success')}")
            
        except Exception as e:
            print(f"{channel} error: {e}")
            results.append({"channel": channel, "success": False, "error": str(e)})
    
    return results


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Notification Service - Usage Examples")
    print("="*60)
    
    # Check available channels first
    example_check_available_channels()
    
    # Run examples (uncomment to test each):
    # SMS, WhatsApp, Telegram, Email, Webhook, In-App, etc.
    
    print("\n" + "="*60)
    print("Examples complete! Uncomment examples to test them.")
    print("="*60)
