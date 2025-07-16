# Notification Service Documentation

## Overview

The Notification Service is a real-time WebSocket-based microservice designed to handle instant notifications between the booking system backend and facilitators. It provides real-time communication capabilities, offline message storage, and reliable notification delivery for the booking system ecosystem.

## Architecture & Technology Stack

- **Framework**: Flask with Flask-SocketIO
- **Real-time Communication**: WebSocket connections via Socket.IO
- **Database**: SQLAlchemy with SQLite (configurable to PostgreSQL)
- **Message Storage**: Persistent storage for offline notifications
- **Authentication**: Bearer token for backend service, JWT support for facilitators

## Core Functionality

### 1. Real-time Notification Delivery
- Instant WebSocket-based notifications to online facilitators
- Automatic fallback to persistent storage for offline facilitators
- Bidirectional communication between backend service and facilitators

### 2. Offline Message Storage
- Stores notifications when facilitators are offline
- Delivers pending notifications when facilitators reconnect
- Maintains message history with delivery status tracking

### 3. Connection Management
- Tracks online facilitators and their socket connections
- Manages backend service connection authentication
- Handles reconnection scenarios gracefully

## Service Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///notifications.db
BACKEND_SERVICE_TOKEN=backend-service-token-here
```

### Default Configuration
- **Port**: 5002
- **Host**: 0.0.0.0 (all interfaces)
- **CORS**: Enabled for all origins
- **Debug Mode**: Enabled in development

## WebSocket Events & Communication Protocol

### Backend Service Events

#### 1. Backend Connection
**Event**: `backend_connect`

**Purpose**: Authenticate and establish connection from the backend service.

**Request Data**:
```json
{
  "token": "backend-service-token-here"
}
```

**Response Events**:
- `backend_auth_success`: Authentication successful
- `auth_error`: Authentication failed

**Business Logic**:
- Validates the provided token against `BACKEND_SERVICE_TOKEN`
- Stores the backend socket ID for future communication
- Joins the backend to a special 'backend' room

#### 2. Booking Notification
**Event**: `booking_notification`

**Purpose**: Send new booking notifications to facilitators.

**Request Data**:
```json
{
  "booking_id": 123,
  "user": {
    "id": 5,
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "session": {
    "id": 1,
    "title": "Morning Meditation",
    "start_time": "2024-01-15T09:00:00"
  },
  "facilitator_id": 2
}
```

**Response Events**:
- `notification_delivered`: Notification sent to online facilitator
- `notification_stored`: Notification stored for offline facilitator
- `notification_error`: Error occurred during processing

**Business Logic**:
- Validates that the request comes from authenticated backend service
- Checks if target facilitator is online
- If online: sends real-time notification via WebSocket
- If offline: stores notification in database for later delivery
- Confirms delivery or storage back to backend service

### Facilitator Events

#### 1. Facilitator Connection
**Event**: `facilitator_connect`

**Purpose**: Authenticate and establish connection for a facilitator.

**Request Data**:
```json
{
  "facilitator_id": 2,
  "token": "jwt-token-here"
}
```

**Response Events**:
- `facilitator_auth_success`: Authentication successful
- `auth_error`: Authentication failed

**Business Logic**:
- Validates facilitator credentials (JWT token in production)
- Stores facilitator as online in memory and database
- Joins facilitator to their specific room
- Automatically sends any pending notifications

#### 2. Get Pending Notifications
**Event**: `get_pending_notifications`

**Purpose**: Request all undelivered notifications.

**Request Data**:
```json
{
  "facilitator_id": 2
}
```

**Response Event**: `pending_notifications`

**Response Data**:
```json
{
  "notifications": [
    {
      "type": "new_booking",
      "booking_id": 123,
      "user": {
        "id": 5,
        "name": "Jane Smith",
        "email": "jane@example.com"
      },
      "session": {
        "id": 1,
        "title": "Morning Meditation",
        "start_time": "2024-01-15T09:00:00"
      },
      "timestamp": "2024-01-14T15:30:00",
      "message": "New booking from Jane Smith for Morning Meditation",
      "notification_id": 456,
      "stored_at": "2024-01-14T15:30:00"
    }
  ],
  "count": 1
}
```

#### 3. Mark Notification as Read
**Event**: `mark_notification_read`

**Purpose**: Mark a specific notification as read/delivered.

**Request Data**:
```json
{
  "facilitator_id": 2,
  "notification_id": 456
}
```

**Response Event**: `notification_marked_read`

**Business Logic**:
- Validates facilitator ownership of notification
- Updates notification status to delivered
- Removes notification from pending list

### Real-time Notification Events

#### New Booking Notification
**Event**: `new_booking_notification`

**Purpose**: Real-time notification sent to online facilitators.

**Data Format**:
```json
{
  "type": "new_booking",
  "booking_id": 123,
  "user": {
    "id": 5,
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "session": {
    "id": 1,
    "title": "Morning Meditation",
    "start_time": "2024-01-15T09:00:00"
  },
  "timestamp": "2024-01-14T15:30:00",
  "message": "New booking from Jane Smith for Morning Meditation"
}
```

### Connection Management Events

#### Connection Response
**Event**: `connection_response`

**Purpose**: Confirms successful WebSocket connection.

**Data Format**:
```json
{
  "status": "connected",
  "socket_id": "abc123xyz"
}
```

#### Error Events
**Event**: `error` or `auth_error`

**Purpose**: Communicate errors to clients.

**Data Format**:
```json
{
  "error": "Descriptive error message"
}
```

## Data Models

### StoredNotification Model
```python
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
```

**Purpose**: Stores notifications for offline facilitators and tracks delivery status.

### FacilitatorSession Model
```python
class FacilitatorSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facilitator_id = db.Column(db.Integer, nullable=False)
    socket_id = db.Column(db.String(100), nullable=False)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
```

**Purpose**: Tracks facilitator connection sessions and manages reconnection scenarios.

## HTTP Endpoints

### Health Check
**GET** `/health`

**Purpose**: Monitor service health and connection status.

**Response**:
```json
{
  "status": "healthy",
  "service": "notification_service",
  "timestamp": "2024-01-14T12:00:00",
  "online_facilitators": 3,
  "backend_connected": true
}
```

### Service Statistics
**GET** `/stats`

**Purpose**: Get detailed service statistics for monitoring.

**Response**:
```json
{
  "online_facilitators": 3,
  "backend_connected": true,
  "total_notifications": 150,
  "pending_notifications": 5,
  "facilitator_sessions": 8
}
```

## How the Notification System Works

### 1. Service Initialization
```
1. Service starts and creates database tables
2. Starts WebSocket server on port 5002
3. Waits for backend service and facilitator connections
```

### 2. Backend Service Integration
```
1. Backend service connects via WebSocket
2. Authenticates using bearer token
3. Receives confirmation of successful connection
4. Can now send booking notifications
```

### 3. Facilitator Connection Flow
```
1. Facilitator connects via WebSocket from frontend
2. Provides facilitator ID and JWT token
3. Service validates credentials
4. Facilitator joins their specific room
5. Service automatically sends pending notifications
6. Facilitator receives real-time notifications
```

### 4. Notification Delivery Process

#### For Online Facilitators:
```
1. Backend sends booking notification
2. Service checks if facilitator is online
3. Sends real-time notification via WebSocket
4. Facilitator receives immediate notification
5. Service confirms delivery to backend
```

#### For Offline Facilitators:
```
1. Backend sends booking notification
2. Service detects facilitator is offline
3. Stores notification in database
4. Confirms storage to backend
5. When facilitator reconnects:
   - Service sends all pending notifications
   - Facilitator can mark notifications as read
```

### 5. Connection Management

#### Online Facilitators Tracking:
```python
online_facilitators = {
    facilitator_id: socket_id,
    2: "abc123xyz",
    5: "def456uvw"
}
```

#### Reconnection Handling:
```
1. Facilitator disconnects (network issue, browser close)
2. Service removes from online_facilitators
3. Updates database session record
4. Future notifications are stored for offline delivery
5. On reconnection:
   - Facilitator re-authenticates
   - Service updates online status
   - Sends all pending notifications
```

## Security Features

### Authentication
- **Backend Service**: Bearer token authentication
- **Facilitators**: JWT token validation (configurable)
- **Room-based Access**: Facilitators only receive their own notifications

### Authorization
- Only authenticated backend service can send notifications
- Facilitators can only access their own notifications
- Socket ID validation prevents unauthorized access

### Data Protection
- Sensitive data is not logged
- Notification data is properly sanitized
- Database stores minimal required information

## Error Handling

### Common Error Scenarios
1. **Invalid Authentication**: Returns `auth_error` event
2. **Missing Required Fields**: Returns `notification_error` event
3. **Database Errors**: Logged and handled gracefully
4. **Network Issues**: Automatic reconnection support

### Error Response Format
```json
{
  "error": "Descriptive error message explaining what went wrong"
}
```

## Integration with Other Services

### Backend Service Integration
```python
# In backend service
from websocket_client import send_booking_notification

# Send notification
booking_data = {
    "booking_id": 123,
    "user": user_data,
    "session": session_data,
    "facilitator_id": facilitator_id
}
success = send_booking_notification(booking_data)
```

### Frontend Integration
```javascript
// In React frontend
import io from 'socket.io-client';

const socket = io('http://localhost:5002');

// Connect as facilitator
socket.emit('facilitator_connect', {
    facilitator_id: facilitatorId,
    token: jwtToken
});

// Listen for notifications
socket.on('new_booking_notification', (notification) => {
    // Handle real-time notification
    showNotification(notification);
});

// Get pending notifications
socket.emit('get_pending_notifications', {
    facilitator_id: facilitatorId
});
```

## Performance Considerations

### Memory Management
- Online facilitators are stored in memory for fast access
- Offline notifications are persisted to database
- Regular cleanup of delivered notifications

### Scalability
- Service can handle multiple concurrent connections
- Database queries are optimized for facilitator-specific data
- WebSocket rooms provide efficient message routing

### Reliability
- Automatic reconnection support
- Persistent storage for offline scenarios
- Delivery confirmation system

## Monitoring & Debugging

### Logging
```python
logger.info("Facilitator 2 connected: abc123xyz")
logger.info("Real-time notification sent to facilitator 2")
logger.info("Notification stored for offline facilitator 5")
logger.error("Error handling booking notification: Connection failed")
```

### Health Monitoring
- Use `/health` endpoint for uptime monitoring
- Check `online_facilitators` count for activity
- Monitor `backend_connected` status

### Debug Information
- Enable debug mode for detailed Socket.IO logs
- Check `/stats` for service metrics
- Monitor database for pending notifications

## Deployment Configuration

### Docker Configuration
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["python", "app.py"]
```

### Environment Variables for Production
```bash
SECRET_KEY=production-secret-key
DATABASE_URL=postgresql://user:pass@db:5432/notifications
BACKEND_SERVICE_TOKEN=secure-backend-token
```

### Load Balancing Considerations
- WebSocket connections are stateful
- Use sticky sessions for load balancing
- Consider Redis adapter for multiple instances

## Future Enhancements

### Potential Features
1. **Message Types**: Support for different notification types
2. **Push Notifications**: Mobile push notification integration
3. **Message History**: Extended message history for facilitators
4. **Analytics**: Notification delivery and engagement metrics
5. **Message Templates**: Customizable notification templates

### Scaling Considerations
1. **Redis Integration**: For multi-instance deployment
2. **Message Queues**: For high-volume notification processing
3. **Database Optimization**: For large-scale notification storage
4. **CDN Integration**: For global WebSocket distribution

This comprehensive documentation provides a complete understanding of the notification service's architecture, functionality, and integration patterns. The service is designed to be reliable, scalable, and easy to integrate with other microservices in the booking system ecosystem.
