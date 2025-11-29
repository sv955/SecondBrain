"""
Database module for Second Brain App
Handles all database connections, initialization, and operations.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any


# Database location
DB_FOLDER = r'C:\Users\z004fa0f\OneDrive - Siemens Healthineers\SecondBrain_Db'
DATABASE_NAME = os.path.join(DB_FOLDER, 'secondbrain.db')


def init_db():
    """Initialize the database with required tables."""
    # Create directory if it doesn't exist
    os.makedirs(DB_FOLDER, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create todos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unique_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'Medium',
            target_date DATE,
            start_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add priority column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE todos ADD COLUMN priority TEXT DEFAULT "Medium"')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add target_date column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE todos ADD COLUMN target_date DATE')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add start_date column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE todos ADD COLUMN start_date DATE')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add end_date column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE todos ADD COLUMN end_date DATE')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add unique_id column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE todos ADD COLUMN unique_id TEXT')
        conn.commit()
        # Generate unique_ids for existing records
        import uuid
        rows = cursor.execute('SELECT id FROM todos WHERE unique_id IS NULL').fetchall()
        for row in rows:
            cursor.execute('UPDATE todos SET unique_id = ? WHERE id = ?', 
                         (str(uuid.uuid4()), row[0]))
        conn.commit()
        # Make it UNIQUE after populating
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_id ON todos(unique_id)')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create experiences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            tags TEXT,
            category TEXT,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add tags column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE experiences ADD COLUMN tags TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add category column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE experiences ADD COLUMN category TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Add context column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE experiences ADD COLUMN context TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()


def get_db_connection():
    """
    Get a database connection with row factory configured.
    Returns a connection object that returns rows as dictionaries.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# TODO OPERATIONS
# ============================================================================

def create_todo(title: str, description: str = '', status: str = 'in-queue', priority: str = 'Medium', target_date: str = None, start_date: str = None, end_date: str = None) -> int:
    """
    Create a new todo item.
    
    Args:
        title: Title of the todo (required)
        description: Rich text description (HTML content)
        status: Status of the todo (default: 'in-queue')
        priority: Priority of the todo (default: 'Medium')
        target_date: Target completion date (YYYY-MM-DD format, optional)
        start_date: Planned start date for working on the task (YYYY-MM-DD format, optional)
        end_date: Planned end date for working on the task (YYYY-MM-DD format, optional)
    
    Returns:
        The ID of the newly created todo
    """
    import uuid
    unique_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO todos (unique_id, title, description, status, priority, target_date, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (unique_id, title, description, status, priority, target_date, start_date, end_date)
    )
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return todo_id


def get_todos(status_filter: str = '', from_date: str = '', to_date: str = '', 
              sort_by: str = 'created_at', sort_order: str = 'DESC', include_done: str = 'false') -> List[sqlite3.Row]:
    """
    Get todos with optional filtering and sorting.
    
    Args:
        status_filter: Filter by status (optional)
        from_date: Filter from date (YYYY-MM-DD format, optional)
        to_date: Filter to date (YYYY-MM-DD format, optional)
        sort_by: Column to sort by (default: 'created_at')
        sort_order: Sort order 'ASC' or 'DESC' (default: 'DESC')
        include_done: Include done status records ('true' or 'false', default: 'false')
    
    Returns:
        List of todo rows
    """
    conn = get_db_connection()
    
    # Build query
    query = 'SELECT * FROM todos'
    params = []
    conditions = []
    
    if status_filter:
        conditions.append('status = ?')
        params.append(status_filter)
    elif include_done == 'false':
        # Exclude done status by default when no specific status filter is applied
        conditions.append('status != ?')
        params.append('done')
    
    if from_date:
        conditions.append('DATE(created_at) >= ?')
        params.append(from_date)
    
    if to_date:
        conditions.append('DATE(created_at) <= ?')
        params.append(to_date)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    # Validate sort options
    allowed_sorts = ['created_at', 'updated_at', 'title', 'status', 'priority', 'target_date', 'start_date', 'end_date', 'remaining_days']
    if sort_by not in allowed_sorts:
        sort_by = 'created_at'
    
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'DESC'
    
    # Custom sorting for status and priority
    if sort_by == 'status':
        # Status order: in-queue, ready, in-progress, hold, done
        order_clause = f'''ORDER BY 
            CASE status
                WHEN 'in-queue' THEN 1
                WHEN 'ready' THEN 2
                WHEN 'in-progress' THEN 3
                WHEN 'hold' THEN 4
                WHEN 'done' THEN 5
                ELSE 6
            END {sort_order}'''
        query += ' ' + order_clause
    elif sort_by == 'priority':
        # Priority order: Low, Medium, High, Critical
        order_clause = f'''ORDER BY 
            CASE priority
                WHEN 'Low' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'High' THEN 3
                WHEN 'Critical' THEN 4
                ELSE 5
            END {sort_order}'''
        query += ' ' + order_clause
    elif sort_by == 'remaining_days':
        # Sort by remaining days (target_date - current_date)
        # NULL values (no target date) should appear last
        order_clause = f'''ORDER BY 
            CASE 
                WHEN target_date IS NULL THEN 1
                ELSE 0
            END,
            julianday(target_date) - julianday('now') {sort_order}'''
        query += ' ' + order_clause
    else:
        # Standard sorting for other columns
        query += f' ORDER BY {sort_by} {sort_order}'
    
    todos = conn.execute(query, params).fetchall()
    conn.close()
    
    return todos


