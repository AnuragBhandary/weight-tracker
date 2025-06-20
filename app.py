from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('weights.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight REAL NOT NULL,
                date TEXT NOT NULL
              )
        ''')
    conn.commit()
    conn.close()

def get_weekly_averages():
    conn = sqlite3.connect('weights.db')
    c = conn.cursor()
    c.execute("SELECT date, weight FROM weights ORDER BY date ASC")
    data = c.fetchall()
    conn.close()

    weekly_data = defaultdict(list)

    for date_str, weight in data:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        start_of_week = date_obj - timedelta(days = date_obj.weekday()) # Monday start
        end_of_week = start_of_week + timedelta(days = 6)
        week_key = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"

        weekly_data[week_key].append(weight)

    weekly_averages = []
    for week, weights in weekly_data.items():
        avg = round(sum(weights) / len(weights), 2)
        weekly_averages.append((week, avg))

    return weekly_averages

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        weight = request.form['weight']
        date = request.form['date']

        conn = sqlite3.connect('weights.db')
        c = conn.cursor()
        c.execute("INSERT INTO weights (weight, date) VALUES (?, ?)", (weight, date))
        conn.commit()
        conn.close()

        return redirect('/')
    
    conn = sqlite3.connect('weights.db')
    c = conn.cursor()
    c.execute("SELECT * FROM weights ORDER BY date DESC")
    data = c.fetchall()
    conn.close()

    weekly_averages = get_weekly_averages()

    dates = [row[2] for row in data]
    weight_values = [row[1] for row in data]

    return render_template(
        'index.html',
         weights = data,
         weekly_averages = weekly_averages,
         chart_dates = dates,
         chart_weights = weight_values
        )

@app.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    conn = sqlite3.connect('weights.db')
    c = conn.cursor()
    c.execute("DELETE FROM WEIGHTS WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    init_db()
    app.run(host = '0.0.0.0', port = 10000)