# Booking System for Sessions & Retreats

A full-stack web application for booking wellness sessions and retreats, built with Flask (backend) and React (frontend).

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [🐳 Docker Setup Guide](DOCKER_SETUP.md) | Quick start guide for running the project with Docker |
| [📊 Data Diagram](DATA_DIAGRAM.md) | Database architecture and entity relationships |
| [🔒 Security Documentation](SECURITY_DOCUMENTATION.md) | Comprehensive security practices and implementation |
| [🔔 Notification Service](notification_service/NOTIFICATION_SERVICE_DOCUMENTATION.md) | Real-time notification system guide |
| [🌐 Backend API Documentation](backend/API_DOCUMENTATION.md) | Complete API reference for all endpoints |

## Features

### User Features
- JWT-based authentication with Google OAuth support
- Browse available sessions and retreats
- Book sessions with real-time availability checking
- View booking history (past and upcoming)
- Responsive design for mobile and desktop

### Facilitator Features
- Create and manage sessions/retreats
- View registered users for their sessions
- Cancel sessions when needed
- Dedicated facilitator dashboard

### System Features
- Real-time CRM notification system
- Secure API communication with Bearer tokens
- Database session management
- Comprehensive error handling

## Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-origin resource sharing
- **SQLite** - Database (easily replaceable with PostgreSQL/MySQL)

### Frontend
- **React** - UI library
- **TypeScript** - Type safety
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **React Hot Toast** - Notifications

### CRM Service
- **Flask** - Microservice for handling booking notifications
- **Bearer Token Authentication** - Secure communication
- **SQLite** - Notification storage

## Project Structure

\`\`\`
booking-system/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── websocket_client.py       # WebSocket client for notifications
│   └── requirements.txt          # Python dependencies
├── notification_service/
│   ├── app.py                    # WebSocket notification service
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx        # Navigation component
│   │   │   ├── NotificationSystem.tsx # Real-time notifications
│   │   │   └── ProtectedRoute.tsx # Route protection
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx   # Authentication context
│   │   ├── pages/
│   │   │   ├── Home.tsx          # Landing page
│   │   │   ├── Login.tsx         # Login page
│   │   │   ├── Register.tsx      # Registration page
│   │   │   ├── Dashboard.tsx     # User dashboard
│   │   │   ├── Sessions.tsx      # Sessions listing
│   │   │   ├── Bookings.tsx      # User bookings
│   │   │   └── FacilitatorDashboard.tsx # Facilitator dashboard
│   │   └── App.tsx              # Main App component
│   ├── package.json             # Node dependencies
│   └── tailwind.config.js       # Tailwind configuration
├── test_websocket.py            # WebSocket testing script (optional)
└── README.md                    # Documentation
\`\`\`

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
\`\`\`bash
cd backend
\`\`\`

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install flask flask-sqlalchemy flask-jwt-extended flask-cors werkzeug requests
\`\`\`

4. Run the main application:
\`\`\`bash
python app.py
\`\`\`

The backend will be available at `http://localhost:5000`

### CRM Service Setup

1. Navigate to the CRM service directory:
\`\`\`bash
cd crm_service
\`\`\`

2. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install flask flask-sqlalchemy
\`\`\`

4. Run the CRM service:
\`\`\`bash
python app.py
\`\`\`

The CRM service will be available at `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
\`\`\`bash
cd frontend
\`\`\`

2. Install dependencies:
\`\`\`bash
npm install react react-dom react-router-dom axios
npm install -D @types/react @types/react-dom typescript
npm install tailwindcss lucide-react react-hot-toast
\`\`\`

3. Start the development server:
\`\`\`bash
npm start
\`\`\`

The frontend will be available at `http://localhost:3000`

## API Documentation

### Authentication Endpoints

#### POST /api/auth/register
Register a new user or facilitator.

