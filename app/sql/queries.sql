-- SQL Queries for Rule Engine API
-- This file contains all CRUD operation queries

-- ============================================
-- RULES QUERIES
-- ============================================
-- Get all rules
SELECT * FROM rules ORDER BY priority DESC, created_at DESC;

-- Get rule by ID
SELECT * FROM rules WHERE id = %s;

-- Get active rules
SELECT * FROM rules WHERE is_active = TRUE ORDER BY priority DESC;

-- Get rules by state
SELECT * FROM rules WHERE state = %s;

-- Create rule
INSERT INTO rules (id, name, description, `condition`, condition_type, is_active, priority, state, debounce_seconds, retry_enabled, retry_max_attempts, retry_interval_seconds) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- Update rule
UPDATE rules SET name=%s, description=%s, `condition`=%s, condition_type=%s, is_active=%s, priority=%s, state=%s, debounce_seconds=%s, retry_enabled=%s, retry_max_attempts=%s, retry_interval_seconds=%s WHERE id=%s;

-- Update rule state
UPDATE rules SET state=%s, last_triggered_at=NOW() WHERE id=%s;

-- Delete rule
DELETE FROM rules WHERE id = %s;

-- ============================================
-- RULE ACTIONS QUERIES
-- ============================================
-- Get all rule actions
SELECT * FROM rule_actions ORDER BY created_at DESC;

-- Get rule action by ID
SELECT * FROM rule_actions WHERE id = %s;

-- Get rule actions by rule ID
SELECT * FROM rule_actions WHERE rule_id = %s ORDER BY created_at DESC;

-- Create rule action
INSERT INTO rule_actions (id, rule_id, action_type, action_config) VALUES (%s, %s, %s, %s);

-- Update rule action
UPDATE rule_actions SET action_type=%s, action_config=%s WHERE id=%s;

-- Delete rule action
DELETE FROM rule_actions WHERE id = %s;

-- ============================================
-- RULE EVALUATIONS QUERIES
-- ============================================
-- Get all rule evaluations
SELECT * FROM rule_evaluations ORDER BY evaluated_at DESC;

-- Get rule evaluation by ID
SELECT * FROM rule_evaluations WHERE id = %s;

-- Get rule evaluations by rule ID
SELECT * FROM rule_evaluations WHERE rule_id = %s ORDER BY evaluated_at DESC;

-- Create rule evaluation
INSERT INTO rule_evaluations (id, rule_id, evaluated_at, result, details) VALUES (%s, %s, NOW(), %s, %s);

-- Update rule evaluation
UPDATE rule_evaluations SET result=%s, details=%s WHERE id=%s;

-- Delete rule evaluation
DELETE FROM rule_evaluations WHERE id = %s;

-- ============================================
-- RULE TRIGGERS QUERIES
-- ============================================
-- Get all rule triggers
SELECT * FROM rule_triggers ORDER BY created_at DESC;

-- Get rule trigger by ID
SELECT * FROM rule_triggers WHERE id = %s;

-- Get rule triggers by rule ID
SELECT * FROM rule_triggers WHERE rule_id = %s ORDER BY created_at DESC;

-- Create rule trigger
INSERT INTO rule_triggers (id, rule_id, trigger_type, trigger_config, is_active) VALUES (%s, %s, %s, %s, %s);

-- Update rule trigger
UPDATE rule_triggers SET trigger_type=%s, trigger_config=%s, is_active=%s WHERE id=%s;

-- Delete rule trigger
DELETE FROM rule_triggers WHERE id = %s;

-- ============================================
-- RULE EVENTS QUERIES
-- ============================================
-- Get all rule events
SELECT * FROM rule_events ORDER BY triggered_at DESC;

-- Get rule event by ID
SELECT * FROM rule_events WHERE id = %s;

-- Get rule events by rule ID
SELECT * FROM rule_events WHERE rule_id = %s ORDER BY triggered_at DESC;

-- Get rule event by event ID
SELECT * FROM rule_events WHERE rule_id = %s AND event_id = %s;

-- Get pending rule events
SELECT * FROM rule_events WHERE notification_status = 'PENDING';

