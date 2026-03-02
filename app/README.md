# Rule Engine API

A FastAPI-based Rule Engine for monitoring, evaluating rules, and sending multi-channel notifications.

---

## Features

- **Rule Management** - Create, update, delete rules with conditions
- **Rule Evaluation** - Evaluate data against rules (SIMPLE, AND, OR conditions)
- **Multi-Channel Notifications** - Send via Email, SMS, WhatsApp, Telegram, Webhook, In-App
- **Parallel Execution** - Notifications sent concurrently to all channels
- **Debounce Mechanism** - Prevent repeated alerts within time window
- **Retry Mechanism** - Automatic retry for failed notifications
- **Rule State Tracking** - Track Triggered/Not Triggered state
- **Event Logging** - Detailed logs for each notification attempt

---

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
Update the `.env` file with your database credentials:
```env
DB_HOST=factory-ops.cmt486yymn9w.us-east-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=Ruleengine
DB_NAME=factory
```

### 3. Run
```bash
python app/main.py
```

### 4. Open API Docs
Visit: http://localhost:8000/docs

---

## API Endpoints

### Rules
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rules` | Get all rules |
| GET | `/api/rules/{id}` | Get rule by ID |
| POST | `/api/rules` | Create new rule |
| PUT | `/api/rules/{id}` | Update rule |
| DELETE | `/api/rules/{id}` | Delete rule |

### Rule Evaluation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rules/evaluate` | Evaluate data against all rules |
| POST | `/api/rules/evaluate/{id}` | Evaluate against specific rule |
| POST | `/api/rules/trigger-now` | Manually trigger a rule |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | Get all notifications |
| GET | `/api/notifications/pending` | Get pending notifications |
| POST | `/api/notifications/trigger` | Trigger a notification |
| POST | `/api/notifications/trigger-multi` | Trigger multi-channel notification |
| POST | `/api/notifications/process` | Process pending notifications |
| GET | `/api/notifications/by-channel/{channel}` | Get by channel |

### Notification Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/settings` | Get all settings |
| POST | `/api/notifications/settings` | Create settings |
| PUT | `/api/notifications/settings/{id}` | Update settings |
| DELETE | `/api/notifications/settings/{id}` | Delete settings |
| GET | `/api/notifications/settings/rule/{rule_id}` | Get settings by rule |

---

## Condition Types

### Simple (Single Condition)
```json
{
  "condition": "temperature > 95",
  "condition_type": "SIMPLE"
}
```

### AND (Multiple Conditions - All Must Match)
```json
{
  "condition": "temperature > 95 AND humidity < 80",
  "condition_type": "AND"
}
```

### OR (Multiple Conditions - Any Must Match)
```json
{
  "condition": "status == 'error' OR temperature > 100",
  "condition_type": "OR"
}
```

---

## Supported Channels

- **EMAIL** - Email notifications via SMTP
- **SMS** - Text messages via SMS provider
- **WHATSAPP** - WhatsApp messages via WhatsApp API
- **TELEGRAM** - Telegram bot messages
- **WEBHOOK** - HTTP POST to custom URL
- **INAPP** - In-app notifications (stored in database)

---

## How It Works

### 1. Create a Rule
```json
POST /api/rules
{
  "name": "High Temperature Alert",
  "condition": "temperature > 95",
  "condition_type": "SIMPLE",
  "debounce_seconds": 60,
  "retry_enabled": true
}
```

### 2. Set Notification Settings
```json
POST /api/notifications/settings
{
  "rule_id": "<RULE_ID>",
  "notification_type": "ALERT",
  "recipient_email": "user@example.com",
  "recipient_phone": "1234567890"
}
```

### 3. Evaluate Data
```json
POST /api/rules/evaluate
{
  "temperature": 96
}
```

System will:
- Evaluate condition (`96 > 95` = TRUE)
- Send notifications to ALL configured channels in parallel
- Log each notification attempt
- Update rule state to "TRIGGERED"

---

## Debounce & Retry

### Debounce
Prevents repeated alerts within a time window:
- Set `debounce_seconds` in rule (default: 60)
- If rule triggered again within window, it's skipped

### Retry
Automatic retry for failed notifications:
- Set `retry_enabled: true` in rule
- Configure `retry_max_attempts` (default: 3)
- Configure `retry_interval_seconds` (default: 30)

---

## Project Structure

```
.
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── config/                 # Database config
├── app/
│   ├── main.py            # Application entry point
│   ├── models.py          # Database queries (loaded from sql/)
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database connection
│   ├── sql_utils.py       # SQL loader utility
│   ├── sql/               # External SQL files
│   │   ├── schema.sql    # Table definitions
│   │   └── queries.sql   # CRUD queries
│   ├── routes/
│   │   ├── rules.py
│   │   ├── notifications.py
│   │   ├── rule_evaluation_service.py
│   │   └── ...
│   └── services/
│       ├── notification_service.py
│       ├── notification_dispatcher.py
│       └── rule_evaluator.py
```

---

## Database Tables

Automatically created on startup:
- **rules** - Rule definitions with conditions
- **rule_actions** - Actions when rules trigger
- **rule_evaluations** - Evaluation results
- **rule_triggers** - Trigger configurations
- **notifications** - Notification records
- **notification_settings** - User preferences
- **rule_events** - Event tracking for deduplication
- **notification_logs** - Detailed notification logs

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| DB_HOST | Database host |
| DB_USER | Database user |
| DB_PASSWORD | Database password |
| DB_NAME | Database name |

---

## API Documentation

Full interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## License

MIT
