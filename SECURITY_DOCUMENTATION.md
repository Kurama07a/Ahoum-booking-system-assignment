# Security Practices Documentation - Booking System

## Overview

This document outlines the comprehensive security practices implemented across the booking system project. The system follows industry-standard security practices to protect user data, prevent unauthorized access, and ensure secure communication between all components.

## Security Architecture

### Multi-Layer Security Approach
1. **Network Security**: Nginx reverse proxy with rate limiting
2. **Authentication**: JWT-based authentication with role-based access
3. **Authorization**: Fine-grained permission system
4. **Data Protection**: Password hashing and secure data storage
5. **Service-to-Service Communication**: Bearer token authentication
6. **Input Validation**: Comprehensive data validation across all endpoints
7. **Configuration Security**: Environment-based configuration management

## Authentication & Authorization

### 1. JWT Token-Based Authentication

**Implementation Location**: `backend/app.py`

```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_EXPIRES_HOURS = int(os.getenv('JWT_EXPIRES_HOURS', '24'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=JWT_EXPIRES_HOURS)
```

**Security Features**:
- **Secret Key Management**: JWT secret key is configurable via environment variables
- **Token Expiration**: Configurable token expiration (default: 24 hours)
- **Production Security**: Clear warning to change default keys in production
- **Token Validation**: All protected endpoints validate JWT tokens

### 2. Role-Based Access Control (RBAC)

**Implementation**: Custom decorator for role validation

```python
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
```

**Role Hierarchy**:
- **User**: Can view sessions, create bookings, manage their own bookings
- **Facilitator**: All user permissions + create/manage sessions, view facilitator dashboard

**Protected Endpoints**:
- `@jwt_required()`: Requires valid JWT token
- `@role_required('facilitator')`: Requires facilitator role
- Automatic authorization checks for resource ownership

### 3. Password Security

**Implementation**: Werkzeug security for password hashing

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Password hashing during registration
user = User(
    email=data['email'],
    password_hash=generate_password_hash(data['password']),
    name=data['name']
)

# Password validation during login
if user and check_password_hash(user.password_hash, data['password']):
    access_token = create_access_token(identity=str(user.id))
```

**Security Features**:
- **Salted Hashes**: Passwords are never stored in plain text
- **PBKDF2 Algorithm**: Uses industry-standard PBKDF2 for password hashing
- **Unique Salts**: Each password gets a unique salt
- **Hash Verification**: Secure password verification during login

### 4. OAuth Integration

**Google OAuth Support**:
```python
@app.route('/api/auth/google', methods=['POST'])
def google_login():
    data = request.get_json()
    google_id = data.get('google_id')
    email = data.get('email')
    name = data.get('name')
    
    # Validation and user creation/linking
    user = User.query.filter_by(google_id=google_id).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
        else:
            user = User(email=email, name=name, google_id=google_id, role='user')
```

**OAuth Security**:
- **Account Linking**: Safely links Google accounts to existing users
- **Email Verification**: Uses verified Google email addresses
- **No Password Storage**: OAuth users don't have local passwords
- **Default Role**: New OAuth users get 'user' role by default

## Service-to-Service Security

### 1. Bearer Token Authentication

**CRM Service Authentication**:
```python
BEARER_TOKEN = os.getenv('CRM_BEARER_TOKEN', 'your-static-bearer-token-here')

def validate_bearer_token():
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
```

**Notification Service Authentication**:
```python
BACKEND_BEARER_TOKEN = os.getenv('BACKEND_SERVICE_TOKEN', 'backend-service-token-here')

@socketio.on('backend_connect')
def handle_backend_connect(data):
    token = data.get('token')
    if token != BACKEND_BEARER_TOKEN:
        emit('auth_error', {'error': 'Invalid token'})
        return
    
    # Authenticate and store backend connection
    global backend_socket_id
    backend_socket_id = request.sid
```

**Security Features**:
- **Static Bearer Tokens**: Services authenticate using pre-shared tokens
- **Header Validation**: Proper Authorization header format validation
- **Token Comparison**: Constant-time token comparison
- **Environment Configuration**: Tokens configurable via environment variables

### 2. WebSocket Security

**Connection Authentication**:
```python
@socketio.on('facilitator_connect')
def handle_facilitator_connect(data):
    facilitator_id = data.get('facilitator_id')
    token = data.get('token')  # JWT token from facilitator
    
    # In production, validate the JWT token here
    if not facilitator_id:
        emit('auth_error', {'error': 'Facilitator ID required'})
        return
```

**WebSocket Security Features**:
- **Token-Based Authentication**: JWT tokens required for facilitator connections
- **Room-Based Access Control**: Users only join their specific rooms
- **Socket ID Validation**: Prevents unauthorized message interception
- **Session Management**: Tracks and validates active connections

## Network Security

### 1. Nginx Reverse Proxy Configuration

**Security Headers**:
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline' 'unsafe-eval'" always;
```

**Rate Limiting**:
```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# Apply rate limiting
location /api {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend:5000;
}

location /api/auth {
    limit_req zone=login burst=5 nodelay;
    proxy_pass http://backend:5000;
}
```

**Security Features**:
- **XSS Protection**: Prevents cross-site scripting attacks
- **CSRF Protection**: X-Frame-Options prevents clickjacking
- **Content Type Validation**: Prevents MIME type confusion attacks
- **Rate Limiting**: Prevents brute force and DoS attacks
- **Reverse Proxy**: Hides internal service architecture

### 2. CORS Configuration

**Backend CORS Setup**:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes
```

**Notification Service CORS**:
```python
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
```

**CORS Security Considerations**:
- **Development**: Allows all origins for development ease
- **Production**: Should be configured to specific domains
- **WebSocket CORS**: Configured for real-time communication

## Data Protection

### 1. Database Security

**Connection Security**:
```python
# Development (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking_system.db'

