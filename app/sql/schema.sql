-- Database Schema for Rule Engine API
-- This file contains all table definitions

-- Rules table
CREATE TABLE IF NOT EXISTS rules (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    `condition` LONGTEXT,
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
);

-- Rule Actions table
CREATE TABLE IF NOT EXISTS rule_actions (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    action_type VARCHAR(100) NOT NULL,
    action_config LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
);

-- Rule Evaluations table
CREATE TABLE IF NOT EXISTS rule_evaluations (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    evaluated_at TIMESTAMP NOT NULL,
    result BOOLEAN,
    details LONGTEXT,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
);

-- Rule Triggers table
CREATE TABLE IF NOT EXISTS rule_triggers (
    id CHAR(36) PRIMARY KEY,
    rule_id CHAR(36),
    trigger_type VARCHAR(100) NOT NULL,
    trigger_config LONGTEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
);

-- Rule Events table - tracks rule trigger events for deduplication
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
);

-- Notification Logs table - detailed logs for each notification attempt
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
);

-- Notifications table
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
);

-- Notification Settings table
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
);
