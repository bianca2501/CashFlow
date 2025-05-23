from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)

# File paths - ensure these are in the correct directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPENSE_FILE = os.path.join(BASE_DIR, 'expenses.csv')
TODO_FILE = os.path.join(BASE_DIR, 'todo.txt')
INCOME_FILE = os.path.join(BASE_DIR, 'income.txt')

# Create files if they don't exist
for file in [EXPENSE_FILE, TODO_FILE, INCOME_FILE]:
    if not os.path.exists(file):
        open(file, 'a').close()

# ========== UTILITY FUNCTIONS ==========
def read_expenses():
    expenses = []
    if os.path.exists(EXPENSE_FILE) and os.path.getsize(EXPENSE_FILE) > 0:
        with open(EXPENSE_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            expenses = list(reader)
    return expenses

def add_expense(category, amount, note=""):
    file_exists = os.path.exists(EXPENSE_FILE) and os.path.getsize(EXPENSE_FILE) > 0
    with open(EXPENSE_FILE, mode='a', newline='') as file:
        fieldnames = ['Date', 'Category', 'Amount', 'Note']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            'Date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'Category': category,
            'Amount': float(amount),
            'Note': note
        })

def read_income():
    try:
        with open(INCOME_FILE, 'r') as f:
            content = f.read().strip()
            return float(content) if content else 0.0
    except (FileNotFoundError, ValueError):
        return 0.0

def save_income(income):
    with open(INCOME_FILE, 'w') as f:
        f.write(str(income))

def read_todo():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def add_todo_task(task):
    with open(TODO_FILE, 'a') as f:
        f.write(task.strip() + "\n")

def delete_todo_task(index):
    tasks = read_todo()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        with open(TODO_FILE, 'w') as f:
            f.write("\n".join(tasks))

# ========== ROUTES ==========
@app.route('/')
def dashboard():
    expenses = read_expenses()
    income = read_income()
    todo_list = read_todo()

    # Total expense calculation
    total_expense = sum(float(row['Amount']) for row in expenses) if expenses else 0
    remaining = income - total_expense

    # Category breakdown
    categories = {}
    for row in expenses:
        cat = row['Category']
        categories[cat] = categories.get(cat, 0) + float(row['Amount'])

    return render_template('dashboard.html',
                         expenses=expenses[-3:],
                         income=income,
                         total_expense=total_expense,
                         remaining=remaining,
                         todo_list=todo_list[-3:],
                         categories=categories)

@app.route('/expenses')
def expenses():
    expenses = read_expenses()
    total_expense = sum(float(row['Amount']) for row in expenses) if expenses else 0
    
    # Category breakdown
    categories = {}
    for row in expenses:
        cat = row['Category']
        categories[cat] = categories.get(cat, 0) + float(row['Amount'])

    return render_template('expenses.html',
                         expenses=expenses,
                         total_expense=total_expense,
                         categories=categories)

@app.route('/todo')
def todo():
    todo_list = read_todo()
    return render_template('todo.html',
                         todo_list=todo_list)

@app.route('/add_expense', methods=['POST'])
def add_expense_route():
    category = request.form['category']
    amount = request.form['amount']
    note = request.form.get('note', '')
    add_expense(category, amount, note)
    return redirect(url_for('expenses'))

@app.route('/set_income', methods=['POST'])
def set_income():
    income = float(request.form['income'])
    save_income(income)
    return redirect(url_for('dashboard'))

@app.route('/add_todo', methods=['POST'])
def add_todo():
    task = request.form['task']
    add_todo_task(task)
    return redirect(url_for('todo'))

@app.route('/delete_todo/<int:index>')
def delete_todo(index):
    delete_todo_task(index)
    return redirect(url_for('todo'))

if __name__ == '__main__':
    app.run(debug=True)