from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import text
import requests
import os
import atexit
from functools import wraps
from websocket_client import initialize_notification_client, send_booking_notification, cleanup_notification_client

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///booking_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# CRM Service Configuration
CRM_SERVICE_URL = os.getenv('CRM_SERVICE_URL', 'http://localhost:5001')
CRM_BEARER_TOKEN = os.getenv('CRM_BEARER_TOKEN', 'your-static-bearer-token-here')

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'facilitator'
    google_id = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Facilitator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.Text)
    specialization = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to User
    user = db.relationship('User', backref='facilitator_profile')
    sessions = db.relationship('Session', backref='facilitator', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    facilitator_id = db.Column(db.Integer, db.ForeignKey('facilitator.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # 'session' or 'retreat'
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # 'active', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='session', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    booking_status = db.Column(db.String(20), default='confirmed')  # 'confirmed', 'cancelled'
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

# Helper Functions
def role_required(role):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = int(get_jwt_identity())
            user = User.query.get(current_user_id)
            if not user or user.role != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def notify_facilitator_websocket(booking_data):
    """Notify facilitator via WebSocket"""
    try:
        success = send_booking_notification(booking_data)
        return success
    except Exception as e:
        print(f"WebSocket notification failed: {e}")
        return False

# Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        name=data['name'],
        role=data.get('role', 'user')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create facilitator profile if role is facilitator
    if user.role == 'facilitator':
        facilitator = Facilitator(
            user_id=user.id,
            bio=data.get('bio', ''),
            specialization=data.get('specialization', '')
        )
        db.session.add(facilitator)
        db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/google', methods=['POST'])
def google_login():
    """Handle Google OAuth login"""
    data = request.get_json()
    google_id = data.get('google_id')
    email = data.get('email')
    name = data.get('name')
    
    if not all([google_id, email, name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
        else:
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                role='user'
            )
            db.session.add(user)
        db.session.commit()
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role
        }
    })

# Session Routes
@app.route('/api/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    sessions = Session.query.filter_by(status='active').all()
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'description': s.description,
        'facilitator': s.facilitator.user.name,
        'session_type': s.session_type,
        'start_time': s.start_time.isoformat(),
        'end_time': s.end_time.isoformat(),
        'capacity': s.capacity,
        'price': s.price,
        'available_spots': s.capacity - len(s.bookings)
    } for s in sessions])

@app.route('/api/sessions', methods=['POST'])
@role_required('facilitator')
def create_session():
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    if not facilitator:
        return jsonify({'error': 'Facilitator profile not found'}), 404
    
    session = Session(
        title=data['title'],
        description=data.get('description', ''),
        facilitator_id=facilitator.id,
        session_type=data['session_type'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        capacity=data.get('capacity', 1),
        price=data.get('price', 0.0)
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'message': 'Session created successfully', 'session_id': session.id}), 201

@app.route('/api/sessions/<int:session_id>', methods=['PUT'])
@role_required('facilitator')
def update_session(session_id):
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    session = Session.query.get_or_404(session_id)
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    if session.facilitator_id != facilitator.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update session fields
    for field in ['title', 'description', 'session_type', 'capacity', 'price']:
        if field in data:
            setattr(session, field, data[field])
    
    if 'start_time' in data:
        session.start_time = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data:
        session.end_time = datetime.fromisoformat(data['end_time'])
    
    db.session.commit()
    return jsonify({'message': 'Session updated successfully'})

@app.route('/api/sessions/<int:session_id>/cancel', methods=['POST'])
@role_required('facilitator')
def cancel_session(session_id):
    current_user_id = int(get_jwt_identity())
    session = Session.query.get_or_404(session_id)
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    if session.facilitator_id != facilitator.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    session.status = 'cancelled'
    
    # Cancel all bookings for this session
    for booking in session.bookings:
        booking.booking_status = 'cancelled'
    
    db.session.commit()
    return jsonify({'message': 'Session cancelled successfully'})

