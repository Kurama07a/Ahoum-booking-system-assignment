from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import logging
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///notifications.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Static Bearer Token for backend authentication
BACKEND_BEARER_TOKEN = os.getenv('BACKEND_SERVICE_TOKEN', 'backend-service-token-here')

# Store online facilitators and their socket IDs
online_facilitators = {}  # {facilitator_id: socket_id}
backend_socket_id = None

# Database Models
class StoredNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facilitator_id = db.Column(db.Integer, nullable=False)
    booking_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    session_title = db.Column(db.String(200), nullable=False)
    session_start_time = db.Column(db.DateTime, nullable=False)
    message_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered = db.Column(db.Boolean, default=False)

class FacilitatorSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facilitator_id = db.Column(db.Integer, nullable=False)
    socket_id = db.Column(db.String(100), nullable=False)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

# WebSocket Events

@socketio.on('connect')
def handle_connect(auth):
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected', 'socket_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    
    # Remove from online facilitators if it was a facilitator
    facilitator_to_remove = None
    for fac_id, socket_id in online_facilitators.items():
        if socket_id == request.sid:
            facilitator_to_remove = fac_id
            break
    
    if facilitator_to_remove:
        del online_facilitators[facilitator_to_remove]
        logger.info(f"Facilitator {facilitator_to_remove} went offline")
        
        # Update database
        session = FacilitatorSession.query.filter_by(
            facilitator_id=facilitator_to_remove, 
            socket_id=request.sid
        ).first()
        if session:
            db.session.delete(session)
            db.session.commit()
    
    # Check if it was the backend service
    global backend_socket_id
    if backend_socket_id == request.sid:
        backend_socket_id = None
        logger.info("Backend service disconnected")

@socketio.on('backend_connect')
def handle_backend_connect(data):
    """Handle backend service connection"""
    token = data.get('token')
    if token != BACKEND_BEARER_TOKEN:
        emit('auth_error', {'error': 'Invalid token'})
        return
    
    global backend_socket_id
    backend_socket_id = request.sid
    join_room('backend')
    logger.info(f"Backend service connected: {request.sid}")
    emit('backend_auth_success', {'status': 'authenticated'})

@socketio.on('facilitator_connect')
def handle_facilitator_connect(data):
    """Handle facilitator connection"""
    facilitator_id = data.get('facilitator_id')
    token = data.get('token')  # JWT token from facilitator
    
    if not facilitator_id:
        emit('auth_error', {'error': 'Facilitator ID required'})
        return
    
    # In production, validate the JWT token here
    # For now, we'll accept any facilitator_id
    
    # Store facilitator as online
    online_facilitators[facilitator_id] = request.sid
    join_room(f'facilitator_{facilitator_id}')
    
    # Store in database
    existing_session = FacilitatorSession.query.filter_by(facilitator_id=facilitator_id).first()
    if existing_session:
        existing_session.socket_id = request.sid
        existing_session.last_seen = datetime.utcnow()
    else:
        new_session = FacilitatorSession(
            facilitator_id=facilitator_id,
            socket_id=request.sid
        )
        db.session.add(new_session)
    
    db.session.commit()
    
    logger.info(f"Facilitator {facilitator_id} connected: {request.sid}")
    emit('facilitator_auth_success', {
        'status': 'authenticated',
        'facilitator_id': facilitator_id
    })
    
    # Send any pending notifications
    send_pending_notifications(facilitator_id)

