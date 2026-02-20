# Table definitions for factory database

# rules table
RULES_TABLE = """
CREATE TABLE IF NOT EXISTS rules (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    condition LONGTEXT,
    condition_type VARCHAR(20) DEFAULT 'SIMPLE' COMMENT 'SIMPLE, AND, OR',
    is_active BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 0,
    state VARCHAR(20) DEFAULT 'NOT_TRIGGERED' COMMENT 'TRIGGERED, NOT_TRIGGERED',
    last_triggered_at TIMESTAMP NULL,
    debounce_seconds INT DEFAULT 60 COMMENT 'Debounce time in seconds',
    retry_enabled BOOLEAN DEFAULT TRUE,
    retry_max_attempts INT DEFAULT 3,
    retry_interval_seconds INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""

# rule_actions table
RULE_ACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS rule_actions (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    action_type VARCHAR(100) NOT NULL,
    action_config LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
)
"""

# rule_evaluations table
RULE_EVALUATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS rule_evaluations (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    evaluated_at TIMESTAMP NOT NULL,
    result BOOLEAN,
    details LONGTEXT,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
)
"""

# rule_triggers table
RULE_TRIGGERS_TABLE = """
CREATE TABLE IF NOT EXISTS rule_triggers (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    trigger_type VARCHAR(100) NOT NULL,
    trigger_config LONGTEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
)
"""

# rule_events table - tracks rule trigger events for deduplication
RULE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS rule_events (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    event_id VARCHAR(255) NOT NULL COMMENT 'Unique identifier for the trigger event',
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_snapshot LONGTEXT COMMENT 'JSON snapshot of data at trigger time',
    notification_status VARCHAR(50) DEFAULT 'PENDING' COMMENT 'PENDING, SENT, FAILED, PARTIAL',
    channels_notified LONGTEXT COMMENT 'JSON array of channels that were notified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE,
    UNIQUE KEY unique_event (rule_id, event_id)
)
"""

# notification_logs table - detailed logs for each notification attempt
NOTIFICATION_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS notification_logs (
    id CHAR(36) PRIMARY KEY,
    event_id CHAR(36),
    rule_id CHAR(36),
    notification_id CHAR(36),
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL COMMENT 'PENDING, SENT, FAILED, RETRYING',
    attempt_number INT DEFAULT 1,
    error_message TEXT,
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
)
"""

# notifications table
NOTIFICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS notifications (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'INFO',
    channel VARCHAR(20) NOT NULL COMMENT 'SMS, WHATSAPP, TELEGRAM, EMAIL, WEBHOOK',
    status VARCHAR(50) DEFAULT 'PENDING',
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    whatsapp_number VARCHAR(50),
    telegram_chat_id VARCHAR(50),
    webhook_url VARCHAR(500),
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    send_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP NULL,
    acknowledged_at TIMESTAMP NULL,
    acknowledged_by VARCHAR(255),
    escalation_level INT DEFAULT 0,
    next_escalation_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
)
"""