@app.route('/api/facilitator/sessions/<int:session_id>', methods=['DELETE'])
@role_required('facilitator')
def delete_session(session_id):
    current_user_id = int(get_jwt_identity())
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    session = Session.query.get_or_404(session_id)
    
    if session.facilitator_id != facilitator.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Cancel all bookings for this session
    for booking in session.bookings:
        booking.booking_status = 'cancelled'
    
    # Mark session as cancelled instead of deleting
    session.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Session cancelled successfully'})

# Booking Routes
@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    session = Session.query.get_or_404(data['session_id'])
    
    # Check if session is available
    if session.status != 'active':
        return jsonify({'error': 'Session is not available'}), 400
    
    # Check capacity
    if len(session.bookings) >= session.capacity:
        return jsonify({'error': 'Session is fully booked'}), 400
    
    # Check if user already booked this session
    existing_booking = Booking.query.filter_by(
        user_id=current_user_id,
        session_id=session.id,
        booking_status='confirmed'
    ).first()
    
    if existing_booking:
        return jsonify({'error': 'You have already booked this session'}), 400
    
    booking = Booking(
        user_id=current_user_id,
        session_id=session.id,
        notes=data.get('notes', '')
    )
    
    db.session.add(booking)
    db.session.commit()
    
    # Get current user for notification
    current_user = User.query.get(current_user_id)
    
    # Notify facilitator via WebSocket
    crm_data = {
        'booking_id': booking.id,
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'name': current_user.name
        },
        'session': {
            'id': session.id,
            'title': session.title,
            'start_time': session.start_time.isoformat()
        },
        'facilitator_id': session.facilitator_id
    }

    notify_facilitator_websocket(crm_data)
    
    return jsonify({'message': 'Booking created successfully', 'booking_id': booking.id}), 201

@app.route('/api/bookings/my', methods=['GET'])
@jwt_required()
def get_my_bookings():
    current_user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([{
        'id': b.id,
        'session': {
            'id': b.session.id,
            'title': b.session.title,
            'start_time': b.session.start_time.isoformat(),
            'end_time': b.session.end_time.isoformat(),
            'facilitator': b.session.facilitator.user.name
        },
        'booking_status': b.booking_status,
        'booking_date': b.booking_date.isoformat(),
        'notes': b.notes
    } for b in bookings])

@app.route('/api/facilitator/bookings', methods=['GET'])
@role_required('facilitator')
def get_facilitator_bookings():
    current_user_id = int(get_jwt_identity())
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    if not facilitator:
        return jsonify({'error': 'Facilitator profile not found'}), 404
    
    bookings = db.session.query(Booking).join(Session).filter(
        Session.facilitator_id == facilitator.id
    ).all()
    
    return jsonify([{
        'id': b.id,
        'user': {
            'id': b.user.id,
            'name': b.user.name,
            'email': b.user.email
        },
        'session': {
            'id': b.session.id,
            'title': b.session.title,
            'start_time': b.session.start_time.isoformat()
        },
        'booking_status': b.booking_status,
        'booking_date': b.booking_date.isoformat(),
        'notes': b.notes
    } for b in bookings])

# Facilitator Dashboard Routes
@app.route('/api/facilitator/dashboard', methods=['GET'])
@role_required('facilitator')
def get_facilitator_dashboard():
    current_user_id = int(get_jwt_identity())
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    if not facilitator:
        return jsonify({'error': 'Facilitator profile not found'}), 404
    
    # Get all sessions for this facilitator
    sessions = Session.query.filter_by(facilitator_id=facilitator.id).all()
    
    # Get all bookings for this facilitator's sessions
    bookings = db.session.query(Booking).join(Session).filter(
        Session.facilitator_id == facilitator.id,
        Booking.booking_status == 'confirmed'
    ).all()
    
    # Calculate metrics
    total_sessions = len(sessions)
    active_sessions = len([s for s in sessions if s.status == 'active'])
    total_bookings = len(bookings)
    
    # Calculate revenue
    total_revenue = sum(b.session.price for b in bookings)
    
    # Get upcoming sessions
    now = datetime.utcnow()
    upcoming_sessions = [s for s in sessions if s.start_time > now and s.status == 'active']
    
    # Get recent bookings (last 10)
    recent_bookings = db.session.query(Booking).join(Session).filter(
        Session.facilitator_id == facilitator.id
    ).order_by(Booking.booking_date.desc()).limit(10).all()
    
    return jsonify({
        'metrics': {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'upcoming_sessions': len(upcoming_sessions)
        },
        'recent_bookings': [{
            'id': b.id,
            'user': {
                'name': b.user.name,
                'email': b.user.email
            },
            'session': {
                'title': b.session.title,
                'start_time': b.session.start_time.isoformat()
            },
            'booking_date': b.booking_date.isoformat(),
            'status': b.booking_status
        } for b in recent_bookings]
    })

