from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from datetime import datetime, timedelta, timezone
from flask import abort
from flask_mail import Mail, Message
import socketio
from sqlalchemy.orm import relationship
from flask_login import current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server address
app.config['MAIL_PORT'] = 587  # Port for SMTP (usually 587 for TLS)
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USERNAME'] = 'choozifeng29@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'mavs gdgn nrcv fcno'  # Your SMTP password
db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app)

# Define your models
class Report(db.Model):
    case_number = db.Column(db.Integer, primary_key=True)
    report_details = db.Column(db.String(255))
    reporting_user_username = db.Column(db.String(50))  
    reported_user_username = db.Column(db.String(50)) 
    date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Open')

    def __init__(self, report_details, reporting_user_username, reported_user_username, date, status):
        self.report_details = report_details
        self.reporting_user_username = reporting_user_username
        self.reported_user_username = reported_user_username
        self.date = date
        self.status = status


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(50))  
    user_type = db.Column(db.String(10))  # 'driver' or 'rider'
    question_text = db.Column(db.String(200))
    answer_text = db.Column(db.String(200), nullable=True)

# Model for FAQs
class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

# Define User and Ride models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    addresses = db.relationship('Address', backref='user', lazy=True)
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active') 
    book_status = db.Column(db.String(20), nullable=False, default='not_book')
    emergency_contacts = db.relationship('Emergency_Contact', backref='user', lazy=True)


    def __init__(self, username, password, email, age, birthday, gender, phone, role, status, book_status):
        self.username = username
        self.password = password
        self.email = email
        self.age = age
        self.birthday = birthday
        self.gender = gender
        self.phone = phone
        self.role = role
        self.status = status
        self.book_status = book_status
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def init(self, name, address, user_id):
        self.name = name
        self.address = address
        self.user_id = user_id

class Emergency_Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def init(self, name, phone, user_id):
        self.name = name
        self.phone = phone
        self.user_id = user_id

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rider = db.Column(db.String(20))
    driver = db.Column(db.String(20), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    gender_preference = db.Column(db.String(10))
    rider_response = db.Column(db.String(10))
    # Define relationship with RidePassenger
    passengers = relationship('RidePassenger', backref='ride', lazy=True)

class RidePassenger(db.Model):
    __tablename__ = 'ride_passenger'
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define relationship to User
    user = db.relationship('User', foreign_keys=[passenger_id])

    def __init__(self, ride_id, passenger_id):
        self.ride_id = ride_id
        self.passenger_id = passenger_id

# Define the Car model
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    license_plate = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, make, model, year, license_plate, user_id):
        self.make = make
        self.model = model
        self.year = year
        self.license_plate = license_plate
        self.user_id = user_id

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    rated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    review = db.Column(db.Text, nullable=True)

@app.route('/')
def index():
    return render_template('index.html')

# Function to generate OTP
def generate_otp():
    return str(random.randint(1000, 9999))

