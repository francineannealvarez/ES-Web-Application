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
    results = {}
    total = 0.0

    if 'username' not in session:
        flash("You need to be logged in to calculate the carbon footprint.")
        return redirect('/login')

    multipliers = {
        'electricity': 0.0498,
        'lpg': 0.022454,
        'water_consumption': 0.0106,
        'waste': 1.59
    }

    if request.method == 'POST':
        try:
            members = int(request.form.get("members", 1)) or 1  # Avoid division by zero
            for item, multiplier in multipliers.items():
                value = float(request.form.get(item, 0))
                if item in ['electricity', 'lpg', 'waste']:
                    value = value / members
                results[item] = value * multiplier
                total += results[item]

            # Insert into DB
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO household (
                    UserID,
                    Electricity,
                    LPG,
                    WaterConsumption,
                    Waste,
                    Total_CarbonFootprint_Household
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, 
            (
                session['user_id'],
                results.get('electricity', 0),
                results.get('lpg', 0),
                results.get('water_consumption', 0),
                results.get('waste', 0),
                total
            ))

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

    return render_template('household.html', results=results, total=total)

@app_routes.route('/calculate/category/transportation', methods=['GET', 'POST'])
def transportation():
    results = {}
    total = 0.0

    if 'username' not in session:
        flash("You need to be logged in to calculate the carbon footprint.")
        return redirect('/login')

    multipliers = {
        'gasoline': 2.31,
        'diesel': 2.68,
        'tricycle': 0.0022,
        'jeep': 0.00104,
        'van': 0.5408,
        'bus': 0.272
    }

    if request.method == 'POST':
        try:
            # Retrieve input values
            for item, multiplier in multipliers.items():
                value = float(request.form.get(item, 0))
                results[item] = value * multiplier
                total += results[item]

            # Insert into DB
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transportation (
                    UserID,
                    Gasoline_Carbon,
                    Diesel_Carbon,
                    Tricycle_Carbon,
                    Jeep_Carbon,
                    Van_Carbon,
                    Bus_Carbon,
                    Total_CarbonFootprint_Transportation
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (
                session['user_id'],
                results.get('gasoline', 0),
                results.get('diesel', 0),
                results.get('tricycle', 0),
                results.get('jeep', 0),
                results.get('van', 0),
                results.get('bus', 0),
                total
            ))

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

    return render_template('transportation.html', results=results, total=total)

@app_routes.route('/calculate/category/food', methods=['GET', 'POST'])
def food_consumption():
    results = {}
    total = 0.0

    if 'username' not in session:
        flash("You need to be logged in to calculate the carbon footprint.")
        return redirect('/login')

    food_multipliers = {
        'fresh_vegetables': 0.137,
        'beef': 60.0,
        'poultry_meat': 6.0,
        'fish': 5.0,
        'pig_meat': 7.0,
        'eggs': 4.5,
        'rice': 4.0,
        'coffee': 17.0,
        'chocolate': 19.0,
        'cheese': 21.0,
        'milk_powder': 10.1,
        'butter': 7.3
    }

    if request.method == 'POST':
        try:
            for item, multiplier in food_multipliers.items():
                kg = float(request.form.get(item, 0))
                results[item] = kg * multiplier
                total += results[item]

            # Insert into database
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO food_consumption (
                    UserID,
                    FreshVegetables_Carbon,
                    Beef_Carbon,
                    PoultryMeat_Carbon,
                    Fish_Carbon,
                    PigMeat_Carbon,
                    Eggs_Carbon,
                    Rice_Carbon,
                    Coffee_Carbon,
                    Chocolate_Carbon,
                    Cheese_Carbon,
                    MilkPowder_Carbon,
                    Butter_Carbon,
                    Total_CarbonFootprint_Food
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (
                session['user_id'],
                results.get('fresh_vegetables', 0),
                results.get('beef', 0),
                results.get('poultry_meat', 0),
                results.get('fish', 0),
                results.get('pig_meat', 0),
                results.get('eggs', 0),
                results.get('rice', 0),
                results.get('coffee', 0),
                results.get('chocolate', 0),
                results.get('cheese', 0),
                results.get('milk_powder', 0),
                results.get('butter', 0),
                total
            ))

            conn.commit()
            flash(f"Food Consumption Carbon Footprint: {total:.2f} kg CO₂")
            return redirect('/calculate/category')

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect('/calculate/category/food')

        finally:
            cursor.close()
            conn.close()

    return render_template('food_consumption.html', results=results, total=total)

