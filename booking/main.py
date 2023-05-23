from flask import Flask, flash,jsonify, redirect, render_template,request,Response, session, url_for, make_response,send_from_directory
from flaskext.mysql import MySQL
import re
import hashlib
import os

app  = Flask(__name__)
mysql = MySQL()


app.secret_key = 'secret_key'

app.config['MYSQL_DATABASE_USER'] = 'stefania.deca'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Carol2019!'
app.config['MYSQL_DATABASE_DB'] = 'stefaniadeca'
app.config['MYSQL_DATABASE_HOST'] = 'ysjcs.net'

mysql.init_app(app)


conn = mysql.connect()
mycursor = conn.cursor()
cursor = conn.cursor()

accommodation_images = [
    'img0.jpg',
    'img2.jpg',
    'img4.jpg'
]

@app.route("/", methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, hashed_password,))

        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Redirect to home page
            session['loggedin'] = True
            session['username'] = username
            user_id = account[0]
            session['userid'] = user_id
            response = make_response(redirect(url_for('home')))
            response.set_cookie('user_id', str(account[0]))
            return response         
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        email = request.form['email']

                # Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, hashed_password, email,))
            conn.commit()
            msg = 'You have successfully registered! Please Login'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('user_id', '', expires=0)
    return response


@app.route('/home')
def home():
    user_id = request.cookies.get('user_id')
    if user_id:
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        return render_template('home.html', username=session['username'])
    else:
        return redirect(url_for('login'))
    

@app.route('/accommodation')
def accommodation_page():
    return render_template('accommodation.html', accommodation_images=accommodation_images)

@app.route('/delete_image/<filename>', methods=['POST'])
def delete_image(filename):
    # Construct the file path of the image
    image_path = os.path.join(app.static_folder, filename)

    if os.path.exists(image_path):
        # Delete the image file from the file system
        os.remove(image_path)

        # Remove the filename from accommodation_images list
        accommodation_images.remove(filename)

        flash('Image deleted successfully', 'success')
    else:
        flash('Image not found', 'error')

    return redirect(url_for('accommodation_page'))



@app.route('/book_vacation', methods=['POST'])
def book_vacation():
    msg=''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        adults = request.form['adults']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        userid =  session['userid'] 

    cursor.execute('INSERT INTO bookings VALUES (NULL, %s, %s, %s, %s, %s, %s,%s)', (name, email, phone,adults,checkin,checkout,userid))
    conn.commit()
    msg = 'You have successfully booked your vacation'
    # Show registration form with message (if any)
    return render_template('home.html', msg=msg)



@app.route('/profile')
def profile():
    userid =  session['userid']
    query = "SELECT * FROM bookings WHERE userid = %s"
    cursor.execute(query, (userid,))
    bookings = cursor.fetchall()
        
 # Show the profile page with account info
    return render_template('profile.html', bookings=bookings)


@app.route('/download/<path:filename>')
def download_image(filename):
    directory = os.path.join(app.root_path, 'static')  # Specify the directory where the images are stored
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/delete_booking', methods=['POST'])
def delete_booking():
   
    idbooking_del = request.form['idbooking_del']
    cursor.execute("DELETE FROM bookings WHERE id=%s", (idbooking_del,))
    conn.commit()
    
    userid =  session['userid']
    query = "SELECT * FROM bookings WHERE userid = %s"
    cursor.execute(query, (userid,))
    bookings = cursor.fetchall()
            
    # Show the profile page with account info
    return render_template('profile.html', bookings=bookings)
    



if __name__ == '__main__':
        print("== Running in debug mode ==")
        app.run(host='ysjcs.net', port=5006, debug=True)
 