@app.route('/api/facilitator/sessions', methods=['GET'])
@role_required('facilitator')
def get_facilitator_sessions():
    current_user_id = int(get_jwt_identity())
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    if not facilitator:
        return jsonify({'error': 'Facilitator profile not found'}), 404
    
    sessions = Session.query.filter_by(facilitator_id=facilitator.id).all()
    
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'description': s.description,
        'session_type': s.session_type,
        'start_time': s.start_time.isoformat(),
        'end_time': s.end_time.isoformat(),
        'capacity': s.capacity,
        'price': s.price,
        'status': s.status,
        'bookings_count': len(s.bookings),
        'available_spots': s.capacity - len([b for b in s.bookings if b.booking_status == 'confirmed']),
        'created_at': s.created_at.isoformat()
    } for s in sessions])

@app.route('/api/facilitator/sessions/<int:session_id>/bookings', methods=['GET'])
@role_required('facilitator')
def get_session_bookings(session_id):
    current_user_id = int(get_jwt_identity())
    facilitator = Facilitator.query.filter_by(user_id=current_user_id).first()
    
    session = Session.query.get_or_404(session_id)
    
    if session.facilitator_id != facilitator.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bookings = Booking.query.filter_by(session_id=session_id).all()
    
    return jsonify([{
        'id': b.id,
        'user': {
            'id': b.user.id,
            'name': b.user.name,
            'email': b.user.email
        },
        'booking_status': b.booking_status,
        'booking_date': b.booking_date.isoformat(),
        'notes': b.notes
    } for b in bookings])

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1')).scalar()
        db_status = 'connected'
    except Exception as e:
        db_status = 'disconnected'
        print(f"Database connection error: {e}")
    
    return jsonify({
        'status': 'healthy',
        'service': 'backend',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status
    }), 200

# Initialize database
def initialize_services():
    create_tables()
    initialize_notification_client()

# Cleanup on shutdown
atexit.register(cleanup_notification_client)

def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create sample data
        if not User.query.first():
            # Create sample facilitator
            facilitator_user = User(
                email='facilitator@example.com',
                password_hash=generate_password_hash('password123'),
                name='John Doe',
                role='facilitator'
            )
            db.session.add(facilitator_user)
            db.session.commit()
            
            facilitator = Facilitator(
                user_id=facilitator_user.id,
                bio='Experienced meditation teacher',
                specialization='Mindfulness & Wellness'
            )
            db.session.add(facilitator)
            db.session.commit()
            
            # Create sample sessions
            sample_sessions = [
                {
                    'title': 'Morning Meditation',
                    'description': 'Start your day with peaceful meditation',
                    'session_type': 'session',
                    'start_time': datetime.now() + timedelta(days=1),
                    'end_time': datetime.now() + timedelta(days=1, hours=1),
                    'capacity': 10,
                    'price': 25.0
                },
                {
                    'title': 'Weekend Retreat',
                    'description': 'Two-day wellness retreat',
                    'session_type': 'retreat',
                    'start_time': datetime.now() + timedelta(days=7),
                    'end_time': datetime.now() + timedelta(days=9),
                    'capacity': 5,
                    'price': 200.0
                }
            ]
            
            for session_data in sample_sessions:
                session = Session(
                    facilitator_id=facilitator.id,
                    **session_data
                )
                db.session.add(session)
            
            db.session.commit()

if __name__ == '__main__':
    initialize_services()
    app.run(debug=True, port=5000, host='0.0.0.0')
