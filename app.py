from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import database as db

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create-todo', methods=['GET', 'POST'])
def create_todo():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        status = request.form.get('status', 'in-queue')
        priority = request.form.get('priority', 'Medium')
        target_date = request.form.get('target_date', None)
        start_date = request.form.get('start_date', None)
        end_date = request.form.get('end_date', None)
        
        if target_date == '':
            target_date = None
        if start_date == '':
            start_date = None
        if end_date == '':
            end_date = None
        
        # Validate lengths
        if len(title) > 200:
            title = title[:200]
        if len(description) > 10000:
            description = description[:10000]
        
        db.create_todo(title, description, status, priority, target_date, start_date, end_date)
        
        return redirect(url_for('all_todos'))
    
    return render_template('create_todo.html')

@app.route('/all-todos')
def all_todos():
    # Get filter parameters
    status_filter = request.args.get('status', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'DESC')
    include_done = request.args.get('include_done', 'false')
    
    todos = db.get_todos(status_filter, from_date, to_date, sort_by, sort_order, include_done)
    
    return render_template('all_todos.html', todos=todos, 
                         current_status=status_filter,
                         from_date=from_date,
                         to_date=to_date,
                         current_sort=sort_by,
                         current_order=sort_order,
                         include_done=include_done)

@app.route('/todays-tasks')
def todays_tasks():
    from datetime import date
    today = date.today()
    todos = db.get_todays_tasks()
    return render_template('todays_tasks.html', todos=todos, today=today)

@app.route('/todo/<int:id>')
def view_todo(id):
    todo = db.get_todo_by_id(id)
    
    if todo is None:
        return redirect(url_for('all_todos'))
    
    return render_template('view_todo.html', todo=todo)

@app.route('/edit-todo/<int:id>', methods=['GET', 'POST'])
def edit_todo(id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        status = request.form.get('status', 'in-queue')
        priority = request.form.get('priority', 'Medium')
        target_date = request.form.get('target_date', None)
        start_date = request.form.get('start_date', None)
        end_date = request.form.get('end_date', None)
        
        if target_date == '':
            target_date = None
        if start_date == '':
            start_date = None
        if end_date == '':
            end_date = None
        
        # Validate lengths
        if len(title) > 200:
            title = title[:200]
        if len(description) > 10000:
            description = description[:10000]
        
        db.update_todo(id, title, description, status, priority, target_date, start_date, end_date)
        
        return redirect(url_for('all_todos'))
    
    todo = db.get_todo_by_id(id)
    
    if todo is None:
        return redirect(url_for('all_todos'))
    
    return render_template('edit_todo.html', todo=todo)

@app.route('/delete-todo/<int:id>')
def delete_todo(id):
    db.delete_todo(id)
    return redirect(url_for('all_todos'))

@app.route('/update-status/<int:id>/<status>')
def update_status(id, status):
    db.update_todo_status(id, status)
    # Check if coming from today's tasks page
    referer = request.referrer
    if referer and 'todays-tasks' in referer:
        return redirect(url_for('todays_tasks'))
    return redirect(url_for('all_todos'))

# Past Experience Routes
@app.route('/create-experience', methods=['GET', 'POST'])
def create_experience():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        tags = request.form.get('tags', '')
        category = request.form.get('category', '')
        context = request.form.get('context', '')
        
        # Validate lengths
        if len(title) > 200:
            title = title[:200]
        if len(content) > 10000:
            content = content[:10000]
        
        db.create_experience(title, content, tags, category, context)
        
        return redirect(url_for('view_experiences'))
    
    return render_template('create_experience.html')

@app.route('/view-experiences')
def view_experiences():
    # Get filter parameters
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'DESC')
    
    experiences = db.get_experiences(from_date, to_date, sort_by, sort_order)
    
    return render_template('all_experiences.html', experiences=experiences,
                         from_date=from_date,
                         to_date=to_date,
                         current_sort=sort_by,
                         current_order=sort_order)

@app.route('/experience/<int:id>')
def view_experience(id):
    experience = db.get_experience_by_id(id)
    
    if experience is None:
        return redirect(url_for('view_experiences'))
    
    return render_template('view_experience.html', experience=experience)

@app.route('/edit-experience/<int:id>', methods=['GET', 'POST'])
def edit_experience(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form.get('content', '')
        tags = request.form.get('tags', '')
        category = request.form.get('category', '')
        context = request.form.get('context', '')
        
        # Validate lengths
        if len(title) > 200:
            title = title[:200]
        if len(content) > 10000:
            content = content[:10000]
        
        db.update_experience(id, title, content, tags, category, context)
        
        return redirect(url_for('view_experiences'))
    
    experience = db.get_experience_by_id(id)
    
    if experience is None:
        return redirect(url_for('view_experiences'))
    
    return render_template('edit_experience.html', experience=experience)

@app.route('/delete-experience/<int:id>')
def delete_experience(id):
    db.delete_experience(id)
    return redirect(url_for('view_experiences'))

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, port=1234)
