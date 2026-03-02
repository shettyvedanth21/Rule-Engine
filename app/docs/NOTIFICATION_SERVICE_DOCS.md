# Unified Notification Service - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Libraries Used](#libraries-used)
4. [File Structure](#file-structure)
5. [API Endpoints](#api-endpoints)
6. [Working Flow](#working-flow)
7. [Class Diagram](#class-diagram)

---

## Overview

The Unified Notification Service is a production-ready backend service that supports multiple notification channels through a single interface. It provides a clean, modular architecture with proper error handling, logging, and credential validation.

### Supported Channels
1. **SMS** - Twilio SMS API
2. **WhatsApp** - Twilio WhatsApp Business API  
3. **Telegram** - Telegram Bot API
4. **Email** - SMTP Protocol
5. **Webhook** - HTTP POST to any REST endpoint
6. **In-App** - Database storage

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NotificationService                       │
│                  (Main Entry Point)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│   SMS API    │ │ WhatsApp │ │   Telegram   │
│   (Twilio)   │ │  (Twilio)│ │    Bot API   │
└──────────────┘ └──────────┘ └──────────────┘

        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│    Email     │ │  Webhook │ │   Database   │
│   (SMTP)     │ │ (HTTP)   │ │   (In-App)   │
└──────────────┘ └──────────┘ └──────────────┘
```

---

## Libraries Used

### 1. **Twilio Library**
```python
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
```
- **Purpose:** Send SMS and WhatsApp messages via Twilio
- **Installation:** `pip install twilio`
- **Version:** Latest from PyPI

**How it works:**
```python
# Initialize client with credentials
client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)

# Send SMS
message = client.messages.create(
    body="Hello!",
    from_=SMS_FROM_NUMBER,
    to="+1234567890"
)
```

---

### 2. **Requests Library**
```python
import requests
```
- **Purpose:** HTTP requests for Telegram Bot API and Webhooks
- **Installation:** `pip install requests`
- **Version:** Latest from PyPI

**How it works (Telegram):**
```python
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": "123456789",
    "text": "Hello!",
    "parse_mode": "Markdown"
}
response = requests.post(url, json=payload, timeout=30)
response.raise_for_status()
```

**How it works (Webhook):**
```python
response = requests.post(
    webhook_url,
    json=payload,
    timeout=WEBHOOK_TIMEOUT,
    headers={"Content-Type": "application/json"}
)
response.raise_for_status()
```

---

### 3. **SMTPLib (Python Standard Library)**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
```
- **Purpose:** Send emails via SMTP protocol
- **Installation:** Built-in (no installation needed)

**How it works:**
```python
# Create email message
msg = MIMEMultipart('alternative')
msg['From'] = SMTP_FROM_EMAIL
msg['To'] = to_email
msg['Subject'] = subject

# Attach body
msg.attach(MIMEText(body, 'plain'))  # or 'html'

# Connect and send
with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    server.starttls()  # Enable TLS
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.send_message(msg)
```

---

### 4. **SQLAlchemy (Optional)**
```python
from sqlalchemy.orm import Session
```
- **Purpose:** Database operations for In-App notifications
- **Installation:** `pip install sqlalchemy`

**How it works:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()
notification = Notification(
    id=str(uuid.uuid4()),
    user_id=user_id,
    title=title,
    message=message,
    created_at=datetime.utcnow(),
    is_read=False
)
session.add(notification)
session.commit()
session.close()
```

---

### 5. **UUID (Python Standard Library)**
```python
import uuid
```
- **Purpose:** Generate unique IDs for notifications
- **Installation:** Built-in

---

### 6. **Datetime (Python Standard Library)**
```python
from datetime import datetime
```
- **Purpose:** Timestamp for notifications and logging

---

### 7. **Logging (Python Standard Library)**
```python
import logging
```
- **Purpose:** Application logging
- **Installation:** Built-in

---

### 8. **OS (Python Standard Library)**
```python
import os
```
- **Purpose:** Environment variable access

---

## File Structure

```
app/
├── services/
│   ├── __init__.py           # Package initialization
│   └── notification_service.py   # Main notification service
│
├── config.py                  # Application configuration
│
├── database.py               # Database connection
│
├── models.py                 # Database models & queries
│
├── .env.example              # Environment variables template
│
├── examples/
│   └── notification_usage.py # Usage examples
│
└── docs/
    └── NOTIFICATION_SERVICE_DOCS.md  # This documentation
```

---

## API Endpoints

### 1. Twilio SMS API
| Property | Value |
|----------|-------|
| Provider | Twilio |
| Endpoint | `https://api.twilio.com/2010-04-01/Accounts/{SID}/Messages` |
| Method | POST |
| Authentication | Account SID + Auth Token |
| Library | `twilio.rest.Client` |

**Request:**
```http
POST /2010-04-01/Accounts/ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/Messages
Authorization: Basic {base64(SID:AuthToken)}
Content-Type: application/x-www-form-urlencoded

Body:
To=+1234567890&From=+0987654321&Body=Hello
```

---

### 2. Twilio WhatsApp API
| Property | Value |
|----------|-------|
| Provider | Twilio |
| Endpoint | `https://api.twilio.com/2010-04-01/Accounts/{SID}/Messages` |
| Method | POST |
| Authentication | Account SID + Auth Token |
| Library | `twilio.rest.Client` |

**Request Format:**
- From: `whatsapp:+1234567890`
- To: `whatsapp:+0987654321`

---

### 3. Telegram Bot API
| Property | Value |
|----------|-------|
| Provider | Telegram |
| Endpoint | `https://api.telegram.org/bot{TOKEN}/sendMessage` |
| Method | POST |
| Authentication | Bot Token |
| Library | `requests` |

**Request:**
```http
POST https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/sendMessage
Content-Type: application/json

{
    "chat_id": "123456789",
    "text": "Hello!",
    "parse_mode": "Markdown"
}
```

---

### 4. SMTP Email
| Property | Value |
|----------|-------|
| Protocol | SMTP |
| Port | 587 (TLS) or 465 (SSL) |
| Authentication | Username + Password |
| Library | `smtplib` |

**Connection Flow:**
```
Client → Connect to SMTP Server:587 → STARTTLS → 
AUTH LOGIN → Username/Password → MAIL FROM → 
RCPT TO → DATA → Message Body → QUIT
```

---

### 5. Webhook HTTP POST
| Property | Value |
|----------|-------|
| Method | POST |
| Content-Type | application/json |
| Timeout | Configurable (default 30s) |
| Library | `requests` |

**Request:**
```http
POST {WEBHOOK_URL}
Content-Type: application/json

{
    "title": "Notification",
    "message": "Hello",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## Working Flow

### 1. Initialization
```python
# Create notification service instance
service = NotificationService()

# Or use convenience function
from app.services.notification_service import send_notification
```

### 2. Credential Validation
```python
def _validate_channel(self, channel):
    """Validates channel and checks credentials"""
    if channel not in ["sms", "whatsapp", "telegram", "email", "webhook", "in_app"]:
        raise ChannelNotSupportedError(...)
    
    # Call channel-specific validator
    validator = self._channel_credentials[channel]
    validator()  # Raises CredentialError if missing
```

### 3. Send Notification Flow
```python
def send_notification(channel, **kwargs):
    # Step 1: Validate channel
    self._validate_channel(channel)
    
    # Step 2: Route to appropriate handler
    if channel == "sms":
        return self.send_sms(to_number, message)
    elif channel == "whatsapp":
        return self.send_whatsapp(to_number, message)
    # ... etc
    
    # Step 3: Return structured response
    return {
        "success": True/False,
        "message": "...",
        "channel": channel
    }
```

### 4. SMS Sending Flow
```python
def send_sms(to_number, message):
    # 1. Validate credentials
    self._validate_sms_credentials()
    
    # 2. Import Twilio client
    from twilio.rest import Client
    
    # 3. Initialize client
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    # 4. Send message
    twilio_message = client.messages.create(
        body=message[:160],  # SMS max length
        from_=FROM_NUMBER,
        to=to_number
    )
    
    # 5. Return result
    return {"success": True, "message": f"SMS sent (SID: {twilio_message.sid})", "channel": "sms"}
```

### 5. In-App Notification Flow
```python
def create_in_app_notification(user_id, title, message, db_session):
    # 1. Try to use SQLAlchemy if available
    try:
        from app.database import engine
        from app.models import Notification
        
        # 2. Create notification object
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            created_at=datetime.utcnow(),
            is_read=False
        )
        
        # 3. Save to database
        db_session.add(notification)
        db_session.commit()
        
        return {"success": True, "message": "Notification created", "channel": "in_app"}
    
    # 4. Fallback if no database
    except ImportError:
        return {"success": True, "message": "Notification created (not persisted)", "channel": "in_app"}
```

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    NotificationService                        │
├─────────────────────────────────────────────────────────────┤
│ - config: NotificationConfig                                │
│ - _channel_credentials: Dict                                │
├─────────────────────────────────────────────────────────────┤
│ + __init__(config: NotificationConfig)                      │
│ + send_notification(channel: str, **kwargs) -> Dict         │
│ + send_sms(to_number: str, message: str) -> Dict           │
│ + send_whatsapp(to_number: str, message: str) -> Dict      │
│ + send_telegram(chat_id: str, message: str) -> Dict          │
│ + send_email(to_email, subject, body, is_html) -> Dict      │
│ + send_webhook(payload, webhook_url) -> Dict                 │
│ + create_in_app_notification(user_id, title, message) -> Dict│
│ + get_available_channels() -> Dict                           │
│ + _validate_channel(channel) -> None                        │
│ + _validate_sms_credentials() -> None                       │
│ + _validate_whatsapp_credentials() -> None                  │
│ + _validate_telegram_credentials() -> None                   │
│ + _validate_email_credentials() -> None                     │
│ + _validate_webhook_credentials() -> None                   │
│ + _format_whatsapp_number(number) -> str                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     NotificationConfig                         │
├─────────────────────────────────────────────────────────────┤
│ + SMS_ACCOUNT_SID: str                                       │
│ + SMS_AUTH_TOKEN: str                                        │
│ + SMS_FROM_NUMBER: str                                       │
│ + WHATSAPP_ACCOUNT_SID: str                                 │
│ + WHATSAPP_AUTH_TOKEN: str                                   │
│ + WHATSAPP_FROM_NUMBER: str                                  │
│ + TELEGRAM_BOT_TOKEN: str                                    │
│ + SMTP_HOST: str                                             │
│ + SMTP_PORT: int                                             │
│ + SMTP_USERNAME: str                                         │
│ + SMTP_PASSWORD: str                                         │
│ + SMTP_USE_TLS: bool                                         │
│ + WEBHOOK_URL: str                                           │
│ + WEBHOOK_TIMEOUT: int                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Response Format

All methods return a standardized response:

```python
{
    "success": True,           # Boolean indicating success
    "message": "SMS sent successfully (SID: SM...)",  # Status message
    "channel": "sms",         # Channel used
    "details": {              # Optional additional details
        "sid": "SM...",
        "status": "sent",
        "to": "+1234567890"
    }
}
```

---

## Error Handling

The service defines custom exceptions:

```python
class NotificationError(Exception):
    """Base exception for notification errors"""
    pass

class CredentialError(NotificationError):
    """Raised when required credentials are missing"""
    pass

class ChannelNotSupportedError(NotificationError):
    """Raised when notification channel is not supported"""
    pass

class SendError(NotificationError):
    """Raised when sending notification fails"""
    pass
```

---

## Installation Requirements

```bash
# Install required packages
pip install twilio
pip install requests
pip install sqlalchemy  # Optional, for database support
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# SMS
SMS_ACCOUNT_SID=your_sid
SMS_AUTH_TOKEN=your_token
SMS_FROM_NUMBER=+1234567890

# WhatsApp
WHATSAPP_ACCOUNT_SID=your_sid
WHATSAPP_AUTH_TOKEN=your_token
WHATSAPP_FROM_NUMBER=+1234567890

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password

# Webhook
WEBHOOK_URL=https://your-webhook.com
```
