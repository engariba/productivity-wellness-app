from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from flask import jsonify  # Import for returning JSON data (optional)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import plotly.express as px
import json
import os
import random
import plotly
import requests
from datetime import datetime
from datetime import timedelta
from sqlalchemy import extract
import random
from flask import Flask, render_template
from sqlalchemy import extract, and_
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from flask import flash



app = Flask(__name__)
app.secret_key = 'your-secret-key-here' 
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'


# Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, nullable=False)


class Affirmation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)

class WaterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    amount = db.Column(db.Integer, nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'))

    category = db.relationship('ExpenseCategory')

class ExpenseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(7))  # Hex color code

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'))
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    category = db.relationship('ExpenseCategory')

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # Duration in minutes
    date = db.Column(db.Date, nullable=False)


# Routes
@app.route('/')
def home():
    today = datetime.today().date()
    tasks = Task.query.filter(Task.date == today).all()
    affirmations = Affirmation.query.all()
    daily_affirmation = random.choice(affirmations).message if affirmations else "Stay positive!"

    return render_template('dashboard.html', tasks=tasks, affirmation=daily_affirmation)


@app.route('/add_task', methods=['POST'])
def add_task():
    description = request.form.get('description')
    date_str = request.form.get('date')

    if not description or not date_str:
        return "Missing data", 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format", 400

    new_task = Task(description=description, date=date)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('calendar_view'))