# Function to send OTP (You need to implement this)
def send_otp(email, otp):
    # Mail Title
    msg = Message('Forgot Password OTP', sender='choozifeng29@gmail.com', recipients=[email])
    # Mail Message Body
    msg.body = f"Your OTP for password reset is: {otp}"
    mail.send(msg)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        # Check if username & email is match with the database
        user = User.query.filter_by(username=username_or_email).first() or User.query.filter_by(email=username_or_email).first()

        if user:
            # Generate OTP
            otp = generate_otp()

            session['reset_username'] = user.username

            session['reset_otp'] = otp
            session['otp_timestamp'] = datetime.now()  # Current time

            send_otp(user.email, otp)

            flash('An OTP has been sent to your email. Please check and enter it below.', 'info')
            return redirect(url_for('verify_otp'))
        else:
            flash('Username or email not found. Please try again.', 'error')

    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_username' not in session or 'reset_otp' not in session:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        otp = request.form['otp']

        if otp == session['reset_otp']:
            # Ensure current time is in UTC timezone
            now = datetime.now(timezone.utc)

            otp_timestamp = session.get('otp_timestamp')
            if otp_timestamp and now - otp_timestamp <= timedelta(minutes=1):
                # OTP is valid and not expired
                session['reset_otp_verified'] = True
                return redirect(url_for('reset_password'))
            else:
                # OTP has expired
                flash('OTP has expired. Please request a new one.', 'error')
        else:
            # Invalid OTP
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify_otp.html')
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # not session['reset_otp_verified'] means the session['reset_otp_verified'] = false; otp is not verified
    if 'reset_username' not in session or 'reset_otp_verified' not in session or not session['reset_otp_verified']:
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        user = User.query.filter_by(username=session['reset_username']).first()
        if user:
            user.password = new_password
            db.session.commit()
            flash('Password reset successful! You can now log in with your new password.', 'success')

            session.pop('reset_username')
            session.pop('reset_otp')
            session.pop('reset_otp_verified')
            return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.status == 'suspended':
                flash('Your account is temporarily suspended. Please contact the administrator for further assistance.', 'error')
                return redirect(url_for('login'))

            if user.status == 'banned':
                flash('Your account is permanently banned from the platform. Please contact the administrator for further assistance.', 'error')
                return redirect(url_for('login'))

            if user.status != 'active':
                flash('Your account is not active. Please contact the administrator.', 'error')
                return redirect(url_for('login'))
            
            session['username'] = username
            if username == 'Admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('driver_or_rider'))

        else:
                flash('Invalid username or password. Please try again.', 'error')
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        email = request.form['email']
        age = request.form['age']
        birthday = request.form['birthday']
        gender = request.form['gender']
        phone = request.form['phone']
        emergency_phone = request.form['emergency_phone']
        
        # Store form data in session, to prevent keep on re-enter the information after occurs error message
        session['form_data'] = {
            'username': username,
            'password': password,
            'address': address,
            'email': email,
            'age': age,
            'birthday': birthday,
            'gender': gender,
            'phone': phone,
            'emergency_phone': emergency_phone
        }
        
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        # Check if the email already exists in the database
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        existing_phone = User.query.filter_by(phone=phone).first()
        if existing_phone:
            flash('Phone already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        # Create a new User instance
        new_user = User(
            username=username,
            password=password,
            email=email,
            age=int(age) if age else None,  # Convert age to int if provided
            birthday=datetime.strptime(birthday, '%Y-%m-%d').date() if birthday else None,  # Parse birthday if provided
            gender=gender,
            phone=phone,
            role='',
            status='active',
            book_status='not_book'
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Create a new Address instance for the user's address
        new_address = Address(
            name='Registered Address',
            address=address,
            user_id=new_user.id
        )
        db.session.add(new_address)
        
        # Create a new EmergencyContact instance for the user's emergency contact
        new_emergency_contact = Emergency_Contact(
            name='Registered Emergenct Contact',
            phone=emergency_phone,
            user_id=new_user.id
        )
        db.session.add(new_emergency_contact)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        session.pop('form_data')  # Clear form data from session
        return redirect(url_for('login'))
    
    # Check if there is form data stored in session
    form_data = session.get('form_data', {})
    return render_template('register.html', form_data=form_data)

@app.route('/logout')
def logout():
    if 'username' in session:
        # Fetch the user from the database
        user = User.query.filter_by(username=session['username']).first()

        # Check if the user exists and update the role to empty
        if user:
            user.role = ''
            db.session.commit()

    # Clear the username from the session
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/driver_or_rider', methods=['GET', 'POST'])
def driver_or_rider():
    if request.method == 'POST':
        role = request.form.get('role')  
        session['role'] = role
        user = User.query.filter_by(username=session['username']).first()
        user.role = role
        db.session.commit()
        print("Role updated successfully:", role)  # Add a debug print
        return redirect(url_for('driver_dashboard' if role == 'Driver' else 'rider_dashboard'))

    return render_template('driver_or_rider.html', username=session['username'])

@app.route('/rider_dashboard')
def rider_dashboard():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    # Fetch user from the database
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        error_message = "User not found"
        return render_template('rider_dashboard.html', error_message=error_message)
    
    # Fetch ride requests for the current rider
    ride_requests = Ride.query.filter_by(rider_response=None).all()
    rides = Ride.query.filter_by(rider=session['username']).all()

    
    return render_template('rider_dashboard.html', username=user.username, ride_requests=ride_requests, gender=user.gender, rides=rides)
    

@app.route('/driver_dashboard')
def driver_dashboard():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Fetch user from the database
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        error_message = "User not found"
        return render_template('driver_dashboard.html', error_message=error_message)
    
    # Fetch rides offered by the current user
    rides = Ride.query.filter_by(driver=session['username']).all()
    return render_template('driver_dashboard.html', username=user.username, gender=user.gender, rides=rides)

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Fetch user from the database
    user = User.query.filter_by(username=session['username']).first()   
    return render_template('admin_dashboard.html', username=user.username)

@app.route('/settings')
def settings():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Fetch user from the database
    user = User.query.filter_by(username=session['username']).first()
    
    # Fetch car associated with the user
    car = Car.query.filter_by(user_id=user.id).first()
    
    return render_template('settings.html', username=session['username'], car=car)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Fetch user from the database
    user = User.query.filter_by(username=session['username']).first()
    
    if request.method == 'POST':
        # Get form data
        new_username = request.form['username']
        new_email = request.form['email']
        new_phone = request.form['phone']
        
        # Check if the new username is already in use
        existing_user_with_username = User.query.filter(User.username == new_username, User.id != user.id).first()
        if existing_user_with_username:
            flash('Username already exists. Please choose a different one.', 'error')
        
        # Check if the new email is already in use
        existing_user_with_email = User.query.filter(User.email == new_email, User.id != user.id).first()
        if existing_user_with_email:
            flash('Email already exists. Please choose a different one.', 'error')
            
        # Check if the new username is already in use
        existing_user_with_phone = User.query.filter(User.phone == new_phone, User.id != user.id).first()
        if existing_user_with_phone:
            flash('Phone already exists. Please choose a different one.', 'error')
        
    # Update profile data
        if new_username != session['username']:
            # Update the session with the new username
            session['username'] = new_username
            user.username = new_username
            db.session.commit()  # Commit the changes to the database
            flash('Username changed successfully. Please log in again.', 'success')
            return redirect(url_for('login'))
        
        user.password = request.form['password']
        user.email = new_email
    
        # Allow age to be empty
        user.age = request.form['age']
        user.age = int(user.age) if user.age else None

        # Allow birthday to be empty
        user.birthday = request.form['birthday']
        user.birthday = datetime.strptime(user.birthday, '%Y-%m-%d').date() if user.birthday else None
            
        user.gender = request.form['gender']
        user.phone = new_phone        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    return render_template('profile.html', user=user)

@app.route('/saved_address', methods=['GET', 'POST'])
def saved_address():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        
        new_address = Address(
            name=name, 
            address=address, 
            user_id=user.id
        )
        db.session.add(new_address)
        db.session.commit()
        flash('Address added successfully!', 'success')
        return redirect(url_for('saved_address'))

    return render_template('saved_address.html', user=user)

# int:address_id is a converter to specify address_id should be integer
@app.route('/edit_address/<int:address_id>', methods=['GET', 'POST'])
# Adrress passed as an argument to the edit_address() function depending on method of Post/Get
def edit_address(address_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get the user object from the database
    user = User.query.filter_by(username=session['username']).first()

    # Get the address object from the database based on address_id and user_id
    address = Address.query.filter_by(id=address_id, user_id=user.id).first()

    if request.method == 'POST':
        address.name = request.form['name']
        address.address = request.form['address']
        db.session.commit()
        flash('Address updated successfully!', 'success')
        return redirect(url_for('saved_address'))
    
    # Render the edit_address.html template with the address object
    return render_template('edit_address.html', address=address)

@app.route('/emergency_contact', methods=['GET', 'POST'])
def emergency_contact():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        if len(user.emergency_contacts) >= 3:
            flash('You already have the maximum number of emergency contacts.', 'error')
            return redirect(url_for('emergency_contact'))

        name = request.form['name']
        phone = request.form['phone']
        
        # Create a new EmergencyContact instance for the user's emergency contact
        new_contact = Emergency_Contact(
            name=name,
            phone=phone,
            user_id=user.id
        )
        db.session.add(new_contact)
        db.session.commit()
        flash('Emergency contact added successfully!', 'success')
        return redirect(url_for('emergency_contact'))

    return render_template('emergency_contact.html', user=user)

@app.route('/edit_emergency_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_emergency_contact(contact_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch the user from the database
    user = User.query.filter_by(username=session['username']).first()

    # Fetch the emergency contact to be edited
    contact = Emergency_Contact.query.filter_by(id=contact_id, user_id=user.id).first()

    if not contact:
        flash('Emergency contact not found.', 'error')
        return redirect(url_for('emergency_contact'))

    if request.method == 'POST':
        # Update contact information with the user's input
        contact.name = request.form['name']
        contact.phone = request.form['phone']
        
        # Commit changes to the database
        db.session.commit()

        flash('Emergency contact updated successfully!', 'success')
        return redirect(url_for('emergency_contact'))

    return render_template('edit_emergency_contact.html', contact=contact)

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'username' in session:
        # Fetch the user from the database
        user = User.query.filter_by(username=session['username']).first()
    
        # Check if the user exists
        if user:
            # Delete associated addresses first by user.id
            Address.query.filter_by(user_id=user.id).delete()
            
            # Delete associated emergency_contact first by user.id
            Emergency_Contact.query.filter_by(user_id=user.id).delete()
            
            # Delete the user
            db.session.delete(user)
            db.session.commit()

            # Clear the session data
            session.clear()

            flash('Your account has been deleted successfully.', 'success')
            return redirect(url_for('index'))

    flash('Failed to delete the account. Please try again later.', 'error')
    return redirect(url_for('settings'))

@app.route('/offer_ride', methods=['GET', 'POST'])
def offer_ride():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        origin = request.form['origin']
        destination = request.form['destination']
        date = request.form['date']
        time = request.form['time']
        seats_available = int(request.form['seats_available'])
        new_ride = Ride(
            driver=session['username'],
            origin=origin,
            destination=destination,
            date=date,
            time=time,
            seats_available=seats_available
        )
        try:
            db.session.add(new_ride)
            db.session.commit()
            return redirect(url_for('driver_dashboard'))
        except Exception as e:
            # Log the exception for debugging
            print(e)
            return render_template('error.html', message="An error occurred while offering the ride. Please try again.")
    return render_template('offer_ride.html')

@app.route('/book_ride', methods=['GET', 'POST'])
def book_ride():
    if 'username' not in session:
        return redirect(url_for('login'))
    username=session['username'] 

    if request.method == 'POST':
        
        action = request.form.get('action')
        if action == 'bookRide':
            origin = request.form['origin']
            destination = request.form['destination']
            date = request.form['date']
            time = request.form['time']
            seats_available = int(request.form['seats_available'])
            gender_preference = request.form['gender']
            new_ride = Ride(
                driver=session['username'],
                origin=origin,
                destination=destination,
                date=date,
                time=time,
                seats_available=seats_available,
                gender_preference=gender_preference
            )
            try:
                db.session.add(new_ride)
                db.session.commit()
                # Pass the ride_id to the client as a JSON response
                return jsonify({'ride_id': new_ride.id})
            except Exception as e:
                # Log the exception for debugging
                print(e)
                return render_template('error.html', message="An error occurred while offering the ride. Please try again.")
        
        elif action == 'privateMessage':  
            session['name'] = session['username']  
            return redirect(url_for('room', room=room))

    return render_template('book_ride.html',room=session.get("room"), username=username)


@app.route('/view_route/<int:id>')
def view_route(id):
    if id == 0:
        # Handle the case where the ride ID is 0
        return render_template('error.html', message="Invalid ride ID")
    
    ride = Ride.query.get(id)
    if ride is None:
        # Handle the case where the ride with the specified ID does not exist
        return render_template('error.html', message="Ride not found")

    origin = ride.origin
    destination = ride.destination

    return render_template('view_route.html', origin=origin, destination=destination)

@app.route('/car_detail', methods=['GET', 'POST'])
def car_detail():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        license_plate = request.form['license_plate']
        
        # Retrieve the username from the session
        username = session.get('username')
        
        # Ensure username is set in the session
        if username is None:
            # Handle case where username is not set in session
            # Redirect to login or handle the error accordingly
            return redirect(url_for('login'))
        
        # Find the user based on the username
        user = User.query.filter_by(username=username).first()
        
        # Ensure user exists
        if user is None:
            # Handle case where user does not exist
            # Redirect to login or handle the error accordingly
            return redirect(url_for('login'))
        
        # Retrieve the user ID associated with the user
        user_id = user.id
        
        # Create a new car with the retrieved user ID
        new_car = Car(make=make, model=model, year=year, license_plate=license_plate, user_id=user_id)
        db.session.add(new_car)
        db.session.commit()
        
        return redirect(url_for('car_added_successfully'))  # Redirect to success page or any other route
        
    return render_template('car_detail.html')

@app.route('/car_added_successfully')
def car_added_successfully():
    return '''Car added successfully!<br>
            <a href="{}">Back to Driver Dashboard</a>'''.format(url_for('driver_dashboard'))

@app.route('/view_car/<int:car_id>')
def view_car(car_id):
    car = Car.query.get(car_id)
    return render_template('view_car.html', car=car)

@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    car = Car.query.get(car_id)
    if request.method == 'POST':
        car.make = request.form['make']
        car.model = request.form['model']
        car.year = request.form['year']
        car.license_plate = request.form['license_plate']
        db.session.commit()
        return redirect(url_for('view_car', car_id=car.id))
    return render_template('view_car.html', car=car)

@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    car = Car.query.get(car_id)
    db.session.delete(car)
    db.session.commit()
    return redirect(url_for('driver_dashboard'))

# FAQs page for admin
@app.route('/faqs')
def faqs_page():
    faqs = FAQ.query.all()
    return render_template('faqs.html', faqs=faqs)

# FAQs page for user
@app.route('/view_faq')
def view_faq():
    faqs = FAQ.query.all()
    return render_template('view_faq.html', faqs=faqs)

# Route for adding a new FAQ
@app.route('/add_faq', methods=['GET', 'POST'])
def add_faq():
    if request.method == 'POST':
        new_faq = FAQ(
            question=request.form['question'],
            answer=request.form['answer']
        )
        try:
            db.session.add(new_faq)
            db.session.commit()
            return redirect(url_for('faqs_page'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding FAQ: {str(e)}")
    return render_template('add_faq.html')

# Define a teardown function to remove the database session at the end of each request
@app.teardown_request
def teardown_request(exception=None):
    db.session.remove()
    

# Route for user management
@app.route('/user_management')
def user_management():
    users = User.query.all()
    return render_template('user_management.html', users=users)

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'POST':
        user = User.query.filter_by(username=session['username']).first()
        user_username = request.form['user_username']
        user_type = request.form['user_type']
        question_text = request.form['question_text']

        question = Question(user_username=user_username,user_type=user_type, question_text=question_text)
        db.session.add(question)
        db.session.commit()

        return redirect(url_for('driver_dashboard' if user.role == 'Driver' else 'rider_dashboard'))

    return render_template('ask_question.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        question_id = request.form['question_id']
        answer_text = request.form['answer_text']

        question = Question.query.get(question_id)
        question.answer_text = answer_text
        db.session.commit()

        return redirect(url_for('admin_panel'))

    questions = Question.query.all()
    return render_template('admin_panel.html', questions=questions)

@app.route('/view_questions')
def view_questions():
    username = session.get('username')
    if username:
        # Retrieve questions asked by the current user
        questions = Question.query.filter_by(user_username=username).all()
        # Render the view_questions.html template and pass the questions data to it
        return render_template('view_questions.html', questions=questions)
    else:
        # Handle case where user is not logged in
        return redirect(url_for('login'))  # Redirect to login page or handle as appropriate
    
@app.route('/rate_review', methods=['GET', 'POST'])
def rate_review():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        ride_id = request.form['ride_id']
        rating = request.form['rating']
        review = request.form['review']

        # Get the user ID from the session
        user_id = session.get('user_id')

        # Ensure that user_id is not None
        if user_id is None:
            flash('User ID not found. Please log in again.', 'error')
            return redirect(url_for('login'))

        # Ensure that the rated_user_id is different from the user_id (person providing the rating)
        rated_user_id = request.form['rated_user_id']
        if rated_user_id == user_id:
            flash('You cannot rate yourself.', 'error')
            return redirect(url_for('rate_review'))

        # Save rating and review to the database
        new_rating = Rating(
            ride_id=ride_id,
            rated_by_id=user_id,
            rated_user_id=rated_user_id,
            rating=rating
        )
        new_review = Review(
            ride_id=ride_id,
            reviewed_by_id=user_id,
            reviewed_user_id=rated_user_id,
            review=review
        )
        db.session.add(new_rating)
        db.session.add(new_review)
        db.session.commit()

        flash('Rating and review submitted successfully!', 'success')

        # Determine the dashboard route based on the user's role
        if user.role == 'driver':
            return redirect(url_for('driver_dashboard'))
        elif user.role == 'rider':
            return redirect(url_for('rider_dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin_dashboard'))

    else:
        # Fetch rides where the user is either the driver or one of the passengers
        rides = Ride.query.filter(
            (Ride.driver == user.username) |
            (Ride.passengers.any(passenger_id=user.id))
        ).all()

        # Extract unique usernames of all participants in these rides
        users = set()
        for ride in rides:
            users.add(ride.driver)
            for passenger in ride.passengers:
                # Access username through associated User object
                users.add(passenger.user.username)

        return render_template('rate_review.html', rides=rides, users=users)

@app.route('/passenger', methods=['GET', 'POST'])
def passenger():
    if request.method == 'POST':
        return redirect(url_for('privatemessage'))
    return render_template('passenger.html')

@app.route('/driver', methods=['GET', 'POST'])
def driver():
    username = request.args.get('username')
    gender = request.args.get('gender')
    
    # Redirect if POST request (assuming room is correctly set in the session)
    if request.method == 'POST':
        room = session.get("room", "default_room")  # Use a default room or handle appropriately
        return redirect(url_for('room', room=room))

    # Ensure the session has a unique room assigned
    if 'room' in session:
        current_room = session['room']
        
        # Safely check if the room exists and has less than 2 members
        room_info = rooms.get(current_room)
        if room_info is not None and room_info.get('members', 0) < 2:
            room_info['members'] += 1
        else:
            # Room is full or does not exist, create and assign a new room
            new_room = generate_unique_code()
            rooms[new_room] = {'members': 1, 'messages': []}
            session['room'] = new_room
    else:
        # No room assigned in session, create a new one
        new_room = generate_unique_code()
        rooms[new_room] = {'members': 1, 'messages': []}
        session['room'] = new_room

    # Render the driver's page with the room information
    return render_template('driver.html', room=session['room'], username=username, gender=gender)

@socketio.on('offer_ride')
def handle_offer_ride(data):
    print('Received offer_ride:', data)
    gender_preference = data.get('gender')
    # Get the ride_id from the database
    ride_id = data.get('ride_id')  # Assuming ride_id is passed from the client-side
    # Filter drivers based on gender preference and role
    drivers = User.query.filter_by(role='Driver', gender=gender_preference).all()
    for driver in drivers:
        # Emit ride_offered event to selected drivers
        emit('ride_offered', {**data, 'ride_id': ride_id}, broadcast=True)  # Include ride_id in the data
rooms = {}

@socketio.on('accept_ride')
def handle_accept_ride(data):
    print('Ride accepted by driver:', data)
    # Notify all clients that a ride has been accepted (you would target the specific passenger in a real app)
    emit('ride_accepted', data, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    print(f"User {request.sid} has joined the room: {room}")
    emit('room_joined', {'room': room, 'message': f'Welcome to room {room}'}, to=room)



@socketio.on('book_ride')
def handle_book_ride(data):
    print('Received ride:', data)
    gender_preference = data.get('gender')
    # Get the ride_id from the database
    ride_id = data.get('ride_id')  # Assuming ride_id is passed from the client-side
    # Filter rider based on gender preference and role
    riders = User.query.filter_by(role='Rider', gender=gender_preference).all()
    for rider in riders:
        # Emit ride_offered event to selected rider
        emit('offer_ride_offered', {**data, 'ride_id': ride_id}, broadcast=True)  # Include ride_id in the data

@socketio.on('accept_offer_ride')
def handle_accept_offer_ride(data):
    print('Ride accepted by rider:', data)
    ride_id = data.get('ride_id')
    ride = Ride.query.get(ride_id)
    if ride:
        ride.rider = data.get('rider')  # 
        db.session.commit()
        emit('offer_ride_accepted', data, broadcast=True)  # Emit ride_accepted event to the rider
    else:
        print('Ride with ID {} not found'.format(ride_id))

@socketio.on('cancel_ride')
def handle_cancel_ride(data):
    print('cancel ride', data)
    emit('ride_cancel', data, broadcast=True)

@app.route('/check_for_ride_requests')
def check_for_ride_requests():
    # Query the database to get a list of new ride requests
    ride_requests = Ride.query.filter_by(rider_response=None).all()
    # Convert ride requests to a list of dictionaries
    ride_requests_data = [{
        'id': ride.id,
        'origin': ride.origin,
        'destination': ride.destination
    } for ride in ride_requests]
    return jsonify(ride_requests_data)

def generate_unique_code(length=4):
    import string
    return ''.join(random.choices(string.ascii_uppercase, k=length))

@app.route("/privatemessage", methods=["POST", "GET"])
def privatemessage():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("privatemessage.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("privatemessage.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("privatemessage.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("privatemessage.html")

@app.route("/room")
def room():
    room = session.get("room")
    name = session.get("name")
    print(session.get("room"))
    print(name)
    messages = []
    if room and room in rooms:
        messages = rooms[room].get("messages", [])

    return render_template("room.html", room=room, messages=messages)

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
         if room not in rooms:
            rooms[room] = {"members": 0, "messages": []}
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    leave_room(room)
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")
    
# Route to activate user
@app.route('/activate_user/<int:user_id>')
def activate_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'active'
        db.session.commit()
    return redirect(url_for('user_management'))

# Route to suspend user
@app.route('/suspend_user/<int:user_id>')
def suspend_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'suspended'
        db.session.commit()
    return redirect(url_for('user_management'))

# Route to ban user
@app.route('/ban_user/<int:user_id>')
def ban_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'banned'
        db.session.commit()
    return redirect(url_for('user_management'))

@app.route('/make_report', methods=['GET', 'POST'])
def make_report():
    if request.method == 'POST':
        # Handle POST request
        report_details = request.form['report_details']
        reported_user_username = request.form['reported_user_username']
        reporting_user_username = request.form['reporting_user_username']
        date_str = request.form['date']
        role = request.form.get('role')
        session['role'] = role
        user = User.query.filter_by(username=session['username']).first()
        user.role = role
        
        # Converts date string to datetime object
        date = datetime.strptime(date_str, '%d/%m/%Y')
        
        # Assuming 'status' defaults to 'open'
        status = 'open'

        # Insert the report into the database
        with app.app_context():
            report = Report(report_details=report_details, 
                            reporting_user_username=reporting_user_username,
                            reported_user_username=reported_user_username,
                            date=date,
                            status=status)
            db.session.add(report)
            db.session.commit()

        flash("Report submitted successfully.", 'success')
        return redirect(url_for('driver_dashboard' if user.role == 'Driver' else 'rider_dashboard'))

    # Handle GET request or rendering the form
    return render_template('make_report.html', users=User.query.all(), now=datetime.now())

@app.route('/report_submitted')
def report_submitted():
    return 'Report submitted successfully.'

@app.route('/user_reports', methods=['GET', 'POST'])
def user_reports():
    # Fetch all reports from the database
    user_reports_data = Report.query.all()
    
    if request.method == 'POST':
        # Handle form submission to update report status
        for report in user_reports_data:
            status_key = f"status_{report.case_number}"
            new_status = request.form.get(status_key)
            # Update the status of the report in the database
            report_obj = Report.query.filter_by(case_number=report.case_number).first()
            if report_obj:
                report_obj.status = new_status
                db.session.commit()
        # Redirect to the same page after processing the form
        return redirect(url_for('user_reports'))
    else:
        # Handle GET request to render the user_reports.html template
        return render_template('user_reports.html', user_reports_data=user_reports_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True)
        
