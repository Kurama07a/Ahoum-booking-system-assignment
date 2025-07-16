# Booking System Backend API Documentation

## Overview

This is the complete API documentation for the Booking System backend service. The system allows users to book sessions and retreats with facilitators, while providing comprehensive management capabilities for both users and facilitators. The service is built with Flask and provides RESTful endpoints for authentication, session management, booking operations, and dashboard functionality.

## Base Information

- **Base URL**: `http://localhost:5000/api` (development)
- **Technology Stack**: Flask, SQLAlchemy, JWT, WebSockets, CORS
- **Database**: SQLite (configurable to PostgreSQL)
- **Authentication**: JWT (JSON Web Tokens) with Bearer token authentication

## Authentication System

The API uses JWT tokens for authentication. All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### JWT Token Configuration
- **Default Expiration**: 24 hours (configurable via `JWT_EXPIRES_HOURS` environment variable)
- **Secret Key**: Configurable via `JWT_SECRET_KEY` environment variable
- **Token Format**: Standard JWT with user ID as identity

## User Roles

The system supports two user roles:
- **user**: Regular users who can book sessions and manage their bookings
- **facilitator**: Users who can create sessions, manage bookings, and access facilitator dashboard

## API Endpoints

### Authentication Endpoints

#### User Registration
**POST** `/api/auth/register`

Register a new user account in the system.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "role": "user",
  "bio": "Optional bio for facilitators",
  "specialization": "Optional specialization for facilitators"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

**Business Logic:**
- Validates email uniqueness
- Hashes password before storage
- Automatically creates facilitator profile if role is "facilitator"
- Returns JWT token for immediate login

**Error Responses:**
- `400 Bad Request`: Email already registered

#### User Login
**POST** `/api/auth/login`

Authenticate user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

**Business Logic:**
- Validates credentials against hashed password
- Generates new JWT token on successful authentication

**Error Responses:**
- `401 Unauthorized`: Invalid credentials

#### Google OAuth Login
**POST** `/api/auth/google`

Authenticate user using Google OAuth credentials.

**Request Body:**
```json
{
  "google_id": "google-oauth-id",
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

**Business Logic:**
- Creates new user if Google ID doesn't exist
- Links Google ID to existing user if email matches
- Default role is "user" for new Google accounts

**Error Responses:**
- `400 Bad Request`: Missing required fields

### Session Management Endpoints

#### Get All Sessions
**GET** `/api/sessions`

Retrieve all active sessions available for booking.

**Authentication:** Required (any authenticated user)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Morning Meditation",
    "description": "Start your day with peaceful meditation",
    "facilitator": "John Doe",
    "session_type": "session",
    "start_time": "2024-01-15T09:00:00",
    "end_time": "2024-01-15T10:00:00",
    "capacity": 10,
    "price": 25.0,
    "available_spots": 8
  }
]
```

**Business Logic:**
- Only returns sessions with status "active"
- Calculates available spots by subtracting confirmed bookings from capacity
- Shows facilitator name for easy identification

#### Create New Session
**POST** `/api/sessions`

Create a new session or retreat (facilitators only).

**Authentication:** Required (facilitator role)

**Request Body:**
```json
{
  "title": "Evening Yoga",
  "description": "Relaxing yoga session",
  "session_type": "session",
  "start_time": "2024-01-15T18:00:00",
  "end_time": "2024-01-15T19:00:00",
  "capacity": 15,
  "price": 30.0
}
```

**Response (201 Created):**
```json
{
  "message": "Session created successfully",
  "session_id": 2
}
```

**Business Logic:**
- Automatically assigns the authenticated facilitator as session owner
- Validates facilitator profile exists
- Supports both "session" and "retreat" types
- Default capacity is 1 if not specified

**Error Responses:**
- `403 Forbidden`: Insufficient permissions (not a facilitator)
- `404 Not Found`: Facilitator profile not found

#### Update Session
**PUT** `/api/sessions/<session_id>`

Update an existing session (facilitators only, own sessions).

**Authentication:** Required (facilitator role, session owner)

**Request Body:**
```json
{
  "title": "Updated Session Title",
  "description": "Updated description",
  "capacity": 20,
  "start_time": "2024-01-15T19:00:00",
  "end_time": "2024-01-15T20:00:00"
}
```

**Response (200 OK):**
```json
{
  "message": "Session updated successfully"
}
```

**Business Logic:**
- Only session owner can update their sessions
- Supports partial updates (only provided fields are updated)
- Validates ownership before allowing updates

**Error Responses:**
- `403 Forbidden`: Unauthorized (not session owner)
- `404 Not Found`: Session not found

#### Cancel Session
**POST** `/api/sessions/<session_id>/cancel`

Cancel a session and all its bookings (facilitators only, own sessions).

**Authentication:** Required (facilitator role, session owner)