@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    """Mark a task as completed and return to the same page"""
    task = Task.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
    # Stay on the task manager page after marking as complete
    return redirect(request.referrer or url_for('task_manager'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    """Delete a task and redirect to the previous page"""
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(request.referrer or url_for('task_manager'))




@app.route('/water_intake', methods=['GET', 'POST'])
def water_intake():
    daily_goal = 2000
    if request.method == 'POST':
        amount = request.form.get('amount')
        if amount and amount.isdigit():
            new_entry = WaterLog(amount=int(amount))
            db.session.add(new_entry)
            db.session.commit()
            flash('Water intake added!', 'success')  # Optional confirmation
            return redirect(url_for('water_intake'))

    today = datetime.today().date()
    records = WaterLog.query.filter(WaterLog.timestamp >= today).all()
    total_intake = sum(record.amount for record in records)

    return render_template('water_intake.html', 
                         records=records, 
                         total_intake=total_intake, 
                         daily_goal=daily_goal)

@app.route('/reset_water', methods=['POST'])
def reset_water():
    # Delete today's records from DATABASE (not session)
    today = datetime.today().date()
    WaterLog.query.filter(WaterLog.timestamp >= today).delete()
    db.session.commit()
    flash('Water log reset successfully', 'success')
    return redirect(url_for('water_intake'))


# Function to calculate category totals
def calculate_category_totals(budgets, current_month, current_year):
    category_totals = {}
    for budget in budgets:
        monthly_expenses = Expense.query.filter(
            Expense.category_id == budget.category_id,
            extract('month', Expense.timestamp) == current_month,
            extract('year', Expense.timestamp) == current_year
        ).all()
        category_totals[budget.category_id] = sum(exp.amount for exp in monthly_expenses)
    return category_totals

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # Handle filters
    category_filter = request.args.get('category_filter', '')
    time_filter = request.args.get('time_filter', 'all')

    # Base query for expenses
    query = Expense.query

    # Apply filters
    if category_filter:
        query = query.filter(Expense.category_id == category_filter)

    if time_filter == 'month':
        start_date = today.replace(day=1)
        query = query.filter(Expense.timestamp >= start_date)
    elif time_filter == 'week':
        start_date = today - timedelta(days=today.weekday())
        query = query.filter(Expense.timestamp >= start_date)

    # Get filtered expenses
    filtered_expenses = query.order_by(Expense.timestamp.desc()).all()
    total_expenses = sum(exp.amount for exp in filtered_expenses)

    # Get all categories and current month's budgets
    categories = ExpenseCategory.query.all()
    budgets = Budget.query.filter(
        Budget.month == current_month,
        Budget.year == current_year
    ).all()

    # Calculate category totals - IMPROVED VERSION
    category_totals = {}
    for category in categories:
        # Base query for this category
        cat_query = Expense.query.filter(Expense.category_id == category.id)
        
        # Always calculate monthly total for budget progress
        monthly_expenses = cat_query.filter(
            extract('month', Expense.timestamp) == current_month,
            extract('year', Expense.timestamp) == current_year
        ).all()
        category_totals[category.id] = sum(exp.amount for exp in monthly_expenses)

    # Prepare chart data
    chart_data = {
        'categories': [],
        'months': []
    }

    # Category data for pie chart
    for category in categories:
        chart_data['categories'].append({
            'name': category.name,
            'total': category_totals.get(category.id, 0),
            'color': category.color
        })

    # Monthly trend data (last 6 months)
    for i in range(6):
        month_date = today - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        monthly_expenses = Expense.query.filter(
            and_(
                Expense.timestamp >= month_start,
                Expense.timestamp <= month_end
            )
        ).all()
        
        chart_data['months'].append({
            'date': month_start.strftime('%b %Y'),
            'total': sum(exp.amount for exp in monthly_expenses)
        })

    chart_data['months'].reverse()

    return render_template(
        'expenses.html',
        expenses=filtered_expenses,
        total=total_expenses,
        categories=categories,
        budgets=budgets,
        category_totals=category_totals,
        chart_data=chart_data,
        category_filter=category_filter,
        time_filter=time_filter,
        current_month=current_month,
        current_year=current_year
    )

@app.route('/set_budget', methods=['POST'])
def set_budget():
    category_id = request.form.get('category_id')
    amount = float(request.form.get('amount'))
    today = datetime.today()

    # Check if budget exists for this category/month/year
    existing_budget = Budget.query.filter(
        Budget.category_id == category_id,
        Budget.month == today.month,
        Budget.year == today.year
    ).first()

    if existing_budget:
        existing_budget.amount = amount
    else:
        new_budget = Budget(
            category_id=category_id,
            amount=amount,
            month=today.month,
            year=today.year
        )
        db.session.add(new_budget)

    db.session.commit()
    return redirect(url_for('expenses'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form.get('description')
    amount = float(request.form.get('amount'))
    category_id = request.form.get('category_id')

    new_expense = Expense(
    description=description,
    amount=amount,
    category_id=category_id,
    timestamp=datetime.now()  # Explicitly set current timestamp
)
    db.session.add(new_expense)
    db.session.commit()
    

    # Recalculate category totals after adding the expense
    today = datetime.today()
    current_month = today.month
    current_year = today.year
    budgets = Budget.query.filter(
        Budget.month == current_month,
        Budget.year == current_year
    ).all()

    calculate_category_totals(budgets, current_month, current_year)

    return redirect(url_for('expenses'))

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('expenses'))

@app.route('/init_categories')
def init_categories():
    categories = [
        {'name': 'Food', 'color': '#FF6384'},
        {'name': 'Transport', 'color': '#36A2EB'},
        {'name': 'Entertainment', 'color': '#FFCE56'},
        {'name': 'Utilities', 'color': '#4BC0C0'},
        {'name': 'Shopping', 'color': '#9966FF'},
        {'name': 'Health', 'color': '#FF9F40'},
    ]

    for cat in categories:
        if not ExpenseCategory.query.filter_by(name=cat['name']).first():
            new_cat = ExpenseCategory(name=cat['name'], color=cat['color'])
            db.session.add(new_cat)

    db.session.commit()
    return redirect(url_for('expenses'))



@app.route('/affirmations', methods=['GET', 'POST'])
def affirmations():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            new_affirmation = Affirmation(message=message)
            db.session.add(new_affirmation)
            db.session.commit()
            return redirect(url_for('affirmations'))
    all_affirmations = Affirmation.query.all()
    return render_template('affirmations.html', affirmations=all_affirmations)



@app.route('/generate_affirmation')
def generate_affirmation():
    response = requests.get('https://www.affirmations.dev/')
    if response.status_code == 200:
        data = response.json()
        message = data.get('affirmation')
        if message:
            new_affirmation = Affirmation(message=message)
            db.session.add(new_affirmation)
            db.session.commit()
            return redirect(url_for('affirmations'))
    return "Failed to generate affirmation", 500


@app.route('/get_affirmation')
def get_affirmation():
    affirmations = Affirmation.query.all()
    if affirmations:
        random_affirmation = random.choice(affirmations).message
        return jsonify({'affirmation': random_affirmation})
    return jsonify({'affirmation': "Stay positive and keep going!"})

from flask import jsonify  # For optional JSON responses

@app.route('/activities', methods=['GET', 'POST'])
def activities():
    if request.method == 'POST':
        activity_type = request.form.get('activity_type')
        duration = request.form.get('duration')
        date = request.form.get('date')
        if activity_type and duration and date:
            new_activity = Activity(
                activity_type=activity_type,
                duration=float(duration),
                date=datetime.strptime(date, "%Y-%m-%d").date()
            )
            db.session.add(new_activity)
            db.session.commit()
            return redirect(url_for('activities'))
    all_activities = Activity.query.order_by(Activity.date.desc()).all()
    return render_template('activities.html', activities=all_activities)

@app.route('/calendar')
def calendar_view():
    tasks = Task.query.filter(Task.completed == False).all()

    events = []
    for task in tasks:
        events.append({
            'title': task.description,
            'start': task.date.strftime('%Y-%m-%d')
        })

    task_map = {}
    for task in tasks:
        date_str = task.date.strftime('%Y-%m-%d')
        task_map.setdefault(date_str, []).append(task.description)

    return render_template('calendar.html', task_map=task_map, events=events)



@app.route('/productivity_report')
def productivity_report():
    """Generate productivity charts with REAL user data"""
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Get REAL data from database
    completed_tasks = Task.query.filter(Task.completed.is_(True)).count()
    pending_tasks = Task.query.filter(Task.completed.is_(False)).count()
    
    daily_completed = Task.query.filter(
        Task.completed.is_(True),
        Task.date == today
    ).count()
    
    weekly_completed = Task.query.filter(
        Task.completed.is_(True),
        Task.date >= start_of_week
    ).count()
    
    monthly_completed = Task.query.filter(
        Task.completed.is_(True),
        Task.date >= start_of_month
    ).count()

    # Chart 1: Completion Status
    fig1 = {
        'data': [{
            'x': ['Completed', 'Pending'],
            'y': [completed_tasks, pending_tasks],
            'type': 'bar',
            'marker': {
                'color': ['#4CAF50', '#F44336']
            }
        }],
        'layout': {
            'title': 'Task Completion Status',
            'yaxis': {'title': 'Number of Tasks'}
        }
    }

    # Chart 2: Completion Over Time
    fig2 = {
        'data': [{
            'x': ['Today', 'This Week', 'This Month'],
            'y': [daily_completed, weekly_completed, monthly_completed],
            'type': 'bar',
            'marker': {
                'color': ['#2196F3', '#FF9800', '#9C27B0']
            }
        }],
        'layout': {
            'title': 'Tasks Completed Over Time',
            'yaxis': {'title': 'Tasks Completed'}
        }
    }

    print("Completed tasks:", Task.query.filter_by(completed=True).count())
    print("Pending tasks:", Task.query.filter_by(completed=False).count())

    return render_template(
        "productivity_report.html",
        chart1=fig1,
        chart2=fig2
    )


@app.route('/task_manager')
def task_manager():
    """Display tasks filtered by Today, Week, Month, or All."""
    filter_by = request.args.get('filter', 'all')
    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Apply filters based on the URL parameter
    if filter_by == 'today':
        tasks = Task.query.filter(Task.date == today).all()
    elif filter_by == 'week':
        tasks = Task.query.filter(Task.date >= start_of_week).all()
    elif filter_by == 'month':
        tasks = Task.query.filter(Task.date >= start_of_month).all()
    else:
        tasks = Task.query.order_by(Task.date).all()

    return render_template('task_manager.html', tasks=tasks, filter_by=filter_by)



import random
from flask import Flask, render_template, request



API_NINJAS_KEY = 'jwxOJEhMmeMBb65wq4Jj7Q==JFoavdqAGgs2zmah'

@app.route('/workouts', methods=['GET', 'POST'])
def workouts():
    if request.method == 'POST':
        try:
            headers = {'X-Api-Key': API_NINJAS_KEY}
            params = {'muscle': 'chest'}  # You can change this to any group like 'legs', 'back', etc.
            response = requests.get('https://api.api-ninjas.com/v1/exercises', headers=headers, params=params)

            if response.status_code == 200:
                exercises = response.json()
                if exercises:
                    workout = random.choice(exercises)
                    return render_template('workouts.html', workout=workout)
                else:
                    error = "No exercises found."
            else:
                error = f"API returned status code {response.status_code}."
        except requests.RequestException as e:
            error = f"An error occurred while fetching data: {e}"

        return render_template('workouts.html', workout=None, error=error)

    return render_template('workouts.html', workout=None)


# Default nutrition goals
DEFAULT_GOALS = {
    'calories': 2000,
    'protein': 150
}

@app.route('/nutrition', methods=['GET', 'POST'])
def nutrition():
    # Initialize session if empty
    if 'meals' not in session:
        session['meals'] = []
        session['goals'] = {'calories': 2000, 'protein': 150}
    
    # Handle form submission
    if request.method == 'POST':
        session['meals'].append({
            'food': request.form.get('food_name'),
            'calories': int(request.form.get('calories', 0)),
            'protein': int(request.form.get('protein', 0)),
            'meal_type': request.form.get('meal_type'),
            'time': datetime.now().strftime("%H:%M")
        })
        session.modified = True  # Force session save
        return redirect(url_for('nutrition'))
    
    # Calculate totals
    totals = {
        'calories': sum(m['calories'] for m in session['meals']),
        'protein': sum(m['protein'] for m in session['meals'])
    }
    
    return render_template('nutrition.html',
                        meals=session['meals'],
                        totals={
                            'calories': sum(m['calories'] for m in session['meals']),
                            'protein': sum(m['protein'] for m in session['meals'])
                        },
                        goals={'calories': 2000, 'protein': 150})

@app.route('/reset_nutrition')
def reset_nutrition():
    session['meals'] = []
    session.modified = True
    return redirect(url_for('nutrition'))

# Schedule periodic reminders
scheduler = BackgroundScheduler()
scheduler.start()
# Reminder function
def send_reminder():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reminder: Stay hydrated or stretch!")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_reminder, trigger="interval", minutes=1)  # Change interval as needed
scheduler.start()

# Shut down the scheduler when the app exits
import atexit
atexit.register(lambda: scheduler.shutdown())

import random

def send_reminder():
    messages = [
        "Stay hydrated! Drink a glass of water.",
        "Time to stretch! Take a quick break.",
        "Take a deep breath. You’re doing amazing!"
    ]
    reminder = random.choice(messages)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {reminder}")


#if __name__ == "__main__":
 #   with app.app_context():
  #      db.create_all()
   # app.run(debug=True)