**Request Body:**
\`\`\`json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "user", // or "facilitator"
  "bio": "Optional bio for facilitators",
  "specialization": "Optional specialization for facilitators"
}
\`\`\`

**Response:**
\`\`\`json
{
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
\`\`\`

#### POST /api/auth/login
Login with email and password.

**Request Body:**
\`\`\`json
{
  "email": "john@example.com",
  "password": "password123"
}
\`\`\`

**Response:**
\`\`\`json
{
  "access_token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
\`\`\`

#### POST /api/auth/google
Login with Google OAuth.

**Request Body:**
\`\`\`json
{
  "google_id": "google_user_id",
  "email": "john@example.com",
  "name": "John Doe"
}
\`\`\`

### Session Endpoints

#### GET /api/sessions
Get all active sessions.

**Headers:**
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

**Response:**
\`\`\`json
[
  {
    "id": 1,
    "title": "Morning Meditation",
    "description": "Start your day with peaceful meditation",
    "facilitator": "Jane Smith",
    "session_type": "session",
    "start_time": "2024-01-15T09:00:00",
    "end_time": "2024-01-15T10:00:00",
    "capacity": 10,
    "price": 25.0,
    "available_spots": 8
  }
]
\`\`\`

#### POST /api/sessions
Create a new session (facilitators only).

**Headers:**
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

**Request Body:**
\`\`\`json
{
  "title": "Morning Meditation",
  "description": "Start your day with peaceful meditation",
  "session_type": "session",
  "start_time": "2024-01-15T09:00:00",
  "end_time": "2024-01-15T10:00:00",
  "capacity": 10,
  "price": 25.0
}
\`\`\`

#### PUT /api/sessions/{id}
Update a session (facilitators only).

#### POST /api/sessions/{id}/cancel
Cancel a session (facilitators only).

### Booking Endpoints

#### POST /api/bookings
Create a new booking.

**Headers:**
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

**Request Body:**
\`\`\`json
{
  "session_id": 1,
  "notes": "Optional notes"
}
\`\`\`

#### GET /api/bookings/my
Get user's bookings.

**Headers:**
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

#### GET /api/facilitator/bookings
Get bookings for facilitator's sessions.

**Headers:**
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

### CRM Service Endpoints

#### POST /api/booking-notification
Receive booking notifications from the main service.

**Headers:**
\`\`\`
Authorization: Bearer <static_bearer_token>
\`\`\`

**Request Body:**
\`\`\`json
{
  "booking_id": 1,
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe"
  },
  "event": {
    "id": 1,
    "title": "Morning Meditation",
    "start_time": "2024-01-15T09:00:00"
  },
  "facilitator_id": 1
}
\`\`\`

#### GET /api/notifications
Get all booking notifications.

#### PUT /api/notifications/{id}/process
Mark a notification as processed.

## 🔄 **Real-Time Notification Architecture**

The system uses WebSockets for real-time communication between services:

### Architecture Flow
1. **User makes booking** → POST request to backend
2. **Backend completes booking** → sends WebSocket message to notification service
3. **Notification service** checks if facilitator is online
4. **If online**: sends real-time notification to facilitator
5. **If offline**: stores notification in database for later delivery

### WebSocket Connections
- **Backend Service** → connects as authenticated client to notification service
- **Facilitators** → connect to receive real-time notifications
- **Notification Service** → acts as WebSocket server managing all connections

### Features
- ✅ Real-time notifications for online facilitators
- ✅ Offline notification storage and delivery
- ✅ Connection status tracking
- ✅ Automatic reconnection handling
- ✅ Audio notifications for new bookings
- ✅ Notification history and management

### Setup Instructions

1. **Start Notification Service** (Port 5001):
\`\`\`bash
cd notification_service
python app.py
\`\`\`

2. **Start Backend Service** (Port 5000):
\`\`\`bash
cd backend
python app.py
\`\`\`

3. **Start Frontend** (Port 3000):
\`\`\`bash
cd frontend
npm start
\`\`\`

### Testing WebSocket Connection
Run the test script to verify WebSocket functionality:
\`\`\`bash
python test_websocket.py
\`\`\`

## Security Features

1. **JWT Authentication** - Secure token-based authentication
2. **Bearer Token** - Static token for CRM service communication
3. **Password Hashing** - Werkzeug security for password storage
4. **CORS Protection** - Configured for specific origins
5. **Input Validation** - Comprehensive validation on all endpoints
6. **Role-Based Access** - Different permissions for users and facilitators

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- password_hash
- name
- role (user/facilitator)
- google_id (for OAuth)
- created_at

### Facilitators Table
- id (Primary Key)
- user_id (Foreign Key)
- bio
- specialization
- created_at

### Sessions Table
- id (Primary Key)
- title
- description
- facilitator_id (Foreign Key)
- session_type (session/retreat)
- start_time
- end_time
- capacity
- price
- status (active/cancelled)
- created_at

### Bookings Table
- id (Primary Key)
- user_id (Foreign Key)
- session_id (Foreign Key)
- booking_status (confirmed/cancelled)
- booking_date
- notes

## Future Enhancements

### Payment Integration Roadmap

1. **Payment Gateway Integration**
   - Stripe/PayPal integration for secure payments
   - Payment processing on booking confirmation
   - Multiple payment methods support

2. **Refund System**
   - Automatic refunds for cancelled sessions
   - Partial refunds based on cancellation policy
   - Refund tracking and notifications

3. **Implementation Plan**
   - Phase 1: Basic payment processing
   - Phase 2: Refund automation
   - Phase 3: Advanced payment features (subscriptions, installments)

### Additional Features
- Email notifications for bookings and reminders
- Calendar integration (Google Calendar, Outlook)
- Rating and review system
- Advanced search and filtering
- Mobile app development
- Multi-language support

## Testing

### Manual Testing Checklist

1. **Authentication**
   - [ ] User registration
   - [ ] User login
   - [ ] Google OAuth (if implemented)
   - [ ] JWT token validation

2. **Sessions**
   - [ ] Browse sessions
   - [ ] Create session (facilitator)
   - [ ] Update session (facilitator)
   - [ ] Cancel session (facilitator)

3. **Bookings**
   - [ ] Book a session
   - [ ] View bookings
   - [ ] Capacity checking
   - [ ] Double booking prevention

4. **CRM Integration**
   - [ ] Booking notification sent
   - [ ] Bearer token validation
   - [ ] Notification storage

## Deployment

### Production Considerations

1. **Environment Variables**
   - JWT_SECRET_KEY
   - DATABASE_URL
   - CRM_SERVICE_URL
   - CRM_BEARER_TOKEN

2. **Database**
   - Migrate from SQLite to PostgreSQL/MySQL
   - Set up database migrations
   - Configure connection pooling

3. **Security**
   - HTTPS enforcement
   - Rate limiting
   - Input sanitization
   - Security headers

4. **Performance**
   - Database indexing
   - Caching (Redis)
   - CDN for static assets
   - Load balancing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
