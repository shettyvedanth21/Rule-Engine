# Table definitions for factory database
# Now loaded from external SQL files

from app.sql_utils import get_queries

# Get queries from external SQL file
_queries = get_queries()

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
    'get_by_rule_id': "SELECT * FROM rule_actions WHERE rule_id = %s ORDER BY created_at DESC",
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