-- Get recent rule events
SELECT * FROM rule_events WHERE rule_id = %s AND triggered_at > DATE_SUB(NOW(), INTERVAL %s SECOND);

-- Create rule event
INSERT INTO rule_events (id, rule_id, event_id, data_snapshot, notification_status, channels_notified) 
VALUES (%s, %s, %s, %s, %s, %s);

-- Update rule event status
UPDATE rule_events SET notification_status=%s, channels_notified=%s WHERE id=%s;

-- Delete rule event
DELETE FROM rule_events WHERE id = %s;

-- ============================================
-- NOTIFICATION LOGS QUERIES
-- ============================================
-- Get all notification logs
SELECT * FROM notification_logs ORDER BY created_at DESC;

-- Get notification log by ID
SELECT * FROM notification_logs WHERE id = %s;

-- Get notification logs by event ID
SELECT * FROM notification_logs WHERE event_id = %s;

-- Get notification logs by rule ID
SELECT * FROM notification_logs WHERE rule_id = %s ORDER BY created_at DESC;

-- Get failed notification logs
SELECT * FROM notification_logs WHERE status = 'FAILED' AND attempt_number < %s;

-- Create notification log
INSERT INTO notification_logs (id, event_id, rule_id, notification_id, channel, status, attempt_number, error_message) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);

-- Update notification log status
UPDATE notification_logs SET status=%s, sent_at=NOW(), error_message=%s, attempt_number=%s WHERE id=%s;

-- ============================================
-- NOTIFICATIONS QUERIES
-- ============================================
-- Get all notifications
SELECT * FROM notifications ORDER BY triggered_at DESC;

-- Get notification by ID
SELECT * FROM notifications WHERE id = %s;

-- Get notifications by rule ID
SELECT * FROM notifications WHERE rule_id = %s ORDER BY triggered_at DESC;

-- Get notifications by channel
SELECT * FROM notifications WHERE channel = %s ORDER BY triggered_at DESC;

-- Get pending notifications
SELECT * FROM notifications WHERE status = 'PENDING' AND send_at <= NOW();

-- Get escalation notifications
SELECT * FROM notifications WHERE status = 'SENT' AND acknowledged_at IS NULL AND next_escalation_at IS NOT NULL AND next_escalation_at <= NOW();

-- Create notification
INSERT INTO notifications (id, rule_id, title, message, notification_type, channel, status, priority, recipient_email, recipient_phone, whatsapp_number, telegram_chat_id, webhook_url, send_at, escalation_level) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- Update notification status
UPDATE notifications SET status=%s, sent_at=NOW() WHERE id=%s;

-- Acknowledge notification
UPDATE notifications SET status='ACKNOWLEDGED', acknowledged_at=NOW(), acknowledged_by=%s WHERE id=%s;

-- Escalate notification
UPDATE notifications SET escalation_level=%s, next_escalation_at=%s, status='PENDING', send_at=%s WHERE id=%s;

-- ============================================
-- NOTIFICATION SETTINGS QUERIES
-- ============================================
-- Get all notification settings
SELECT * FROM notification_settings WHERE is_active = TRUE;

-- Get notification settings by ID
SELECT * FROM notification_settings WHERE id = %s;

-- Get notification settings by rule ID
SELECT * FROM notification_settings WHERE rule_id = %s AND is_active = TRUE;

-- Get notification settings by channel
SELECT * FROM notification_settings WHERE rule_id = %s AND notification_type = %s AND is_active = TRUE;

-- Create notification settings
INSERT INTO notification_settings (id, rule_id, notification_type, recipient_email, recipient_phone, whatsapp_number, telegram_chat_id, webhook_url, send_interval_minutes, escalation_enabled, escalation_interval_minutes, max_escalations, is_active) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- Update notification settings
UPDATE notification_settings SET notification_type=%s, recipient_email=%s, recipient_phone=%s, whatsapp_number=%s, telegram_chat_id=%s, webhook_url=%s, send_interval_minutes=%s, escalation_enabled=%s, escalation_interval_minutes=%s, max_escalations=%s, is_active=%s WHERE id=%s;

-- Delete notification settings
UPDATE notification_settings SET is_active=FALSE WHERE id=%s;