# notification_settings table
NOTIFICATION_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS notification_settings (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    notification_type VARCHAR(50) NOT NULL,
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    whatsapp_number VARCHAR(50),
    telegram_chat_id VARCHAR(50),
    webhook_url VARCHAR(500),
    push_token VARCHAR(255),
    send_interval_minutes INT DEFAULT 60,
    escalation_enabled BOOLEAN DEFAULT TRUE,
    escalation_interval_minutes INT DEFAULT 60,
    max_escalations INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
)
"""

# SQL queries for CRUD operations
RULES_QUERIES = {
    'get_all': "SELECT * FROM rules ORDER BY priority DESC, created_at DESC",
    'get_by_id': "SELECT * FROM rules WHERE id = %s",
    'get_active': "SELECT * FROM rules WHERE is_active = TRUE ORDER BY priority DESC",
    'get_by_state': "SELECT * FROM rules WHERE state = %s",
    'create': "INSERT INTO rules (id, name, description, `condition`, condition_type, is_active, priority, state, debounce_seconds, retry_enabled, retry_max_attempts, retry_interval_seconds) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    'update': "UPDATE rules SET name=%s, description=%s, `condition`=%s, condition_type=%s, is_active=%s, priority=%s, state=%s, debounce_seconds=%s, retry_enabled=%s, retry_max_attempts=%s, retry_interval_seconds=%s WHERE id=%s",
    'update_state': "UPDATE rules SET state=%s, last_triggered_at=NOW() WHERE id=%s",
    'delete': "DELETE FROM rules WHERE id = %s",
}

RULE_ACTIONS_QUERIES = {
    'get_all': "SELECT * FROM rule_actions ORDER BY created_at DESC",
    'get_by_id': "SELECT * FROM rule_actions WHERE id = %s",
    'get_by_rule_id': "SELECT * FROM rule_actions WHERE rule_id = %s",
    'create': "INSERT INTO rule_actions (id, rule_id, action_type, action_config) VALUES (%s, %s, %s, %s)",
    'update': "UPDATE rule_actions SET action_type=%s, action_config=%s WHERE id=%s",
    'delete': "DELETE FROM rule_actions WHERE id = %s",
}

RULE_EVALUATIONS_QUERIES = {
    'get_all': "SELECT * FROM rule_evaluations ORDER BY evaluated_at DESC",
    'get_by_id': "SELECT * FROM rule_evaluations WHERE id = %s",
    'get_by_rule_id': "SELECT * FROM rule_evaluations WHERE rule_id = %s ORDER BY evaluated_at DESC",
    'create': "INSERT INTO rule_evaluations (id, rule_id, evaluated_at, result, details) VALUES (%s, %s, NOW(), %s, %s)",
    'update': "UPDATE rule_evaluations SET result=%s, details=%s WHERE id=%s",
    'delete': "DELETE FROM rule_evaluations WHERE id = %s",
}

RULE_TRIGGERS_QUERIES = {
    'get_all': "SELECT * FROM rule_triggers ORDER BY created_at DESC",
    'get_by_id': "SELECT * FROM rule_triggers WHERE id = %s",
    'get_by_rule_id': "SELECT * FROM rule_triggers WHERE rule_id = %s ORDER BY created_at DESC",
    'create': "INSERT INTO rule_triggers (id, rule_id, trigger_type, trigger_config, is_active) VALUES (%s, %s, %s, %s, %s)",
    'update': "UPDATE rule_triggers SET trigger_type=%s, trigger_config=%s, is_active=%s WHERE id=%s",
    'delete': "DELETE FROM rule_triggers WHERE id = %s",
}

# Rule events queries - for tracking trigger events and deduplication
RULE_EVENTS_QUERIES = {
    'get_all': "SELECT * FROM rule_events ORDER BY triggered_at DESC",
    'get_by_id': "SELECT * FROM rule_events WHERE id = %s",
    'get_by_rule_id': "SELECT * FROM rule_events WHERE rule_id = %s ORDER BY triggered_at DESC",
    'get_by_event_id': "SELECT * FROM rule_events WHERE rule_id = %s AND event_id = %s",
    'get_pending': "SELECT * FROM rule_events WHERE notification_status = 'PENDING'",
    'get_recent': "SELECT * FROM rule_events WHERE rule_id = %s AND triggered_at > DATE_SUB(NOW(), INTERVAL %s SECOND)",
    'create': "INSERT INTO rule_events (id, rule_id, event_id, data_snapshot, notification_status, channels_notified) VALUES (%s, %s, %s, %s, %s, %s)",
    'update_status': "UPDATE rule_events SET notification_status=%s, channels_notified=%s WHERE id=%s",
    'delete': "DELETE FROM rule_events WHERE id = %s",
}

# Notification logs queries
NOTIFICATION_LOGS_QUERIES = {
    'get_all': "SELECT * FROM notification_logs ORDER BY created_at DESC",
    'get_by_id': "SELECT * FROM notification_logs WHERE id = %s",
    'get_by_event_id': "SELECT * FROM notification_logs WHERE event_id = %s",
    'get_by_rule_id': "SELECT * FROM notification_logs WHERE rule_id = %s ORDER BY created_at DESC",
    'get_failed': "SELECT * FROM notification_logs WHERE status = 'FAILED' AND attempt_number < %s",
    'create': "INSERT INTO notification_logs (id, event_id, rule_id, notification_id, channel, status, attempt_number, error_message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
    'update_status': "UPDATE notification_logs SET status=%s, sent_at=NOW(), error_message=%s, attempt_number=%s WHERE id=%s",
}

# Notification queries
NOTIFICATIONS_QUERIES = {
    'get_all': "SELECT * FROM notifications ORDER BY triggered_at DESC",
    'get_by_id': "SELECT * FROM notifications WHERE id = %s",
    'get_by_rule_id': "SELECT * FROM notifications WHERE rule_id = %s ORDER BY triggered_at DESC",
    'get_by_channel': "SELECT * FROM notifications WHERE channel = %s ORDER BY triggered_at DESC",
    'get_pending': "SELECT * FROM notifications WHERE status = 'PENDING' AND send_at <= NOW()",
    'get_pending_by_channel': "SELECT * FROM notifications WHERE status = 'PENDING' AND send_at <= NOW() AND channel = %s",
    'get_escalations': "SELECT * FROM notifications WHERE status = 'SENT' AND acknowledged_at IS NULL AND next_escalation_at IS NOT NULL AND next_escalation_at <= NOW()",
    'create': "INSERT INTO notifications (id, rule_id, title, message, notification_type, channel, status, priority, recipient_email, recipient_phone, whatsapp_number, telegram_chat_id, webhook_url, send_at, escalation_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    'update_status': "UPDATE notifications SET status=%s, sent_at=NOW() WHERE id=%s",
    'acknowledge': "UPDATE notifications SET status='ACKNOWLEDGED', acknowledged_at=NOW(), acknowledged_by=%s WHERE id=%s",
    'escalate': "UPDATE notifications SET escalation_level=%s, next_escalation_at=%s, status='PENDING', send_at=%s WHERE id=%s",
}

NOTIFICATION_SETTINGS_QUERIES = {
    'get_all': "SELECT * FROM notification_settings WHERE is_active = TRUE",
    'get_by_id': "SELECT * FROM notification_settings WHERE id = %s",
    'get_by_rule_id': "SELECT * FROM notification_settings WHERE rule_id = %s AND is_active = TRUE",
    'get_by_channel': "SELECT * FROM notification_settings WHERE rule_id = %s AND notification_type = %s AND is_active = TRUE",
    'create': "INSERT INTO notification_settings (id, rule_id, notification_type, recipient_email, recipient_phone, whatsapp_number, telegram_chat_id, webhook_url, send_interval_minutes, escalation_enabled, escalation_interval_minutes, max_escalations, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    'update': "UPDATE notification_settings SET notification_type=%s, recipient_email=%s, recipient_phone=%s, whatsapp_number=%s, telegram_chat_id=%s, webhook_url=%s, send_interval_minutes=%s, escalation_enabled=%s, escalation_interval_minutes=%s, max_escalations=%s, is_active=%s WHERE id=%s",
    'delete': "UPDATE notification_settings SET is_active=FALSE WHERE id=%s",
}