def get_todays_tasks() -> List[sqlite3.Row]:
    """
    Get todos that should be worked on today based on work start/end dates.
    
    Logic:
    - Include tasks where today falls between start_date and end_date
    - Include tasks where end_date has passed but status is not 'done' (overdue tasks)
    - Order by: overdue tasks first, then by priority (Critical > High > Medium > Low)
    
    Returns:
        List of todo rows for today
    """
    conn = get_db_connection()
    
    query = '''SELECT *, 
                   CASE 
                       WHEN end_date < DATE('now') AND status != 'done' THEN 1
                       ELSE 0
                   END as is_overdue
               FROM todos 
               WHERE (
                   (start_date IS NOT NULL AND end_date IS NOT NULL 
                    AND DATE('now') BETWEEN start_date AND end_date)
                   OR 
                   (end_date IS NOT NULL AND end_date < DATE('now') AND status != 'done')
               )
               ORDER BY 
                   is_overdue DESC,
                   CASE priority
                       WHEN 'Critical' THEN 1
                       WHEN 'High' THEN 2
                       WHEN 'Medium' THEN 3
                       WHEN 'Low' THEN 4
                       ELSE 5
                   END ASC,
                   start_date ASC'''
    
    todos = conn.execute(query).fetchall()
    conn.close()
    
    return todos


def get_todo_by_id(todo_id: int) -> Optional[sqlite3.Row]:
    """
    Get a single todo by ID.
    
    Args:
        todo_id: The ID of the todo
    
    Returns:
        Todo row or None if not found
    """
    conn = get_db_connection()
    todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
    conn.close()
    return todo


def update_todo(todo_id: int, title: str, description: str = '', status: str = 'in-queue', priority: str = 'Medium', target_date: str = None, start_date: str = None, end_date: str = None) -> bool:
    """
    Update an existing todo.
    
    Args:
        todo_id: The ID of the todo to update
        title: New title
        description: New description
        status: New status
        priority: New priority
        target_date: New target date (YYYY-MM-DD format, optional)
        start_date: New start date (YYYY-MM-DD format, optional)
        end_date: New end date (YYYY-MM-DD format, optional)
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    conn.execute(
        'UPDATE todos SET title = ?, description = ?, status = ?, priority = ?, target_date = ?, start_date = ?, end_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, description, status, priority, target_date, start_date, end_date, todo_id)
    )
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0


def update_todo_status(todo_id: int, status: str) -> bool:
    """
    Update only the status of a todo.
    
    Args:
        todo_id: The ID of the todo
        status: New status value
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    conn.execute(
        'UPDATE todos SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (status, todo_id)
    )
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0


def delete_todo(todo_id: int) -> bool:
    """
    Delete a todo by ID.
    
    Args:
        todo_id: The ID of the todo to delete
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0


# ============================================================================
# EXPERIENCE OPERATIONS
# ============================================================================

def create_experience(title: str, content: str = '', tags: str = '', category: str = '', context: str = '') -> int:
    """
    Create a new experience entry.
    
    Args:
        title: Title of the experience (required)
        content: Plain text content
        tags: Comma-separated tags for categorization (e.g., "python, debugging, performance")
        category: Category of experience (e.g., "Technical", "Project", "Problem-Solving")
        context: Additional context or situation description for LLM understanding
    
    Returns:
        The ID of the newly created experience
    """
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO experiences (title, content, tags, category, context) VALUES (?, ?, ?, ?, ?)',
        (title, content, tags, category, context)
    )
    experience_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return experience_id


def get_experiences(from_date: str = '', to_date: str = '', 
                   sort_by: str = 'created_at', sort_order: str = 'DESC') -> List[sqlite3.Row]:
    """
    Get experiences with optional filtering and sorting.
    
    Args:
        from_date: Filter from date (YYYY-MM-DD format, optional)
        to_date: Filter to date (YYYY-MM-DD format, optional)
        sort_by: Column to sort by (default: 'created_at')
        sort_order: Sort order 'ASC' or 'DESC' (default: 'DESC')
    
    Returns:
        List of experience rows
    """
    conn = get_db_connection()
    
    # Build query
    query = 'SELECT * FROM experiences'
    params = []
    conditions = []
    
    if from_date:
        conditions.append('DATE(created_at) >= ?')
        params.append(from_date)
    
    if to_date:
        conditions.append('DATE(created_at) <= ?')
        params.append(to_date)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    # Validate sort options
    allowed_sorts = ['created_at', 'updated_at', 'title']
    if sort_by not in allowed_sorts:
        sort_by = 'created_at'
    
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'DESC'
    
    query += f' ORDER BY {sort_by} {sort_order}'
    
    experiences = conn.execute(query, params).fetchall()
    conn.close()
    
    return experiences


def get_experience_by_id(experience_id: int) -> Optional[sqlite3.Row]:
    """
    Get a single experience by ID.
    
    Args:
        experience_id: The ID of the experience
    
    Returns:
        Experience row or None if not found
    """
    conn = get_db_connection()
    experience = conn.execute('SELECT * FROM experiences WHERE id = ?', (experience_id,)).fetchone()
    conn.close()
    return experience


def update_experience(experience_id: int, title: str, content: str = '', tags: str = '', category: str = '', context: str = '') -> bool:
    """
    Update an existing experience.
    
    Args:
        experience_id: The ID of the experience to update
        title: New title
        content: New content
        tags: Comma-separated tags for categorization
        category: Category of experience
        context: Additional context or situation description
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    conn.execute(
        'UPDATE experiences SET title = ?, content = ?, tags = ?, category = ?, context = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (title, content, tags, category, context, experience_id)
    )
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0


def delete_experience(experience_id: int) -> bool:
    """
    Delete an experience by ID.
    
    Args:
        experience_id: The ID of the experience to delete
    
    Returns:
        True if successful, False otherwise
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM experiences WHERE id = ?', (experience_id,))
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0
