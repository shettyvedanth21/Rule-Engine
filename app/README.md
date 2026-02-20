# Rule Engine API

A FastAPI-based Rule Engine for monitoring, evaluating IoT device rules, and sending notifications with escalation support.

---

## Features

- **Rule Management** - Create, update, delete rules
- **Rule Actions** - Define actions when rules trigger
- **Rule Evaluations** - Store evaluation results
- **Rule Triggers** - Track triggered events
- **Notifications** - Send alerts via Email, SMS, WhatsApp, Push
- **Escalation** - Automatic escalation if alerts are not acknowledged

---

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Configure
Update the `.env` file with your database credentials:
```env
DB_HOST=your-mysql-host
DB_USER=admin
DB_PASSWORD=yourpassword
DB_NAME=factory
```

### 3. Run
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
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

### Rule Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rule-actions` | Get all actions |
| POST | `/api/rule-actions` | Create action |

### Rule Evaluations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rule-evaluations` | Get all evaluations |
| POST | `/api/rule-evaluations` | Create evaluation |

### Rule Triggers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rule-triggers` | Get all triggers |
| POST | `/api/rule-triggers` | Create trigger |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | Get all notifications |
| GET | `/api/notifications/pending` | Get pending notifications |
| POST | `/api/notifications/trigger` | Trigger a notification |
| POST | `/api/notifications/process` | Process notifications & escalations |
| PUT | `/api/notifications/{id}/acknowledge` | Acknowledge notification |

### Notification Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/settings` | Get all settings |
| POST | `/api/notifications/settings` | Create settings |
| PUT | `/api/notifications/settings/{id}` | Update settings |

---

## Notification Methods

Users can select their preferred notification method:
- **EMAIL** - Email notifications
- **SMS** - SMS via phone
- **WHATSAPP** - WhatsApp messages
- **PUSH** - Push notifications (FCM)

---

## Escalation

When a rule triggers:
1. Notification created with status `PENDING`
2. Processed → status `SENT`
3. If not acknowledged within escalation time → auto-escalate
4. Repeats up to max_escalations times

### Settings:
- `send_interval_minutes` - How often to send
- `escalation_enabled` - Enable escalation
- `escalation_interval_minutes` - Time before escalating
- `max_escalations` - Maximum escalation levels

---

## Scheduler Setup

To process notifications automatically, call this endpoint periodically:

```bash
# Every minute (Linux/Mac)
* * * * * curl -X POST http://localhost:8000/api/notifications/process
```

---

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── database.py          # Database connection
│   ├── main.py             # Application entry point
│   ├── models.py           # Database models & queries
│   ├── schemas.py          # Pydantic schemas
│   └── routes/
│       ├── __init__.py
│       ├── rules.py
│       ├── rule_actions.py
│       ├── rule_evaluations.py
│       ├── rule_triggers.py
│       └── notifications.py
├── config.py                # Configuration
├── requirements.txt          # Dependencies
├── .env                    # Environment variables
└── README.md
```

---

## Database

The application uses MySQL. Tables are created automatically:
- **rules** - Rule definitions
- **rule_actions** - Actions when rules trigger
- **rule_evaluations** - Evaluation results
- **rule_triggers** - Triggered events
- **notifications** - Notification records with timestamps
- **notification_settings** - User notification preferences

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | localhost | Database host |
| DB_USER | root | Database user |
| DB_PASSWORD | (empty) | Database password |
| DB_NAME | factory | Database name |
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |

---

## API Documentation

Full interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## License

MIT
