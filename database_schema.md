# Database Schema - Second Brain App

## Database: secondbrain.db
SQLite3 database file storing all application data.

---

## Table: todos

Stores user's tasks and to-do items.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each todo |
| unique_id | TEXT | NOT NULL, UNIQUE | UUID (GUID) for todo identification |
| title | TEXT | NOT NULL, max 200 chars | Title of the todo item |
| description | TEXT | NULL, max 10000 chars | Rich text description (HTML content from Quill editor) |
| status | TEXT | DEFAULT 'pending' | Current status of the todo |
| priority | TEXT | DEFAULT 'Medium' | Priority level of the todo |
| target_date | DATE | NULL | Target completion date (YYYY-MM-DD format) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when todo was created |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when todo was last updated |

### Status Values
- `in-queue` - Todo is waiting in queue
- `ready` - Todo is ready to be worked on
- `in-progress` - Currently being worked on
- `hold` - Temporarily on hold
- `done` - Completed

### Priority Values
- `Low` - Low priority task
- `Medium` - Medium priority task (default)
- `High` - High priority task
- `Critical` - Critical priority task

### Indexes
- Primary key index on `id`

### Related Templates
- `create_todo.html` - Form fields: title (required), description (Quill editor), status, priority, target_date (defaults to today, min: today, max: +10 years); Auto-generates unique_id (UUID)
- `edit_todo.html` - Form fields: unique_id (readonly), title (required), description (Quill editor), status, priority, target_date (defaults to today if not set, min: today, max: +10 years)
- `view_todos.html` - Displays: created_at, target_date, title, status, priority; Column headers are sortable with up/down arrows; Filters: status, from_date, to_date
- `todo_detail.html` - Displays: title, description, status, priority, target_date, created_at, updated_at

---

## Table: experiences

Stores past experiences and knowledge documentation for RAG (Retrieval-Augmented Generation) integration.

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each experience |
| title | TEXT | NOT NULL, max 200 chars | Title of the experience |
| content | TEXT | NULL, max 10000 chars | Plain text content (supports line breaks) |
| tags | TEXT | NULL, max 200 chars | Comma-separated tags for categorization (e.g., "python, debugging, api") |
| category | TEXT | NULL | Category of experience for better organization |
| context | TEXT | NULL, max 500 chars | Additional context/situation description to help LLM understand relevance |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when experience was created |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Timestamp when experience was last updated |

### Category Values
- `Technical` - Technical knowledge or solution
- `Problem-Solving` - Problem-solving approach
- `Project` - Project-related experience
- `Learning` - Learning or educational content
- `Best-Practice` - Best practices and recommendations
- `Troubleshooting` - Troubleshooting steps and fixes
- `Design` - Design patterns and architecture
- `Other` - Other types of experiences

### Indexes
- Primary key index on `id`

### RAG Integration Notes
- **Plain Text Storage**: Content is stored as plain text (not HTML) to make it directly usable for LLM processing
- **Structured Metadata**: Tags, category, and context fields provide structured metadata for better retrieval
- **Tags**: Enable semantic search and filtering by topics
- **Category**: Groups similar experiences for domain-specific queries
- **Context**: Provides situational information to help LLM understand when/how to use the experience
- **Timestamps**: Allow temporal filtering (recent vs older experiences)

### Related Templates
- `create_experience.html` - Form fields: title (required), tags, category, context (3 rows), content (21 rows)
- `edit_experience.html` - Form fields: title (required), tags, category, context (3 rows), content (21 rows)
- `view_experiences.html` - Displays: title, created_at, updated_at; Filters: from_date, to_date; Sort: created_at, updated_at, title

---

## Notes

1. **Text Storage for RAG**: The `content` field in experiences table stores plain text (not HTML) to be directly compatible with LLM/RAG systems. Line breaks are preserved for readability.

2. **Metadata for Better Retrieval**: Experiences include tags, category, and context fields to improve semantic search and retrieval accuracy for RAG applications.

3. **Rich Text for Todos**: The `description` field in todos table stores HTML content from Quill.js rich text editor for detailed formatting needs.

4. **Timestamps**: All timestamps are managed by SQLite's CURRENT_TIMESTAMP and are stored in UTC format (YYYY-MM-DD HH:MM:SS).

5. **Status Field**: The `status` field in todos table uses lowercase hyphenated values for consistency with the frontend.

6. **Auto-update Triggers**: The `updated_at` field is manually updated in UPDATE queries using `updated_at = CURRENT_TIMESTAMP`.

7. **Field Validation**: Required fields (NOT NULL) are validated both at database level and in HTML forms.

8. **RAG Use Case**: The experiences table is optimized for:
   - Vector embeddings generation from plain text content
   - Semantic search using tags and category
   - Contextual retrieval using the context field
   - Temporal filtering using timestamps
   - Easy export to JSON/CSV for LLM training or fine-tuning
