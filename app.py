from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from datetime import datetime
from flask import abort
import socketio
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
socketio = SocketIO(app)

user_reports_data = [
    {
        'case_number': 'Case 1',
        'involved_parties': 'Driver: Bob, Rider: Amy',
        'report_details': 'Detailed description of the incident for Case 1.',
        'date': '01-02-2024',
        'status': 'Closed',
    },
    {
        'case_number': 'Case 2',
        'involved_parties': 'Driver: John, Rider: Mary',
        'report_details': 'Detailed description of the incident for Case 2.',
        'date': '02-02-2024',
        'status': 'Open',
    },
]

user_questions_data = [
    {'id': 1, 'user': 'user1', 'question': 'How can I offer a ride as a driver?', 'reply': None},
    {'id': 2, 'user': 'user2', 'question': 'Is there a way to book a ride as a rider?', 'reply': None},
    {'id': 3, 'user': 'user3', 'question': 'What is the maximum number of passengers allowed per ride?', 'reply': None},
]

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
    address = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    birthday = db.Column(db.Date)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active') 


    def __init__(self, username, password, address, email, age, birthday, gender, phone, role, status):
        self.username = username
        self.password = password
        self.address = address
        self.email = email
        self.age = age
        self.birthday = birthday
        self.gender = gender
        self.phone = phone
        self.role = role
        self.status = status

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rider = db.Column(db.String(20))
    driver = db.Column(db.String(20))
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.role != role:
                flash('Incorrect role selected. Please select the correct role.', 'error')
                return redirect(url_for('login'))
            
            if user.status == 'suspended':
                flash('Your account is temporarily suspended. Please contact the administrator for further assistance.', 'error')
                return redirect(url_for('login'))
            
            if user.status == 'banned':
                flash('Your account is permanently banned from the platform. Please contact the administrator for further assistance.', 'error')
                return redirect(url_for('login'))
            
            if user.status != 'active':
                flash('Your account is not active. Please contact the administrator.', 'error')
                return redirect(url_for('login'))
            
            # Store user ID, username, and role in the session
            session['user_id'] = user.id
            session['username'] = username
            session['role'] = user.role  # Set the role in the session
            
            if role == 'rider':
                return redirect(url_for('rider_dashboard'))
            elif role == 'driver':
                return redirect(url_for('driver_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))
            
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        email = request.form['email']
        age = int(request.form['age'])
        birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
        gender = request.form['gender']
        phone = request.form['phone']
        
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        # Create a new User instance
        new_user = User(
            username=username,
            password=password,
            address=address,
            email=email,
            age=age,
            birthday=birthday,
            gender=gender,
            phone=phone,
            role=role,
            status='active'
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/rider_dashboard')
def rider_dashboard():
    # Check if user is logged in
    if 'username' not in session or session['role'] != 'rider':
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
    if 'username' not in session or session['role'] != 'driver':
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
    if 'username' not in session or session['role'] != 'admin':
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
        # Update profile data
        new_username = request.form['username']
        if new_username != session['username']:
            # Update the session with the new username
            session['username'] = new_username
            user.username = new_username  # Update the user's username
            db.session.commit()  # Commit the changes to the database
            flash('Username changed successfully. Please log in again.', 'success')
            return redirect(url_for('login'))
        
        else:
            user.password = request.form['password']
            user.address = request.form['address']
            user.email = request.form['email']
            user.age = int(request.form['age'])
            user.birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
            user.gender = request.form['gender']
            user.phone = request.form['phone']
            db.session.commit()
            flash('Profile updated successfully!', 'success')
    
    return render_template('profile.html', user=user)

@app.route('/offer_ride', methods=['GET', 'POST'])
def offer_ride():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Retrieve form data
        origin = request.form['origin']
        destination = request.form['destination']
        date = request.form['date']
        time = request.form['time']
        seats_available = int(request.form['seats_available'])
        gender_preference = request.form['gender']
        
        # Create new ride instance
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
            # Handle exceptions
            print(e)
            return render_template('error.html', message="An error occurred while offering the ride. Please try again.")
    
    return render_template('offer_ride.html')

@app.route('/book_ride', methods=['GET', 'POST'])
def book_ride():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first() 

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
            return redirect(url_for('room', room=room))

    return render_template('book_ride.html',room=session.get("room"), username=user.username)


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

# FAQs page
@app.route('/faqs')
def faqs_page():
    faqs = FAQ.query.all()
    return render_template('faqs.html', faqs=faqs)

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

# Route for user reports
@app.route('/user_reports')
def user_reports():
    return render_template('user_reports.html', user_reports_data = user_reports_data)

@app.route('/user_questions')
def user_questions():
    return render_template('user_questions.html', questions=user_questions_data)

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
    session['name'] = session['username']
    username = request.args.get('username')
    gender = request.args.get('gender')
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        return redirect(url_for('privatemessage'))
    return render_template('passenger.html', username=username, gender=gender)

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
    drivers = User.query.filter_by(role='driver', gender=gender_preference).all()
    for driver in drivers:
        # Emit ride_offered event to selected drivers
        emit('ride_offered', {**data, 'ride_id': ride_id}, broadcast=True)  # Include ride_id in the data

@socketio.on('accept_ride')
def handle_accept_ride(data):
    print('Ride accepted by driver:', data)
    # Notify all clients that a ride has been accepted (you would target the specific passenger in a real app)
    emit('ride_accepted', data, broadcast=True)

rooms = {}

@socketio.on('book_ride')
def handle_book_ride(data):
    print('Received ride:', data)
    gender_preference = data.get('gender')
    # Get the ride_id from the database
    ride_id = data.get('ride_id')  # Assuming ride_id is passed from the client-side
    # Filter rider based on gender preference and role
    riders = User.query.filter_by(role='rider', gender=gender_preference).all()
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

@app.route('/reply_to_question/<int:question_id>', methods=['POST'])
def reply_to_question(question_id):
    if request.method == 'POST':
        reply = request.form.get('reply')
        # Logic to save the reply to the question with the given question_id
        return redirect(url_for('user_questions'))  # Redirect to user_questions page after replying

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables before running the app
    app.run(debug=True)

