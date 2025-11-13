# PrivateRoute Backend API

A FastAPI-based backend for managing inter-departmental communication with role-based access control, temporary and permanent communication rules, and comprehensive audit logging.

## Features

- **Role-Based Access Control**: Admin, Manager, User, and Auditor roles
- **Permanent Communication Rules**: Admin-only cross-department communication rules
- **Temporary Access Requests**: User-initiated, manager-approved temporary access
- **Message Sending with Permission Checks**: Automatic validation before message delivery
- **Comprehensive Audit Logging**: All actions are logged for compliance
- **JWT Authentication**: Secure token-based authentication

## Project Structure

```
PrivateRoute/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication and authorization
│   ├── permissions.py       # Communication permission checking
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── users.py         # User management
│       ├── departments.py   # Department management
│       ├── roles.py         # Role management
│       ├── communication_rules.py  # Communication rules
│       ├── messages.py      # Message sending and retrieval
│       └── audit.py         # Audit and logging
├── requirements.txt
├── init_db.py               # Database initialization script
└── README.md
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL database:**
   
   **Install PostgreSQL:**
   - Download from: https://www.postgresql.org/download/
   - Install and remember the `postgres` user password
   
   **Create the database:**
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- Create database
   CREATE DATABASE privateroute;
   
   -- Create user (optional but recommended)
   CREATE USER privateroute_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE privateroute TO privateroute_user;
   \q
   ```

3. **Set up environment variables:**
Create a `.env` file in the root directory (you can copy from `.env.example`):

**Required variables:**
```
# Database
DATABASE_URL=postgresql://privateroute_user:your_secure_password@localhost:5432/privateroute

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Optional - Email Configuration:**
If you want to send emails when messages are sent, add these:
```
ENABLE_EMAIL=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@privateroute.com
MAIL_FROM_NAME=PrivateRoute System
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

**Notes:** 
- **Database**: Replace `your_secure_password` with your actual PostgreSQL password
- **Email**: 
  - Email configuration is **optional** - if `ENABLE_EMAIL=False` or not set, messages will only be logged to the database
  - To enable email sending, set `ENABLE_EMAIL=True` and configure your SMTP settings
  - For Gmail, you'll need to use an App Password (not your regular password)
  - See `.env.example` for detailed email provider examples

4. **Initialize the database:**
```bash
python init_db.py
```

This will create all tables and default roles in your PostgreSQL database.

5. **Run the server:**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation (Swagger UI) at `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Users
- `POST /api/users` - Create user (Admin only)
- `GET /api/users` - List users (Admin/Auditor only)
- `GET /api/users/search` - Search for users you can send messages to (filtered by permissions)
- `GET /api/users/{user_id}` - Get user details

### Departments
- `POST /api/departments` - Create department (Admin only)
- `GET /api/departments` - List departments
- `GET /api/departments/{dept_id}` - Get department details

### Roles
- `POST /api/roles` - Create role (Admin only)
- `GET /api/roles` - List roles
- `GET /api/roles/{role_id}` - Get role details

### Communication Rules
- `POST /api/communication-rules/permanent` - Create permanent rule (Admin only)
- `POST /api/communication-rules/request` - Request temporary access
- `GET /api/communication-rules/pending` - Get pending requests (Manager/Admin)
- `POST /api/communication-rules/approve` - Approve/reject request (Manager/Admin)
- `GET /api/communication-rules` - List rules
- `DELETE /api/communication-rules/{rule_id}` - Delete rule (Admin only)

### Messages
- `POST /api/messages/send` - Send a message (permission checked automatically, optionally sends email)
- `GET /api/messages/sent` - Get sent messages
- `GET /api/messages/received` - Get received messages
- `GET /api/messages/logs` - Get all message logs (Admin/Auditor only)

### Audit
- `GET /api/audit/communication-rules` - Audit communication rules
- `GET /api/audit/message-logs` - Audit message logs
- `GET /api/audit/user-activity/{user_id}` - Get user activity report

## Usage Examples

### 1. Create an Admin User

First, create departments and roles, then create a user:

```bash
# Create a department
curl -X POST "http://localhost:8000/api/departments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "IT"}'

# Create an admin user (requires admin token or manual DB insertion)
```

### 2. Search for Users You Can Message

```bash
# Search for users by name or email (only shows users you can communicate with)
curl -X GET "http://localhost:8000/api/users/search?q=john" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by department
curl -X GET "http://localhost:8000/api/users/search?dept_id=2" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Combine search and department filter
curl -X GET "http://localhost:8000/api/users/search?q=john&dept_id=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Note:** This endpoint only returns users you can actually send messages to based on:
- Same department (always allowed)
- Permanent communication rules
- Active temporary rules (if you're the requester or it's department-wide)

### 3. Request Temporary Access

```bash
curl -X POST "http://localhost:8000/api/communication-rules/request" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_dept_id": 2,
    "reason": "Need to coordinate on project",
    "expiry_hours": 24
  }'
```

### 4. Approve Request (Manager)

```bash
curl -X POST "http://localhost:8000/api/communication-rules/approve" \
  -H "Authorization: Bearer MANAGER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_id": 1,
    "approve": true,
    "reason": "Approved for project coordination"
  }'
```

### 5. Send a Message

```bash
curl -X POST "http://localhost:8000/api/messages/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": 5,
    "subject": "Project Update",
    "message_content": "Here is the update..."
  }'
```

## Database Schema (PostgreSQL)

### Tables
- **departments**: Department information
- **roles**: User roles (admin, manager, user, auditor)
- **users**: User accounts with department and role assignments
- **communication_rules**: Rules governing inter-department communication
- **message_logs**: All message attempts (sent/blocked) with timestamps

All tables are automatically created on application startup using async SQLAlchemy with PostgreSQL.

## Email Configuration

The system supports sending emails when messages are sent. To enable:

1. Set `ENABLE_EMAIL=True` in your `.env` file
2. Configure your SMTP settings:
   - **Gmail**: Use an App Password (not your regular password)
     - Enable 2-Step Verification
     - Go to Google Account > Security > App passwords
     - Generate an app password and use it as `MAIL_PASSWORD`
   - **Other providers**: Use their SMTP settings

### Email Providers Examples:
- **Gmail**: `smtp.gmail.com`, port `587`, STARTTLS
- **Outlook**: `smtp-mail.outlook.com`, port `587`, STARTTLS
- **Yahoo**: `smtp.mail.yahoo.com`, port `587`, STARTTLS

If email is disabled or fails, messages are still logged in the database.

## Security Notes

- Change `SECRET_KEY` in production
- Use environment variables for sensitive configuration
- Consider using PostgreSQL for production instead of SQLite
- Implement rate limiting for production
- Configure CORS appropriately for your frontend domain
- Never commit `.env` file with real credentials
- Use App Passwords for email accounts (not regular passwords)

## License

Private use only.