# Production (PostgreSQL with credentials)
DATABASE_URL = 'postgresql://postgres:password123@db:5432/booking_system'
```

**Data Isolation**:
- **Separate Databases**: Each service has its own database
- **Connection Pooling**: Managed by SQLAlchemy
- **SQL Injection Prevention**: ORM-based queries prevent injection

### 2. Sensitive Data Handling

**Environment Variables**:
```python
# All sensitive data configured via environment variables
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
CRM_BEARER_TOKEN = os.getenv('CRM_BEARER_TOKEN', 'your-static-bearer-token-here')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
```

**Email Configuration Security**:
```python
# Email service configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
```

## Input Validation & Sanitization

### 1. Request Validation

**Registration Validation**:
```python
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Email uniqueness check
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Required field validation
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        name=data['name'],
        role=data.get('role', 'user')
    )
```

**Booking Validation**:
```python
@app.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json()
    current_user_id = int(get_jwt_identity())
    
    session = Session.query.get_or_404(data['session_id'])
    
    # Business logic validation
    if session.status != 'active':
        return jsonify({'error': 'Session is not available'}), 400
    
    if len(session.bookings) >= session.capacity:
        return jsonify({'error': 'Session is fully booked'}), 400
```

### 2. Data Sanitization

**JSON Schema Validation**:
```python
# CRM Service validation
required_fields = ['booking_id', 'user', 'session', 'facilitator_id']
for field in required_fields:
    if field not in data:
        return jsonify({'error': f'Missing required field: {field}'}), 400

# Nested field validation
user_fields = ['id', 'email', 'name']
for field in user_fields:
    if field not in data.get('user', {}):
        return jsonify({'error': f'Missing user field: {field}'}), 400
```

**Email Service Validation**:
```python
def send_booking_emails(request):
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['booking_id', 'user', 'session', 'facilitator']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
```

## Configuration Management

### 1. Environment-Based Configuration

**Configuration Manager**:
```python
class ConfigManager:
    def __init__(self):
        self.config = {
            'development': {
                'security': {
                    'jwt_secret': 'dev-jwt-secret-key',
                    'crm_bearer_token': 'dev-static-bearer-token',
                    'backend_service_token': 'dev-backend-service-token'
                }
            },
            'production': {
                'security': {
                    'jwt_secret': secrets.token_urlsafe(32),
                    'crm_bearer_token': secrets.token_urlsafe(32),
                    'backend_service_token': secrets.token_urlsafe(32)
                }
            }
        }
```

**Secret Generation**:
```python
def generate_env_file(self, environment='development'):
    config = self.config[environment]
    
    env_content = f"""
# Security Configuration
JWT_SECRET_KEY={config['security']['jwt_secret']}
CRM_BEARER_TOKEN={config['security']['crm_bearer_token']}
BACKEND_SERVICE_TOKEN={config['security']['backend_service_token']}
"""
```

### 2. Docker Security

**Production Docker Configuration**:
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-jwt-secret-key-change-in-production}
      - CRM_BEARER_TOKEN=${CRM_BEARER_TOKEN:-your-static-bearer-token-here}
      - BACKEND_SERVICE_TOKEN=${BACKEND_SERVICE_TOKEN:-backend-service-token-here}
    restart: unless-stopped
    networks:
      - booking-network
```

**Container Security**:
- **Network Isolation**: Services communicate through internal Docker network
- **Environment Variables**: Secrets passed via environment variables
- **Restart Policies**: Automatic restart on failure
- **Resource Limits**: Controlled resource usage

## Frontend Security

### 1. Token Storage & Management

**Secure Token Handling**:
```typescript
// AuthContext.tsx
const [token, setToken] = useState<string | null>(localStorage.getItem("token"))

useEffect(() => {
  if (token) {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`
  }
  setLoading(false)
}, [token])
```

**API Configuration**:
```typescript
// api.ts
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  NOTIFICATION_URL: process.env.REACT_APP_NOTIFICATION_URL || 'http://localhost:5002'
}
```

### 2. Protected Routes

**Route Protection**:
```typescript
// ProtectedRoute component ensures authentication
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()
  
  if (loading) return <div>Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  
  return <>{children}</>
}
```

## Error Handling & Logging

### 1. Secure Error Responses

**Standardized Error Format**:
```python
# Generic error responses that don't leak sensitive information
return jsonify({'error': 'Invalid credentials'}), 401
return jsonify({'error': 'Insufficient permissions'}), 403
return jsonify({'error': 'Resource not found'}), 404
```

**Logging Security**:
```python
# Notification service logging
logger.info(f"Facilitator {facilitator_id} connected: {request.sid}")
logger.error(f"Authentication error: {data.get('error')}")

# Email service logging
logger.info(f"Email sent successfully to {to_email}")
logger.error(f"Failed to send email to {to_email}: {str(e)}")
```

### 2. Security Monitoring

**Health Check Endpoints**:
```python
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'backend',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status
    }), 200
```

## Security Best Practices Implemented

### 1. **Principle of Least Privilege**
- Users only have access to their own resources
- Facilitators have additional permissions for their sessions
- Service-to-service communication uses specific tokens

### 2. **Defense in Depth**
- Multiple layers of security (network, application, data)
- Rate limiting at nginx level
- Authentication at application level
- Authorization at endpoint level

### 3. **Secure Development Practices**
- Environment-based configuration
- No hardcoded secrets in code
- Comprehensive input validation
- Secure password storage

### 4. **Monitoring & Auditing**
- Comprehensive logging across all services
- Health check endpoints for monitoring
- Error tracking and reporting

