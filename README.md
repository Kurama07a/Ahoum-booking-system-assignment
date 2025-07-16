# Booking System for Sessions & Retreats

A full-stack web application for booking wellness sessions and retreats, built with Flask (backend) and React (frontend).

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


## License

This project is licensed under the MIT License.
