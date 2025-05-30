from flask import jsonify, render_template, request, redirect, flash, Blueprint, session
from db_config import get_connection
import re
from datetime import datetime
from collections import OrderedDict, defaultdict

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def home():
    return render_template('home.html')

@app_routes.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['first_name']
        mname = request.form['middle_name']
        lname = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        password_pattern = r'^(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,16}$'
        if not re.match(password_pattern, password):
            flash("Password must be 8-16 characters long and contain at least one special character.")
            return redirect('/')
        
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Check if username already exists
            cursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username already exists. Please choose a different one.")
                return redirect('/')

            cursor.execute("""
                INSERT INTO user (User_FirstName, User_MiddleName, User_LastName, Username, Password, Email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fname, mname, lname, username, password, email))

            conn.commit()
            flash("Account created successfully! You can now log in.")
            return redirect('/') 
            # Redirect to the home page after successful sign up

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect('/')

        finally:
            cursor.close()
            conn.close()

    return render_template('home.html')

@app_routes.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Password format validation before querying database
    if not re.match(r'^(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,16}$', password):
        return render_template("home.html", password_format_error="Password must be 8–16 characters and include at least one special character.")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return render_template("home.html", username_error="Username doesn't exist.")

        if password != user[5]:  
            return render_template("home.html", incorrect_password_error="Incorrect password.")

        # Successful login
        session['user_id'] = user[0]  # UserID
        session['username'] = user[4]  # Username

        flash("Login successful!")
        return redirect('/dashboard')

    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect('/')

    finally:
        cursor.close()
        conn.close()
        
@app_routes.route('/check-credentials', methods=['POST'])
def check_credentials():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "username"})

        if password != user[5]:  
            return jsonify({"error": "password"})

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": "server", "message": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


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


@app_routes.route('/logout')
def logout():
    session.clear() #logs the user out
    return redirect('/')

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
            members = int(request.form.get("members", 1)) or 1  
            for item, multiplier in multipliers.items():
                value = float(request.form.get(item, 0))
                if item in ['electricity', 'lpg', 'waste']:
                    value = value / members
                results[item] = value * multiplier
                total += results[item]

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
            flash(f"Household Carbon Footprint: {total:.2f} kg CO₂", "success")
            flash(get_recommendation('household', total), "info")
            return redirect('/dashboard')

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
            flash(f"Transportation Carbon Footprint: {total:.2f} kg CO₂", "success")
            flash(get_recommendation('transportation', total), "info")
            return redirect('/dashboard')

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
            flash(f"Food Consumption Carbon Footprint: {total:.2f} kg CO₂", "success")
            flash(get_recommendation('food', total), "info")
            return redirect('/dashboard')

        except Exception as e:
            conn.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect('/calculate/category/food')

        finally:
            cursor.close()
            conn.close()

    return render_template('food_consumption.html', results=results, total=total)

@app_routes.route('/calculate/full-assessment', methods=['GET', 'POST'])
def full_assessment():
    if 'username' not in session or 'user_id' not in session:
        flash("You need to be logged in to complete the assessment.")
        return redirect('/login')

    results = {}
    total = 0.0
    household_total = 0.0
    transportation_total = 0.0
    food_total = 0.0

    household_multipliers = {
        'electricity': 0.0498,
        'lpg': 0.022454,
        'water_consumption': 0.0106,
        'waste': 1.59
    }

    transportation_multipliers = {
        'gasoline': 2.31,
        'diesel': 2.68,
        'tricycle': 0.0022,
        'jeep': 0.00104,
        'van': 0.5408,
        'bus': 0.272
    }

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

    conn = None
    cursor = None
    if request.method == 'POST':
        try:
            # Handle member count safely
            try:
                members = int(request.form.get("members", 1))
                if members <= 0:
                    members = 1
            except ValueError:
                members = 1

            # Household
            for item, multiplier in household_multipliers.items():
                try:
                    value = float(request.form.get(item, 0))
                except ValueError:
                    value = 0.0

                if item in ['electricity', 'lpg', 'waste']:
                    value /= members
                carbon = value * multiplier
                results[item] = carbon
                household_total += carbon

            # Transportation
            for item, multiplier in transportation_multipliers.items():
                try:
                    value = float(request.form.get(item, 0))
                except ValueError:
                    value = 0.0
                carbon = value * multiplier
                results[item] = carbon
                transportation_total += carbon

            # Food Consumption
            for item, multiplier in food_multipliers.items():
                try:
                    value = float(request.form.get(item, 0))
                except ValueError:
                    value = 0.0
                carbon = value * multiplier
                results[item] = carbon
                food_total += carbon

            total = household_total + transportation_total + food_total

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO full_assessment (
                    UserID, Household_Total, Transportation_Total, Food_Consumption_Total, Overall_Total
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                session['user_id'], household_total, transportation_total, food_total, total
            ))
            conn.commit()

            flash(f"Full Assessment Submitted: {total:.2f} kg CO₂", "success")
            flash(get_recommendation('full', total), "info")
            return redirect('/dashboard')

        except Exception as e:
            if conn:
                conn.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect('/calculate/full-assessment')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("full_assessment.html", results=results, total=total)

@app_routes.route('/history', methods=['GET', 'POST'])
def view_history():
    if 'username' not in session:
        flash("You need to be logged in to view your history.")
        return redirect('/login')

    category = None
    records = []
    available_months = []
    selected_month = None
    month_map = {} 
    query_map = {
        'household': ("SELECT Electricity, LPG, WaterConsumption, Waste, Total_CarbonFootprint_Household, timestamp FROM household WHERE UserID = %s ORDER BY timestamp DESC", 'timestamp'),
        'transportation': ("SELECT Gasoline_Carbon, Diesel_Carbon, Tricycle_Carbon, Jeep_Carbon, Van_Carbon, Bus_Carbon, Total_CarbonFootprint_Transportation, timestamp FROM transportation WHERE UserID = %s ORDER BY timestamp DESC", 'timestamp'),
        'food': ("SELECT FreshVegetables_Carbon, Rice_Carbon, Eggs_Carbon, MilkPowder_Carbon, Cheese_Carbon, Butter_Carbon, Beef_Carbon, PigMeat_Carbon, PoultryMeat_Carbon, Fish_Carbon, Coffee_Carbon, Chocolate_Carbon, Total_CarbonFootprint_Food, timestamp FROM food_consumption WHERE UserID = %s ORDER BY timestamp DESC", 'timestamp'),
        'assessment': ("SELECT Household_Total, Transportation_Total, Food_Consumption_Total, Overall_Total, Full_AssessmentDate FROM full_assessment WHERE UserID = %s ORDER BY Full_AssessmentDate DESC", 'Full_AssessmentDate')
    }

    if request.method == 'POST':
        
      user_id = session['user_id']
      category = request.form.get('category')

    # Only read month if it exists in the form and category is not just newly selected
      selected_month = request.form.get('month') if 'month' in request.form else None

    if category in query_map:
        query, date_col = query_map[category]
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            all_records = cursor.fetchall()

            # Group by year-month (ex. 2025 May)
            month_map = defaultdict(list)
            for record in all_records:
                raw_date = record[date_col]
                month_year_str = raw_date.strftime("%Y %B")
                month_map[month_year_str].append(record)

            available_months = sorted(month_map.keys(), key=lambda x: datetime.strptime(x, "%Y %B"))

            if selected_month in month_map:
                records = month_map[selected_month]
            else:
                selected_month = None
                records = []

        except Exception as e:
            flash(f"Database error: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    else:
        flash("Invalid category selected.")

        
    return render_template(
        'view_history.html',
        category=category,
        available_months=available_months,
        selected_month=selected_month,
        records=records,
        month_map=month_map
        )
    
    
def get_recommendation(category, total):
    if category == 'household':
        if total < 50:
            return "Great job! Your household carbon footprint is very low."
        elif total < 150:
            return "Your household footprint is moderate. Consider saving energy and reducing waste."
        else:
            return "Your household footprint is high. Try switching to energy-efficient appliances and limiting water use."
    
    elif category == 'transportation':
        if total < 100:
            return "You're doing well with transportation emissions!"
        elif total < 250:
            return "Your transportation emissions are moderate. Try carpooling or using public transport more."
        else:
            return "Your transportation emissions are high. Consider reducing vehicle use or switching to greener options."
    
    elif category == 'food':
        if total < 50:
            return "Excellent! Your diet has a low environmental impact."
        elif total < 150:
            return "Your food emissions are average. Try reducing meat and dairy consumption."
        else:
            return "High food emissions. Consider more plant-based meals and reducing food waste."
    
    elif category == 'full':
        if total < 200:
            return "Fantastic! Your total carbon footprint is impressively low."
        elif total < 600:
            return "Your overall emissions are average. Keep looking for ways to reduce further."
        else:
            return "Your overall emissions are high. A shift toward sustainable habits could make a big difference."

    return "No recommendation available."
