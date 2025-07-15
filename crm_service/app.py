from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///crm.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Static Bearer Token for authentication
BEARER_TOKEN = os.getenv('CRM_BEARER_TOKEN', 'your-static-bearer-token-here')

# CRM Database Models
class BookingNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    event_title = db.Column(db.String(200), nullable=False)
    event_start_time = db.Column(db.DateTime, nullable=False)
    facilitator_id = db.Column(db.Integer, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

def validate_bearer_token():
    """Validate Bearer token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    
    try:
        token_type, token = auth_header.split(' ')
        if token_type.lower() != 'bearer' or token != BEARER_TOKEN:
            return False
        return True
    except ValueError:
        return False

@app.route('/api/booking-notification', methods=['POST'])
def receive_booking_notification():
    # Validate Bearer token
    if not validate_bearer_token():
        return jsonify({'error': 'Invalid or missing Bearer token'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['booking_id', 'user', 'event', 'facilitator_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate nested required fields
    user_fields = ['id', 'email', 'name']
    event_fields = ['id', 'title', 'start_time']
    
    for field in user_fields:
        if field not in data['user']:
            return jsonify({'error': f'Missing required user field: {field}'}), 400
    
    for field in event_fields:
        if field not in data['event']:
            return jsonify({'error': f'Missing required event field: {field}'}), 400
    
    try:
        # Parse and validate start_time
        start_time = datetime.fromisoformat(data['event']['start_time'])
        
        # Store notification in database
        notification = BookingNotification(
            booking_id=data['booking_id'],
            user_id=data['user']['id'],
            user_email=data['user']['email'],
            user_name=data['user']['name'],
            event_id=data['event']['id'],
            event_title=data['event']['title'],
            event_start_time=start_time,
            facilitator_id=data['facilitator_id']
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Log the notification (in production, you might want to send emails, etc.)
        print(f"New booking notification received:")
        print(f"  Booking ID: {data['booking_id']}")
        print(f"  User: {data['user']['name']} ({data['user']['email']})")
        print(f"  Event: {data['event']['title']}")
        print(f"  Facilitator ID: {data['facilitator_id']}")
        
        return jsonify({
            'message': 'Booking notification received successfully',
            'notification_id': notification.id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    # Validate Bearer token
    if not validate_bearer_token():
        return jsonify({'error': 'Invalid or missing Bearer token'}), 401
    
    notifications = BookingNotification.query.order_by(
        BookingNotification.received_at.desc()
    ).all()
    
    return jsonify([{
        'id': n.id,
        'booking_id': n.booking_id,
        'user': {
            'id': n.user_id,
            'email': n.user_email,
            'name': n.user_name
        },
        'event': {
            'id': n.event_id,
            'title': n.event_title,
            'start_time': n.event_start_time.isoformat()
        },
        'facilitator_id': n.facilitator_id,
        'received_at': n.received_at.isoformat(),
        'processed': n.processed
    } for n in notifications])

@app.route('/api/notifications/<int:notification_id>/process', methods=['PUT'])
def mark_notification_processed(notification_id):
    # Validate Bearer token
    if not validate_bearer_token():
        return jsonify({'error': 'Invalid or missing Bearer token'}), 401
    
    notification = BookingNotification.query.get_or_404(notification_id)
    notification.processed = True
    db.session.commit()
    
    return jsonify({'message': 'Notification marked as processed'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'CRM'}), 200

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5001, host='0.0.0.0')
