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
            if password != user[5]:  # user[5] is the Password column
                flash("Incorrect password. Please try again.")
                return redirect('/login')

            # Store user ID and username in session for future actions
            session['user_id'] = user[0]  # user[0] is the UserID column
            session['username'] = user[4]  # user[4] is the Username column

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

@app_routes.route('/calculate/category')
def category_choice():
    return render_template('category_choice.html')



@app_routes.route('/calculate/full')
def full_assessment():
    # Later: Form with all categories
    return render_template('full_assessment.html')

@app_routes.route('/logout')
def logout():
    session.clear()  # This logs the user out by clearing the session
    flash("You have been logged out.")
    return redirect('/')

@app_routes.route('/calculate', methods=['POST'])
def calculate():
    pass

@app_routes.route('/history')
def history():
    pass

@app_routes.route('/calculate/category/household', methods=['GET', 'POST'])
def household():
    elec_result, lpg_result, water_consumption_result, waste_result, total = None, None, None, None, None

    if 'username' not in session:
        flash("You need to be logged in to calculate the carbon footprint.")
        return redirect('/login')

    if request.method == 'POST':
        electricity = float(request.form["electricity"])
        lpg = float(request.form["lpg"])
        water_consumption = float(request.form["water consumption"])
        waste = float(request.form["waste"])
        members = int(request.form["members"])

        # Calculate results
        elec_result = (electricity / members) * 0.0498
        lpg_result = (lpg / members) * 0.022454
        water_consumption_result = water_consumption * 0.0106
        waste_result = (waste / members) * 1.59
        total = elec_result + lpg_result + water_consumption_result + waste_result

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(""" 
            INSERT INTO household (UserID, Electricity, LPG, WaterConsumption, Waste, Total_CarbonFootprint_Household)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], elec_result, lpg_result, water_consumption_result, waste_result, total))

            conn.commit()
            flash(f"Household Carbon Footprint: {total:.2f} kg CO₂")
            return redirect('/calculate/category')

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect('/calculate/category/household')

        finally:
            cursor.close()
            conn.close()

    # Return the calculated values to the template (ensure 'total' is passed here)
    return render_template('household.html', elec_result=elec_result, lpg_result=lpg_result, waste_result=waste_result, total=total)

@app_routes.route('/calculate/category/transportation', methods=['GET', 'POST'])
def transportation():
    gasoline_result, diesel_result, tricycle_result, jeep_result, van_result, bus_result, total = None, None, None, None, None, None, None
    
    if 'username' not in session:
        flash("You need to be logged in to calculate the carbon footprint.")
        return redirect('/login')

    if request.method == 'POST':
        gasoline = float(request.form["gasoline"])
        diesel = float(request.form["diesel"])
        tricycle_expense = float(request.form["tricycle"])
        jeep_expense = float(request.form["jeep"])
        van_expense = float(request.form["van"])
        bus_expense = float(request.form["bus"])

    # Calculate results
        gasoline_result = gasoline * 2.31
        diesel_result = diesel * 2.68
        tricycle_result = tricycle_expense * 0.0022
        jeep_result = jeep_expense * 0.00104
        van_result = van_expense * 0.5408
        bus_result = bus_expense * 0.272
        total = gasoline_result + diesel_result + tricycle_result + jeep_result + van_result + bus_result
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(""" 
            INSERT INTO transportation (UserID, Gasoline_Carbon, Diesel_Carbon, Tricycle_Carbon, Jeep_Carbon, Van_Carbon, Bus_Carbon, Total_CarbonFootprint_Transportation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], gasoline_result, diesel_result, tricycle_result, jeep_result, van_result, bus_result, total))

            conn.commit()
            flash(f"Transportation Carbon Footprint: {total:.2f} kg CO₂")
            return redirect('/calculate/category')

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect('/calculate/category/transportation')

        finally:
            cursor.close()
            conn.close()

    # Return the calculated values to the template (ensure 'total' is passed here)
    return render_template('transportation.html', gasoline_result=gasoline_result, diesel_result=diesel_result, tricycle_result=tricycle_result, jeep_result=jeep_result, van_result=van_result, bus_result=bus_result, total=total)
