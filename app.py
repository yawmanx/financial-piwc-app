from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Data storage file
DATA_FILE = 'financial_data.json'

# Initialize data structure
def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            'income': [],
            'expenses': []
        }
        save_data(data)
    return load_data()

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'income': [], 'expenses': []}

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Reports - Euro</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        input, select, button {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s ease;
        }
        button:hover {
            transform: scale(1.05);
        }
        .stat-card {
            text-align: center;
            padding: 20px;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        .income { color: #22c55e; }
        .expense { color: #ef4444; }
        .balance { color: #3b82f6; }
        .table-container {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }
        .delete-btn {
            background: #ef4444;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            border: none;
            font-size: 12px;
        }
        .delete-btn:hover {
            background: #dc2626;
        }
        .filter-section {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .filter-section input, .filter-section select {
            flex: 1;
            min-width: 150px;
        }
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Financial Reports System</h1>
        
        <!-- Statistics Dashboard -->
        <div class="dashboard">
            <div class="card stat-card">
                <div class="stat-label">Total Income</div>
                <div class="stat-value income">€{{ "%.2f"|format(total_income) }}</div>
            </div>
            <div class="card stat-card">
                <div class="stat-label">Total Expenses</div>
                <div class="stat-value expense">€{{ "%.2f"|format(total_expenses) }}</div>
            </div>
            <div class="card stat-card">
                <div class="stat-label">Net Balance</div>
                <div class="stat-value balance">€{{ "%.2f"|format(balance) }}</div>
            </div>
        </div>

        <!-- Add Transaction Forms -->
        <div class="dashboard">
            <!-- Income Form -->
            <div class="card">
                <h2>Add Income</h2>
                <form method="POST" action="/add_income">
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" name="description" required placeholder="e.g., Salary, Freelance">
                    </div>
                    <div class="form-group">
                        <label>Amount (€)</label>
                        <input type="number" name="amount" step="0.01" required placeholder="0.00">
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select name="category" required>
                            <option value="">Select Category</option>
                            <option value="Salary">Salary</option>
                            <option value="Freelance">Freelance</option>
                            <option value="Investment">Investment</option>
                            <option value="Business">Business</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" required value="{{ today }}">
                    </div>
                    <button type="submit">Add Income</button>
                </form>
            </div>

            <!-- Expense Form -->
            <div class="card">
                <h2>Add Expense</h2>
                <form method="POST" action="/add_expense">
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" name="description" required placeholder="e.g., Groceries, Rent">
                    </div>
                    <div class="form-group">
                        <label>Amount (€)</label>
                        <input type="number" name="amount" step="0.01" required placeholder="0.00">
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select name="category" required>
                            <option value="">Select Category</option>
                            <option value="Food">Food & Dining</option>
                            <option value="Transport">Transport</option>
                            <option value="Housing">Housing</option>
                            <option value="Utilities">Utilities</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Entertainment">Entertainment</option>
                            <option value="Shopping">Shopping</option>
                            <option value="Education">Education</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" required value="{{ today }}">
                    </div>
                    <button type="submit">Add Expense</button>
                </form>
            </div>
        </div>

        <!-- Reports Section -->
        <div class="card">
            <h2>Reports & Analysis</h2>
            <div class="filter-section">
                <input type="month" id="monthFilter" value="{{ current_month }}">
                <select id="categoryFilter">
                    <option value="">All Categories</option>
                    <option value="Salary">Salary</option>
                    <option value="Food">Food & Dining</option>
                    <option value="Transport">Transport</option>
                    <option value="Housing">Housing</option>
                </select>
                <button onclick="filterTransactions()">Filter</button>
                <button onclick="exportReport()">Export CSV</button>
            </div>

            <!-- Monthly Summary -->
            <div style="margin: 20px 0;">
                <h3 style="color: #333; margin-bottom: 10px;">Monthly Summary</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    {% for month, stats in monthly_summary.items() %}
                    <div style="background: #f9fafb; padding: 15px; border-radius: 8px;">
                        <div style="font-weight: 600; color: #374151;">{{ month }}</div>
                        <div style="color: #22c55e;">Income: €{{ "%.2f"|format(stats.income) }}</div>
                        <div style="color: #ef4444;">Expenses: €{{ "%.2f"|format(stats.expenses) }}</div>
                        <div style="color: #3b82f6; font-weight: 600;">Net: €{{ "%.2f"|format(stats.income - stats.expenses) }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Category Breakdown -->
            <div style="margin: 20px 0;">
                <h3 style="color: #333; margin-bottom: 10px;">Category Breakdown (Current Month)</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px;">
                    {% for category, amount in category_breakdown.items() %}
                    <div style="background: #f3f4f6; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between;">
                        <span>{{ category }}</span>
                        <span style="font-weight: 600;">€{{ "%.2f"|format(amount) }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Recent Transactions -->
        <div class="dashboard">
            <!-- Recent Income -->
            <div class="card">
                <h2>Recent Income</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Description</th>
                                <th>Category</th>
                                <th>Amount</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in recent_income %}
                            <tr>
                                <td>{{ item.date }}</td>
                                <td>{{ item.description }}</td>
                                <td>{{ item.category }}</td>
                                <td style="color: #22c55e; font-weight: 600;">€{{ "%.2f"|format(item.amount) }}</td>
                                <td>
                                    <form method="POST" action="/delete_income" style="display: inline;">
                                        <input type="hidden" name="index" value="{{ item.index }}">
                                        <button type="submit" class="delete-btn">Delete</button>
                                    </form>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Recent Expenses -->
            <div class="card">
                <h2>Recent Expenses</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Description</th>
                                <th>Category</th>
                                <th>Amount</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in recent_expenses %}
                            <tr>
                                <td>{{ item.date }}</td>
                                <td>{{ item.description }}</td>
                                <td>{{ item.category }}</td>
                                <td style="color: #ef4444; font-weight: 600;">€{{ "%.2f"|format(item.amount) }}</td>
                                <td>
                                    <form method="POST" action="/delete_expense" style="display: inline;">
                                        <input type="hidden" name="index" value="{{ item.index }}">
                                        <button type="submit" class="delete-btn">Delete</button>
                                    </form>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        function filterTransactions() {
            const month = document.getElementById('monthFilter').value;
            const category = document.getElementById('categoryFilter').value;
            // This would typically make an AJAX call to filter data
            window.location.href = `/?month=${month}&category=${category}`;
        }

        function exportReport() {
            const month = document.getElementById('monthFilter').value;
            window.location.href = `/export?month=${month}`;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    data = load_data()
    
    # Calculate totals
    total_income = sum(float(item['amount']) for item in data['income'])
    total_expenses = sum(float(item['amount']) for item in data['expenses'])
    balance = total_income - total_expenses
    
    # Get recent transactions (last 10)
    recent_income = []
    for i, item in enumerate(reversed(data['income'][-10:])):
        item_copy = item.copy()
        item_copy['index'] = len(data['income']) - 1 - i
        recent_income.append(item_copy)
    
    recent_expenses = []
    for i, item in enumerate(reversed(data['expenses'][-10:])):
        item_copy = item.copy()
        item_copy['index'] = len(data['expenses']) - 1 - i
        recent_expenses.append(item_copy)
    
    # Calculate monthly summary (last 6 months)
    monthly_summary = defaultdict(lambda: {'income': 0, 'expenses': 0})
    for item in data['income']:
        month = item['date'][:7]
        monthly_summary[month]['income'] += float(item['amount'])
    for item in data['expenses']:
        month = item['date'][:7]
        monthly_summary[month]['expenses'] += float(item['amount'])
    
    # Sort and limit to last 6 months
    monthly_summary = dict(sorted(monthly_summary.items(), reverse=True)[:6])
    
    # Category breakdown for current month
    current_month = datetime.now().strftime('%Y-%m')
    category_breakdown = defaultdict(float)
    for item in data['expenses']:
        if item['date'].startswith(current_month):
            category_breakdown[item['category']] += float(item['amount'])
    
    return render_template_string(
        HTML_TEMPLATE,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        recent_income=recent_income,
        recent_expenses=recent_expenses,
        today=datetime.now().strftime('%Y-%m-%d'),
        current_month=current_month,
        monthly_summary=monthly_summary,
        category_breakdown=dict(category_breakdown)
    )

@app.route('/add_income', methods=['POST'])
def add_income():
    data = load_data()
    income_entry = {
        'date': request.form['date'],
        'description': request.form['description'],
        'amount': float(request.form['amount']),
        'category': request.form['category'],
        'timestamp': datetime.now().isoformat()
    }
    data['income'].append(income_entry)
    save_data(data)
    return redirect(url_for('index'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = load_data()
    expense_entry = {
        'date': request.form['date'],
        'description': request.form['description'],
        'amount': float(request.form['amount']),
        'category': request.form['category'],
        'timestamp': datetime.now().isoformat()
    }
    data['expenses'].append(expense_entry)
    save_data(data)
    return redirect(url_for('index'))

@app.route('/delete_income', methods=['POST'])
def delete_income():
    data = load_data()
    index = int(request.form['index'])
    if 0 <= index < len(data['income']):
        del data['income'][index]
        save_data(data)
    return redirect(url_for('index'))

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    data = load_data()
    index = int(request.form['index'])
    if 0 <= index < len(data['expenses']):
        del data['expenses'][index]
        save_data(data)
    return redirect(url_for('index'))

@app.route('/export')
def export_csv():
    import csv
    from flask import Response
    import io
    
    data = load_data()
    month_filter = request.args.get('month', '')
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Type', 'Date', 'Description', 'Category', 'Amount (€)'])
    
    # Write income entries
    for item in data['income']:
        if not month_filter or item['date'].startswith(month_filter):
            writer.writerow(['Income', item['date'], item['description'], item['category'], item['amount']])
    
    # Write expense entries
    for item in data['expenses']:
        if not month_filter or item['date'].startswith(month_filter):
            writer.writerow(['Expense', item['date'], item['description'], item['category'], item['amount']])
    
    # Create response
    response = Response(output.getvalue(), mimetype='text/csv')
    filename = f"financial_report_{month_filter or 'all'}.csv"
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@app.route('/api/summary')
def api_summary():
    data = load_data()
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    monthly_income = sum(float(item['amount']) for item in data['income'] if item['date'].startswith(month))
    monthly_expenses = sum(float(item['amount']) for item in data['expenses'] if item['date'].startswith(month))
    
    return jsonify({
        'month': month,
        'income': monthly_income,
        'expenses': monthly_expenses,
        'balance': monthly_income - monthly_expenses
    })

if __name__ == '__main__':
    init_data()
    # For production deployment, use a proper WSGI server like Gunicorn
    # For local testing, you can use:
    # Port 5001 is used to avoid conflicts with macOS AirPlay Receiver (port 5000)
    app.run(debug=True, host='0.0.0.0', port=5001)