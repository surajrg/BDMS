from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'lifedrop_secret_key_change_in_production'

# ── Simple JSON-based "database" ──────────────────────────────────────────────
# Stores users in a local file: users.json
# For production, replace this with a real database (SQLite, PostgreSQL, etc.)

USERS_FILE = 'users.json'

def load_users():
    """Load all users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Save all users to the JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        phone    = request.form.get('phone', '').strip()
        blood    = request.form.get('blood', '').strip()
        city     = request.form.get('city', '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation
        if not all([name, phone, blood, city, password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        users = load_users()

        # Check if phone already registered
        for user in users:
            if user['phone'] == phone:
                flash('This phone number is already registered. Please login.', 'error')
                return render_template('register.html')

        # Save new user
        new_user = {
            'name':     name,
            'phone':    phone,
            'blood':    blood,
            'city':     city.title(),   # capitalize city name
            'password': password        # NOTE: store hashed in production!
        }
        users.append(new_user)
        save_users(users)

        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()

        if not phone or not password:
            flash('Phone and password are required.', 'error')
            return render_template('login.html')

        users = load_users()

        for user in users:
            if user['phone'] == phone and user['password'] == password:
                session['user_phone'] = phone
                session['user_name']  = user['name']
                flash(f"Welcome back, {user['name']}!", 'success')
                return redirect(url_for('index'))

        flash('Invalid phone number or password.', 'error')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        blood = request.form.get('blood', '').strip()
        city  = request.form.get('city', '').strip().title()

        if not blood or not city:
            flash('Please select a blood group and enter a city.', 'error')
            return render_template('search.html')

        users = load_users()

        # Filter donors by blood group and city (case-insensitive city match)
        results = [
            u for u in users
            if u['blood'] == blood and u['city'].lower() == city.lower()
        ]

        return render_template('result.html', results=results, blood=blood, city=city)

    return render_template('search.html')


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