**Response (200 OK):**
```json
{
  "message": "Session cancelled successfully"
}
```

**Business Logic:**
- Sets session status to "cancelled"
- Automatically cancels all bookings for the session
- Maintains data integrity by not deleting records

**Error Responses:**
- `403 Forbidden`: Unauthorized (not session owner)
- `404 Not Found`: Session not found

#### Delete Session
**DELETE** `/api/facilitator/sessions/<session_id>`

Delete/cancel a session (facilitators only, own sessions).

**Authentication:** Required (facilitator role, session owner)

**Response (200 OK):**
```json
{
  "message": "Session cancelled successfully"
}
```

**Business Logic:**
- Actually marks session as cancelled rather than deleting
- Cancels all associated bookings
- Maintains referential integrity

**Error Responses:**
- `403 Forbidden`: Unauthorized (not session owner)
- `404 Not Found`: Session not found

### Booking Management Endpoints

#### Create Booking
**POST** `/api/bookings`

Create a new booking for a session.

**Authentication:** Required (any authenticated user)

**Request Body:**
```json
{
  "session_id": 1,
  "notes": "Optional booking notes"
}
```

**Response (201 Created):**
```json
{
  "message": "Booking created successfully",
  "booking_id": 123
}
```

**Business Logic:**
- Validates session availability and capacity
- Prevents double booking by the same user
- Automatically sends WebSocket notification to facilitator
- Triggers email notifications to both user and facilitator
- Integrates with external CRM and email services

**Error Responses:**
- `400 Bad Request`: Session not available, fully booked, or already booked by user
- `404 Not Found`: Session not found

#### Get My Bookings
**GET** `/api/bookings/my`

Retrieve all bookings for the authenticated user.

**Authentication:** Required (any authenticated user)

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "session": {
      "id": 1,
      "title": "Morning Meditation",
      "start_time": "2024-01-15T09:00:00",
      "end_time": "2024-01-15T10:00:00",
      "facilitator": "John Doe"
    },
    "booking_status": "confirmed",
    "booking_date": "2024-01-14T15:30:00",
    "notes": "Looking forward to this session"
  }
]
```

**Business Logic:**
- Returns all bookings for the authenticated user
- Includes session details and facilitator information
- Shows booking status and date

#### Get Facilitator Bookings
**GET** `/api/facilitator/bookings`

Retrieve all bookings for the facilitator's sessions.

**Authentication:** Required (facilitator role)

**Response (200 OK):**
```json
[
  {
    "id": 123,
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
    "booking_status": "confirmed",
    "booking_date": "2024-01-14T15:30:00",
    "notes": "User notes"
  }
]
```

**Business Logic:**
- Shows all bookings for sessions created by the facilitator
- Includes user contact information for communication
- Useful for managing attendees and capacity

**Error Responses:**
- `404 Not Found`: Facilitator profile not found

### Facilitator Dashboard Endpoints

#### Get Facilitator Dashboard
**GET** `/api/facilitator/dashboard`

Retrieve comprehensive dashboard data for facilitators.

**Authentication:** Required (facilitator role)

**Response (200 OK):**
```json
{
  "metrics": {
    "total_sessions": 15,
    "active_sessions": 12,
    "total_bookings": 48,
    "total_revenue": 1200.0,
    "upcoming_sessions": 8
  },
  "recent_bookings": [
    {
      "id": 123,
      "user": {
        "name": "Jane Smith",
        "email": "jane@example.com"
      },
      "session": {
        "title": "Morning Meditation",
        "start_time": "2024-01-15T09:00:00"
      },
      "booking_date": "2024-01-14T15:30:00",
      "status": "confirmed"
    }
  ]
}
```

**Business Logic:**
- Calculates key performance metrics
- Shows recent bookings (last 10)
- Provides revenue calculations
- Counts upcoming sessions for planning

**Error Responses:**
- `404 Not Found`: Facilitator profile not found

#### Get Facilitator Sessions
**GET** `/api/facilitator/sessions`

Retrieve all sessions created by the facilitator.

**Authentication:** Required (facilitator role)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Morning Meditation",
    "description": "Start your day with peaceful meditation",
    "session_type": "session",
    "start_time": "2024-01-15T09:00:00",
    "end_time": "2024-01-15T10:00:00",
    "capacity": 10,
    "price": 25.0,
    "status": "active",
    "bookings_count": 2,
    "available_spots": 8,
    "created_at": "2024-01-10T12:00:00"
  }
]
```

**Business Logic:**
- Returns all sessions regardless of status
- Includes booking statistics
- Calculates available spots based on confirmed bookings
- Shows creation date for tracking

**Error Responses:**
- `404 Not Found`: Facilitator profile not found

#### Get Session Bookings
**GET** `/api/facilitator/sessions/<session_id>/bookings`

