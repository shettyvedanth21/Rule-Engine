from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.database import test_connection, execute_query
from app.routes import rules, rule_actions, rule_evaluations, rule_triggers
from app.routes.notifications import router as notifications_router
from app.routes.rule_evaluation_service import router as rule_evaluation_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Rule Engine API",
    description="REST API for Rule Engine Database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rules.router, prefix="/api")
app.include_router(rule_actions.router, prefix="/api")
app.include_router(rule_evaluations.router, prefix="/api")
app.include_router(rule_triggers.router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(rule_evaluation_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Rule Engine API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug/db-structure")
async def debug_db_structure():
    """Debug endpoint to show database table structure."""
    import mysql.connector
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Direct connection without pooling
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            connect_timeout=10
        )
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        result = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            result[table_name] = [
                {"name": col[0], "type": col[1], "key": col[3]} 
                for col in columns
            ]
        
        cursor.close()
        conn.close()
        
        return {"tables": result}
    except mysql.connector.Error as e:
        return {"error": str(e), "error_code": e.errno}


@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to show all registered routes."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return {"routes": routes}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    import os
    from dotenv import load_dotenv
    
    print("Starting Rule Engine API...")
    
    # First, try to create the database if it doesn't exist
    db_name = os.getenv('DB_NAME', 'factory')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    
    try:
        import mysql.connector
        # Connect without database to create it if needed
        temp_config = {
            'host': db_host,
            'user': db_user,
            'password': db_password
        }
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.close()
        conn.close()
        print(f"Database '{db_name}' ready!")
    except Exception as e:
        print(f"Note: Could not create database: {e}")
    
    # Now test connection and create tables
    if test_connection():
        print("Database connection established!")
        # Create tables if they don't exist
        try:
            # Create rules table with enhanced fields
            execute_query("""
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
                )
            """, fetch=False)
            
            # Create rule_actions table
            execute_query("""
                CREATE TABLE IF NOT EXISTS rule_actions (
                    id CHAR(36) PRIMARY KEY,
                    rule_id CHAR(36),
                    action_type VARCHAR(100) NOT NULL,
                    action_config LONGTEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
                )
            """, fetch=False)
            
            # Create rule_evaluations table
            execute_query("""
                CREATE TABLE IF NOT EXISTS rule_evaluations (
                    id CHAR(36) PRIMARY KEY,
                    rule_id CHAR(36),
                    evaluated_at TIMESTAMP NOT NULL,
                    result BOOLEAN,
                    details LONGTEXT,
                    FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE
                )
            """, fetch=False)
            
            # Create rule_triggers table
            execute_query("""
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
            """, fetch=False)
            
            # Create notifications table with channel support
            execute_query("""
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
            """, fetch=False)
            
            # Create notification_settings table
            execute_query("""
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
            """, fetch=False)
            
            # Create rule_events table - tracks rule trigger events for deduplication
            execute_query("""
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
            """, fetch=False)
            
            # Create notification_logs table - detailed logs for each notification attempt
            execute_query("""
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
            """, fetch=False)
            
            print("Database tables created successfully!")
            print("Database tables updated successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")
    else:
        print("WARNING: Database connection failed! Application may not function correctly.")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("Shutting down Rule Engine API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
