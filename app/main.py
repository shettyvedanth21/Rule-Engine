from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.database import test_connection, execute_query
from app.sql_utils import load_schema
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
            # Load and execute schema from external SQL file
            schema_sql = load_schema()
            # Execute each statement separately (split by semicolon)
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                if statement:
                    execute_query(statement, fetch=False)
            
            print("Database tables created successfully!")
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