Retrieve all bookings for a specific session.

**Authentication:** Required (facilitator role, session owner)

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "user": {
      "id": 5,
      "name": "Jane Smith",
      "email": "jane@example.com"
    },
    "booking_status": "confirmed",
    "booking_date": "2024-01-14T15:30:00",
    "notes": "Looking forward to this session"
  }
]
```

**Business Logic:**
- Only shows bookings for sessions owned by the facilitator
- Includes user contact information
- Shows all booking statuses (confirmed, cancelled)

**Error Responses:**
- `403 Forbidden`: Unauthorized (not session owner)
- `404 Not Found`: Session not found

### System Health Endpoint

#### Health Check
**GET** `/health`

Check the health status of the backend service.

**Authentication:** Not required

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "backend",
  "timestamp": "2024-01-14T12:00:00",
  "database": "connected"
}
```

**Business Logic:**
- Tests database connectivity
- Provides service status information
- Useful for monitoring and load balancers

## Data Models

### User Model
```
- id: Integer (Primary Key)
- email: String (Unique, Required)
- password_hash: String (Hashed password)
- name: String (Required)
- role: String (Default: 'user', Options: 'user', 'facilitator')
- google_id: String (Unique, for OAuth)
- created_at: DateTime (Default: current time)
```

### Facilitator Model
```
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User)
- bio: Text (Optional)
- specialization: String (Optional)
- created_at: DateTime (Default: current time)
```

### Session Model
```
- id: Integer (Primary Key)
- title: String (Required)
- description: Text (Optional)
- facilitator_id: Integer (Foreign Key to Facilitator)
- session_type: String (Required, Options: 'session', 'retreat')
- start_time: DateTime (Required)
- end_time: DateTime (Required)
- capacity: Integer (Default: 1)
- price: Float (Default: 0.0)
- status: String (Default: 'active', Options: 'active', 'cancelled')
- created_at: DateTime (Default: current time)
```

### Booking Model
```
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User)
- session_id: Integer (Foreign Key to Session)
- booking_status: String (Default: 'confirmed', Options: 'confirmed', 'cancelled')
- booking_date: DateTime (Default: current time)
- notes: Text (Optional)
```

## Integration Features

### WebSocket Notifications
The system integrates with a notification service via WebSocket connections to provide real-time notifications to facilitators when new bookings are created.

**Configuration:**
- `NOTIFICATION_SERVICE_URL`: URL of the notification service
- `BACKEND_SERVICE_TOKEN`: Authentication token for backend service

### Email Service Integration
Automatically sends email notifications for booking confirmations to both users and facilitators.

**Configuration:**
- `EMAIL_SERVICE_URL`: URL of the email service

### CRM Integration
The system can integrate with external CRM systems for advanced customer relationship management.

**Configuration:**
- `CRM_SERVICE_URL`: URL of the CRM service
- `CRM_BEARER_TOKEN`: Bearer token for CRM authentication

## Environment Configuration

### Required Environment Variables
```
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRES_HOURS=24
DATABASE_URL=sqlite:///booking_system.db
CRM_SERVICE_URL=http://localhost:5001
CRM_BEARER_TOKEN=your-static-bearer-token-here
EMAIL_SERVICE_URL=http://localhost:5003
NOTIFICATION_SERVICE_URL=http://localhost:5002
BACKEND_SERVICE_TOKEN=backend-service-token-here
```

### Optional Configuration
- Database can be configured to use PostgreSQL by changing the `DATABASE_URL`
- JWT token expiration can be customized via `JWT_EXPIRES_HOURS`
- All service URLs are configurable for different environments

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses:

### Common Error Responses
- `400 Bad Request`: Invalid request data or business logic violation
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions for the operation
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server-side error

### Error Response Format
```json
{
  "error": "Descriptive error message"
}
```

## Security Features

### Authentication & Authorization
- JWT-based authentication with configurable expiration
- Role-based access control (user vs facilitator)
- Password hashing using Werkzeug security
- Google OAuth integration support

### Data Protection
- Password hashing before storage
- JWT token validation on protected endpoints
- Role-based endpoint access control
- Bearer token authentication for service-to-service communication

## Sample Data

The system automatically creates sample data on first run:

### Sample Facilitator
- **Email**: facilitator@example.com
- **Password**: password123
- **Name**: John Doe
- **Specialization**: Mindfulness & Wellness

### Sample Sessions
1. **Morning Meditation**
   - Type: session
   - Duration: 1 hour
   - Capacity: 10 people
   - Price: $25.00

2. **Weekend Retreat**
   - Type: retreat
   - Duration: 2 days
   - Capacity: 5 people
   - Price: $200.00

This comprehensive API documentation provides everything needed to understand and integrate with the booking system backend service. The system is designed to be scalable, secure, and easy to integrate with other services in a microservices architecture.
