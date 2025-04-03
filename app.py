from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    calorie_goal = db.Column(db.Integer, default=2000)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food = db.Column(db.String(100))
    quantity = db.Column(db.Float)
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    time = db.Column(db.String(20))
    date = db.Column(db.String(20))

# Dummy food DB
food_db = {
    'Boiled Egg': {'calories': 155, 'protein': 13, 'carbs': 1.1, 'fats': 11},
    'Paneer': {'calories': 265, 'protein': 18, 'carbs': 6, 'fats': 20},
    'Cooked Chickpeas': {'calories': 164, 'protein': 9, 'carbs': 27, 'fats': 2.6},
    'Tofu': {'calories': 144, 'protein': 15, 'carbs': 3.9, 'fats': 8},
    'Soya Chunks': {'calories': 345, 'protein': 52, 'carbs': 33, 'fats': 0.5},
    'Greek Yogurt': {'calories': 59, 'protein': 10, 'carbs': 3.6, 'fats': 0.4},
    'Protein Shake': {'calories': 120, 'protein': 26, 'carbs': 2, 'fats': 1}
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/home')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    today = datetime.now().strftime("%Y-%m-%d")
    today_meals = Meal.query.filter_by(user_id=user.id, date=today).all()
    total_calories = sum(m.calories for m in today_meals)
    return render_template('index.html', food_db=food_db, meals=today_meals, time=datetime.now().strftime('%H:%M'), today=today, total_calories=total_calories, goal=user.calorie_goal)

@app.route('/add', methods=['POST'])
def add_meal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    food = request.form['food']
    quantity = float(request.form['quantity'])
    factor = quantity / 100
    user = User.query.get(session['user_id'])
    if food in food_db:
        data = food_db[food]
        meal = Meal(
            user_id=user.id,
            food=food,
            quantity=quantity,
            calories=round(data['calories'] * factor, 1),
            protein=round(data['protein'] * factor, 1),
            carbs=round(data['carbs'] * factor, 1),
            fats=round(data['fats'] * factor, 1),
            time=request.form['time'],
            date=datetime.now().strftime("%Y-%m-%d")
        )
        db.session.add(meal)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    last_7_days = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    data = []
    for d in last_7_days:
        total = db.session.query(db.func.sum(Meal.calories)).filter_by(user_id=user_id, date=d).scalar() or 0
        data.append(round(total, 1))
    return render_template('dashboard.html', labels=last_7_days, data=data)

@app.route('/set_goal', methods=['POST'])
def set_goal():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        user.calorie_goal = int(request.form['goal'])
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists('meals.db'):
        with app.app_context():
            db.create_all()
            
    app.run(host = 0.0.0.0, debug=False, port=5001)
