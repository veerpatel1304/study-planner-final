from flask import Flask, render_template, request, redirect, url_for
from database.db import get_db_connection

app = Flask(__name__)

# Secret key is needed for session management (placeholder)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    """
    Home page route.
    """
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route. Handles both GET (show form) and POST (submit form).
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Placeholder authentication logic
        # In a real app, you would hash the password and check against the database
        print(f"Login attempt: Email={email}, Password={password}")
        
        # For now, just redirect to dashboard upon "success"
        if email and password:
            return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route. Handles both GET (show form) and POST (submit form).
    """
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Placeholder registration logic
        # In a real app, you would validate inputs and insert into the database
        print(f"Register attempt: Name={name}, Email={email}")
        
        if password != confirm_password:
            # In a real app, show an error message
            print("Passwords do not match!")
        else:
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """
    Dashboard route. Protected area for logged-in users.
    """
    # In a real app, check if user is logged in
    return render_template('dashboard.html')

# Machine Learning Integration (Future)
# model_path = 'models/study_plan_model.pkl'
# def recommend_study_plan(user_data):
#     # Load model and predict
#     pass

if __name__ == '__main__':
    app.run(debug=True)
