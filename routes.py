from flask import render_template, request, redirect, flash, Blueprint, session
from db_config import get_connection
import hashlib

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def home():
    return render_template('home.html')


@app_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Collect form data
        fname = request.form['first_name']
        mname = request.form['middle_name']
        lname = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Connect to the database
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Check if username already exists
            cursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username already exists. Please choose a different one.")
                return redirect('/signup')

            # Insert new user into the database 
            cursor.execute("""
                INSERT INTO user (User_FirstName, User_MiddleName, User_LastName, Username, Password, Email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fname, mname, lname, username, password, email))

            conn.commit()
            flash("Account created successfully! You can now log in.")

            # Redirect to the home page after successful sign up
            return redirect('/')

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect('/signup')

        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')


@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Check if the username exists
            cursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                flash("Username not found. Please try again.")
                return redirect('/login')

            # Verify the password (no hashing since you're storing it plain text)
            if password != user[5]:  
                flash("Incorrect password. Please try again.")
                return redirect('/login')

            # If everything is correct, store the user info in the session
            session['user_id'] = user[0]  # Save the user ID to the session
            session['username'] = user[3]  # Save the username to the session

            flash("Login successful!")
            return redirect('/dashboard')

        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return redirect('/login')

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')


@app_routes.route('/dashboard')
def dashboard():
    # Check if the user is logged in (if there's a user_id in the session)
    if 'user_id' not in session:
        flash("You must log in first!")
        return redirect('/login')

   
    return render_template('dashboard.html')

@app_routes.route('/calculate', methods=['POST'])
def calculate():
    pass

@app_routes.route('/history')
def history():
    pass