@socketio.on('booking_notification')
def handle_booking_notification(data):
    """Handle booking notification from backend"""
    if request.sid != backend_socket_id:
        emit('error', {'error': 'Unauthorized'})
        return
    
    try:
        # Validate required fields
        required_fields = ['booking_id', 'user', 'session', 'facilitator_id']
        for field in required_fields:
            if field not in data:
                emit('notification_error', {'error': f'Missing field: {field}'})
                return
        
        facilitator_id = data['facilitator_id']
        
        # Prepare notification message
        notification_message = {
            'type': 'new_booking',
            'booking_id': data['booking_id'],
            'user': data['user'],
            'session': data['session'],
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"New booking from {data['user']['name']} for {data['session']['title']}"
        }
        
        # Check if facilitator is online
        if facilitator_id in online_facilitators:
            # Send real-time notification
            socket_id = online_facilitators[facilitator_id]
            socketio.emit('new_booking_notification', notification_message, room=socket_id)
            logger.info(f"Real-time notification sent to facilitator {facilitator_id}")
            
            # Confirm delivery to backend
            emit('notification_delivered', {
                'booking_id': data['booking_id'],
                'facilitator_id': facilitator_id,
                'delivered_at': datetime.utcnow().isoformat()
            })
        else:
            # Store notification for offline facilitator
            stored_notification = StoredNotification(
                facilitator_id=facilitator_id,
                booking_id=data['booking_id'],
                user_name=data['user']['name'],
                user_email=data['user']['email'],
                session_title=data['session']['title'],
                session_start_time=datetime.fromisoformat(data['session']['start_time']),
                message_data=json.dumps(notification_message)
            )
            
            db.session.add(stored_notification)
            db.session.commit()
            
            logger.info(f"Notification stored for offline facilitator {facilitator_id}")
            
            # Confirm storage to backend
            emit('notification_stored', {
                'booking_id': data['booking_id'],
                'facilitator_id': facilitator_id,
                'stored_at': datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error handling booking notification: {str(e)}")
        emit('notification_error', {'error': str(e)})

@socketio.on('get_pending_notifications')
def handle_get_pending_notifications(data):
    """Get pending notifications for a facilitator"""
    facilitator_id = data.get('facilitator_id')
    
    if facilitator_id not in online_facilitators or online_facilitators[facilitator_id] != request.sid:
        emit('error', {'error': 'Unauthorized'})
        return
    
    send_pending_notifications(facilitator_id)

@socketio.on('mark_notification_read')
def handle_mark_notification_read(data):
    """Mark a notification as read"""
    facilitator_id = data.get('facilitator_id')
    notification_id = data.get('notification_id')
    
    if facilitator_id not in online_facilitators or online_facilitators[facilitator_id] != request.sid:
        emit('error', {'error': 'Unauthorized'})
        return
    
    notification = StoredNotification.query.filter_by(
        id=notification_id,
        facilitator_id=facilitator_id
    ).first()
    
    if notification:
        notification.delivered = True
        db.session.commit()
        emit('notification_marked_read', {'notification_id': notification_id})

def send_pending_notifications(facilitator_id):
    """Send all pending notifications to a facilitator"""
    pending_notifications = StoredNotification.query.filter_by(
        facilitator_id=facilitator_id,
        delivered=False
    ).order_by(StoredNotification.created_at.desc()).all()
    
    if pending_notifications:
        notifications_data = []
        for notification in pending_notifications:
            message_data = json.loads(notification.message_data)
            message_data['notification_id'] = notification.id
            message_data['stored_at'] = notification.created_at.isoformat()
            notifications_data.append(message_data)
        
        emit('pending_notifications', {
            'notifications': notifications_data,
            'count': len(notifications_data)
        })
        
        logger.info(f"Sent {len(notifications_data)} pending notifications to facilitator {facilitator_id}")

# HTTP endpoints for health check and stats
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'notification_service',
        'timestamp': datetime.utcnow().isoformat(),
        'online_facilitators': len(online_facilitators),
        'backend_connected': backend_socket_id is not None
    }), 200

@app.route('/stats')
def get_stats():
    total_stored = StoredNotification.query.count()
    undelivered = StoredNotification.query.filter_by(delivered=False).count()
    
    return {
        'online_facilitators': len(online_facilitators),
        'backend_connected': backend_socket_id is not None,
        'total_notifications': total_stored,
        'pending_notifications': undelivered,
        'facilitator_sessions': FacilitatorSession.query.count()
    }

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    socketio.run(app, debug=True, port=5002, host='0.0.0.0', allow_unsafe_werkzeug=True)
