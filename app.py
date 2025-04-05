"""from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.secret_key = "supersecretkey"

# In-memory user store
users = {}

# Flask-Mail config (update with your credentials or use Mailtrap for testing)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'yourpassword'         # Replace with your password
mail = Mail(app)

# Token generator
s = URLSafeTimedSerializer(app.secret_key)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in users:
            flash('Username already exists!', 'error')
        else:
            users[username] = {'password': password, 'email': email, 'verified': False}
            token = s.dumps(email, salt='email-confirm')
            link = url_for('confirm_email', token=token, _external=True)
            print(f'Verification link: {link}')  # For testing in console

            # Send email
            msg = Message('Confirm your email', sender='youremail@gmail.com', recipients=[email])
            msg.body = f'Click the link to confirm your email: {link}'
            mail.send(msg)

            flash('A verification email has been sent. Please check your inbox.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # 1 hour token
        # Mark user as verified
        for user in users:
            if users[user]['email'] == email:
                users[user]['verified'] = True
                flash('Email verified successfully! You can now log in.', 'success')
                break
    except SignatureExpired:
        flash('The verification link has expired.', 'error')

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            if user['verified']:
                flash('Login successful!', 'success')
            else:
                flash('Please verify your email before logging in.', 'error')
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
"""

import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Flask-Mail config (update with your credentials or use Mailtrap for testing)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youremail@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'yourpassword'         # Replace with your password
mail = Mail(app)

# In-memory user store
users = {}

# Token generator
s = URLSafeTimedSerializer(app.secret_key)

# Function to generate a random verification code
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))  # 6-digit code

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if username in users:
            flash('Username already exists!', 'error')
        else:
            # Generate verification code
            verification_code = generate_verification_code()
            
            # Store user information temporarily with a "not verified" status
            users[username] = {'password': password, 'email': email, 'verified': False, 'verification_code': verification_code}

            # Send verification code to the user's email
            msg = Message('Email Verification Code', sender='youremail@gmail.com', recipients=[email])
            msg.body = f'Your verification code is: {verification_code}'
            mail.send(msg)

            flash('A verification code has been sent to your email.', 'success')

            return redirect(url_for('verify_email', username=username))

    return render_template('signup.html')

@app.route('/verify_email/<username>', methods=['GET', 'POST'])
def verify_email(username):
    if request.method == 'POST':
        entered_code = request.form['verification_code']
        
        # Check if the entered code matches the one sent to the user
        if users[username]['verification_code'] == entered_code:
            users[username]['verified'] = True
            flash('Email verified successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid verification code. Please try again.', 'error')

    return render_template('verify_email.html', username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        
        if user and user['password'] == password:
            if user['verified']:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Please verify your email before logging in.', 'error')
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
