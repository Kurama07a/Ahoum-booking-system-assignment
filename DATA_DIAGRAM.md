# Data Diagram - Booking System 📊

## Database Architecture Overview

The booking system uses a **microservices architecture** with **3 separate database schemas**, each handling different aspects of the system.

### Production Setup:
```
           🐘 Single PostgreSQL Container
    ┌──────────────────────────────────────────────────┐
    │  📊 booking_system    � crm    📊 notifications|
    │   (Main System)    (Analytics)  (Real-time)      │
    └──────────────────────────────────────────────────┘
```

### Development Setup:
```
    🗄️ SQLite Files (Local Storage)
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│ booking_system  │ │   crm.db    │ │ notifications   │
│     .db         │ │             │ │     .db         │
└─────────────────┘ └─────────────┘ └─────────────────┘
```

**Key Point**: It's **3 database schemas** in production (1 PostgreSQL container) or **3 SQLite files** in development, not 3 separate database servers!

---

## 🏢 Backend Database Schema (booking_system)

### Core Entity Relationships

```
                    ┌─────────────────┐
                    │      User       │
                    │ ─────────────── │
                    │ • id (PK)       │
                    │ • email         │
                    │ • password_hash │
                    │ • name          │
                    │ • role          │
                    │ • google_id     │
                    │ • created_at    │
                    └─────────────────┘
                             │
                             │ 1:1 (if role='facilitator')
                             ▼
                    ┌─────────────────┐
                    │   Facilitator   │
                    │ ─────────────── │
                    │ • id (PK)       │
                    │ • user_id (FK)  │
                    │ • bio           │
                    │ • specialization│
                    │ • created_at    │
                    └─────────────────┘
                             │
                             │ 1:Many
                             ▼
                    ┌─────────────────┐
                    │    Session      │
                    │ ─────────────── │
                    │ • id (PK)       │
                    │ • title         │
                    │ • description   │
                    │ • facilitator_id│
                    │ • session_type  │
                    │ • start_time    │
                    │ • end_time      │
                    │ • capacity      │
                    │ • price         │
                    │ • status        │
                    │ • created_at    │
                    └─────────────────┘
                             │
                             │ 1:Many
                             ▼
     ┌─────────────────┐    ┌─────────────────┐
     │      User       │    │    Booking      │
     │ (from above)    │◄───│ ─────────────── │
     │                 │    │ • id (PK)       │
     └─────────────────┘    │ • user_id (FK)  │
                            │ • session_id(FK)│
                            │ • booking_status│
                            │ • booking_date  │
                            │ • notes         │
                            └─────────────────┘
```

### Key Relationships Explained:

1. **User → Facilitator** (1:1, Optional)
   - Only users with `role='facilitator'` get a facilitator profile
   - Contains facilitator-specific info (bio, specialization)

2. **Facilitator → Sessions** (1:Many)
   - Each facilitator can create multiple sessions
   - Sessions can be 'session' or 'retreat' types

3. **User → Bookings** (1:Many)
   - Regular users can book multiple sessions
   - Booking status: 'confirmed' or 'cancelled'

4. **Session → Bookings** (1:Many)
   - Each session can have multiple bookings
   - Limited by session capacity

---

## 🔔 Notification Database Schema (notifications)

```
                    ┌─────────────────┐
                    │StoredNotification│
                    │ ─────────────── │
                    │ • id (PK)       │
                    │ • facilitator_id│
                    │ • booking_id    │
                    │ • user_name     │
                    │ • user_email    │
                    │ • session_title │
                    │ • session_start │
                    │ • message_data  │
                    │ • created_at    │
                    │ • delivered     │
                    └─────────────────┘
                             │
                             │ Related via facilitator_id
                             ▼
                    ┌─────────────────┐
                    │FacilitatorSession│
                    │ ─────────────── │
                    │ • id (PK)       │
                    │ • facilitator_id│
                    │ • socket_id     │
                    │ • connected_at  │
                    │ • last_seen     │
                    └─────────────────┘
```

### Purpose:
- **StoredNotification**: Saves notifications for offline facilitators
- **FacilitatorSession**: Tracks who's online for real-time delivery

---

## 📋 CRM Database Schema (crm)

```
                    ┌─────────────────┐
                    │BookingNotification│
                    │ ─────────────── │
                    │ • id (PK)       │
                    │ • booking_id    │
                    │ • user_id       │
                    │ • user_email    │
                    │ • user_name     │
                    │ • event_id      │
                    │ • event_title   │
                    │ • event_start   │
                    │ • facilitator_id│
                    │ • received_at   │
                    │ • processed     │
                    └─────────────────┘
```

### Purpose:
- **BookingNotification**: Stores all booking events for CRM analysis
- Used for tracking customer interactions and business metrics

---

## 🔄 Cross-Schema Relationships

```
booking_system Schema          notifications Schema         crm Schema
┌─────────────┐               ┌─────────────┐            ┌─────────────┐
│   Booking   │ booking_id    │StoredNotif. │ booking_id │BookingNotif.│
│     │       │◄─────────────►│             │◄──────────►│             │
│ facilitator │               │facilitator_ │            │facilitator_ │
│     _id     │◄─────────────►│     id      │◄──────────►│     id      │
└─────────────┘               └─────────────┘            └─────────────┘
```

### How They Connect:
- **booking_id**: Links booking records across all schemas
- **facilitator_id**: Connects facilitator actions across systems
- **user_id**: Tracks user behavior across services

**Important**: These are logical connections, not foreign keys, since they're in different database schemas!

---

## 📝 Sample Data Flow

### When a User Books a Session:

1. **booking_system schema** creates:
   ```sql
   INSERT INTO booking (user_id, session_id, booking_status, booking_date)
   VALUES (123, 456, 'confirmed', NOW());
   ```

2. **Notification Service** handles:
   - If facilitator online → Real-time WebSocket
   - If facilitator offline → Store in `notifications.stored_notification`

3. **CRM schema** records:
   ```sql
   INSERT INTO booking_notification (booking_id, user_id, facilitator_id, ...)
   VALUES (789, 123, 456, ...);
   ```

---

## 🎯 Data Types & Constraints

### Common Field Types:
- **IDs**: `Integer` (Primary Keys, Foreign Keys)
- **Names/Titles**: `String(100-200)`
- **Emails**: `String(120)`
- **Timestamps**: `DateTime`
- **Status Fields**: `String(20)` with specific values
- **Large Text**: `Text` (descriptions, notes, JSON)

### Key Constraints:
- **Unique Fields**: email, google_id
- **Required Fields**: email, name, title, start_time, end_time
- **Default Values**: role='user', status='active', booking_status='confirmed'
- **Foreign Keys**: Maintain referential integrity

---

## 🔐 Security & Privacy

### Data Protection:
- **Passwords**: Hashed using Werkzeug (never stored plain text)
- **Personal Data**: Names and emails are duplicated in notification/CRM DBs for performance
- **Session Data**: Sensitive session details only in main backend DB

### Access Patterns:
- **Users**: Can only see their own bookings
- **Facilitators**: Can see bookings for their sessions
- **Services**: Each service has its own database scope

---

