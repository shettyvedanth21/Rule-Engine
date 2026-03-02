"""SQL Loader Module - Loads SQL from external files."""

import os
from typing import Dict, List

# Base directory for SQL files
SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')

def load_schema() -> str:
    """Load the database schema from schema.sql file."""
    schema_path = os.path.join(SQL_DIR, 'schema.sql')
    with open(schema_path, 'r') as f:
        return f.read()

def get_table_creation_sql(table_name: str) -> str:
    """Get the CREATE TABLE SQL for a specific table."""
    schema = load_schema()
    
    # Find the specific table definition
    lines = schema.split('\n')
    in_table = False
    table_sql = []
    
    current_table = None
    for line in lines:
        if line.startswith('CREATE TABLE IF NOT EXISTS'):
            # Extract table name
            start = line.find('`') + 1
            end = line.find('`', start)
            current_table = line[start:end]
            in_table = current_table == table_name
        
        if in_table:
            table_sql.append(line)
            if line.strip() == ');':
                break
    
    return '\n'.join(table_sql)

def load_queries() -> Dict[str, str]:
    """Load all SQL queries from queries.sql file."""
    queries_path = os.path.join(SQL_DIR, 'queries.sql')
    with open(queries_path, 'r') as f:
        content = f.read()
    
    # Parse queries - they are separated by comments
    # Format: -- ============================================
    #         -- QUERY NAME
    #         -- ============================================
    #         ACTUAL QUERY;
    
    queries = {}
    current_section = []
    current_query_name = None
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('-- ============================================'):
            # Save previous query if exists
            if current_query_name and current_section:
                query_text = '\n'.join(current_section).strip()
                if query_text:
                    queries[current_query_name] = query_text
            current_section = []
            current_query_name = None
        elif line.startswith('-- '):
            # This is a section header
            query_name = line.replace('-- ', '').replace(' QUERIES', '').replace(' QUERY', '').strip()
            current_query_name = query_name
        elif line.strip() and not line.startswith('--'):
            current_section.append(line)
    
    # Don't forget the last query
    if current_query_name and current_section:
        query_text = '\n'.join(current_section).strip()
        if query_text:
            queries[current_query_name] = query_text
    
    return queries

# Pre-load queries on module import
_QUERIES_CACHE = None

def get_queries() -> Dict[str, str]:
    """Get cached queries dictionary."""
    global _QUERIES_CACHE
    if _QUERIES_CACHE is None:
        _QUERIES_CACHE = load_queries()
    return _QUERIES_CACHE
