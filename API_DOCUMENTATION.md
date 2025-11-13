# PrivateRoute API Documentation

## Overview

PrivateRoute is a secure communication control system that manages inter-department messaging with role-based access control and temporary access requests. This documentation is for frontend developers integrating with the PrivateRoute backend API.

**Base URL:** `http://localhost:8000` (Development)

**API Prefix:** All endpoints start with `/api`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Authentication Endpoints](#authentication-endpoints)
3. [User Management](#user-management)
4. [Department Management](#department-management)
5. [Roles Management](#roles-management)
6. [Communication Rules](#communication-rules)
7. [Messages](#messages)
8. [Audit & Logging](#audit--logging)
9. [Error Handling](#error-handling)
10. [Data Models](#data-models)

---

## Authentication

### Authentication Flow

1. **Login** → Get JWT token
2. **Include JWT** in `Authorization: Bearer <token>` header for all subsequent requests
3. **Token Expiry** → Default 30 minutes; request new token when expired

### JWT Token Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Password Requirements (When Creating/Changing Passwords)

- **Minimum 8 characters**
- **At least one uppercase letter** (A-Z)
- **At least one lowercase letter** (a-z)
- **At least one digit** (0-9)
- **At least one special character** (!@#$%^&*)

✅ Valid examples: `SecurePass123!`, `MyPassword@456`, `NewPass789#abc`

---

## Authentication Endpoints

### 1. Login

**POST** `/api/auth/login`

Returns a JWT token for authentication.

**Request Body:**
```json
{
  "username": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized` - Incorrect email or password

---

### 2. Get Current User Profile

**GET** `/api/auth/me`

Requires authentication. Returns the current logged-in user's details.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "dept_id": 2,
  "role_id": 1,
  "role": {
    "id": 1,
    "name": "admin"
  },
  "department": {
    "id": 2,
    "name": "IT"
  }
}
```

---

### 3. Change Password

**POST** `/api/auth/change-password`

Allows authenticated users to change their password. Requires verification of current password.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecure@Pass456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully",
  "email": "john@example.com",
  "details": "Your password must contain: at least 8 characters, one uppercase letter, one lowercase letter, one digit, and one special character"
}
```

**Error Responses:**
- `400 Bad Request` - New password must be different / Password doesn't meet requirements
- `401 Unauthorized` - Current password is incorrect

---

## User Management

### 1. Create User

**POST** `/api/users`

Only admins can create users. Creates a new user with the specified role and department.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "TempPass123!",
  "dept_id": 2,
  "role_id": 3
}
```

**Response (201 Created):**
```json
{
  "id": 5,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "dept_id": 2,
  "role_id": 3
}
```

**Error Responses:**
- `403 Forbidden` - Only admins can create users
- `400 Bad Request` - Email already exists / Invalid department or role

---

### 2. List Users

**GET** `/api/users?skip=0&limit=100&dept_id=2`

Retrieve a paginated list of users. Can filter by department.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `dept_id` (optional) - Filter by department ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "dept_id": 2,
    "role_id": 1
  },
  {
    "id": 5,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "dept_id": 2,
    "role_id": 3
  }
]
```

---

### 3. Get User by ID

**GET** `/api/users/{user_id}`

Retrieve details of a specific user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "dept_id": 2,
  "role_id": 1,
  "role": {
    "id": 1,
    "name": "admin"
  },
  "department": {
    "id": 2,
    "name": "IT"
  }
}
```

**Error Responses:**
- `404 Not Found` - User not found

---

### 4. Delete User

**DELETE** `/api/users/{user_id}`

Only admins can delete users.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

**Error Responses:**
- `403 Forbidden` - Only admins can delete users
- `404 Not Found` - User not found

---

## Department Management

### 1. Create Department

**POST** `/api/departments`

Only admins can create departments.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Human Resources"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "Human Resources"
}
```

**Error Responses:**
- `403 Forbidden` - Only admins can create departments
- `400 Bad Request` - Department name already exists

---

### 2. List Departments

**GET** `/api/departments?skip=0&limit=100`

Retrieve all departments.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Finance"
  },
  {
    "id": 2,
    "name": "IT"
  },
  {
    "id": 3,
    "name": "Human Resources"
  }
]
```

---

### 3. Get Department by ID

**GET** `/api/departments/{dept_id}`

Retrieve details of a specific department.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "IT"
}
```

**Error Responses:**
- `404 Not Found` - Department not found

---

### 4. Delete Department

**DELETE** `/api/departments/{dept_id}`

Only admins can delete departments.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

**Error Responses:**
- `403 Forbidden` - Only admins can delete departments
- `404 Not Found` - Department not found

---

## Roles Management

### 1. List Roles

**GET** `/api/roles?skip=0&limit=100`

Retrieve all available roles in the system.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "admin"
  },
  {
    "id": 2,
    "name": "manager"
  },
  {
    "id": 3,
    "name": "user"
  },
  {
    "id": 4,
    "name": "auditor"
  }
]
```

**Default Roles:**
- **admin** - Full system access, can approve any communication rule
- **manager** - Can approve communication rules involving their department
- **user** - Standard user, can request temporary access
- **auditor** - Read-only access to audit logs

---

## Communication Rules

Communication rules control which departments can communicate with each other. There are two types:

1. **Permanent Rules** - Always active, created by admins
2. **Temporary Rules** - Time-limited, require manager/admin approval

### 1. Create Permanent Rule

**POST** `/api/communication-rules/permanent`

Only admins can create permanent rules that allow departments to communicate indefinitely.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "dept_a_id": 1,
  "dept_b_id": 2,
  "rule_type": "permanent",
  "reason": "Finance and IT need to coordinate on system upgrades"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "dept_a_id": 1,
  "dept_b_id": 2,
  "rule_type": "permanent",
  "reason": "Finance and IT need to coordinate on system upgrades",
  "requester_id": null,
  "approved_by_id": 1,
  "is_active": true,
  "user_specific": false,
  "expiry_timestamp": null
}
```

**Error Responses:**
- `403 Forbidden` - Only admins can create permanent rules
- `404 Not Found` - One or both departments not found
- `400 Bad Request` - Cannot create rule for same department / Rule already exists

---

### 2. Request Temporary Access

**POST** `/api/communication-rules/request`

Users can request temporary access to communicate with another department.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "target_dept_id": 3,
  "expiry_hours": 24,
  "reason": "Need to discuss HR policies",
  "target_user_id": null
}
```

**Parameters:**
- `target_dept_id` (required) - ID of the department to request access to
- `expiry_hours` (optional) - Hours until the rule expires (e.g., 24 = 24 hours from now)
- `reason` (optional) - Reason for the request
- `target_user_id` (optional) - If specified, access is limited to this specific user

**Response (201 Created):**
```json
{
  "id": 2,
  "dept_a_id": 2,
  "dept_b_id": 3,
  "rule_type": "temporary",
  "reason": "Need to discuss HR policies",
  "requester_id": 5,
  "approved_by_id": 5,
  "is_active": false,
  "user_specific": false,
  "expiry_timestamp": "2025-11-15T12:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Target department not found
- `400 Bad Request` - Cannot request access to your own department

---

### 3. Get Pending Requests

**GET** `/api/communication-rules/pending`

Managers and admins can view pending temporary access requests.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "dept_a_id": 2,
    "dept_b_id": 3,
    "rule_type": "temporary",
    "reason": "Need to discuss HR policies",
    "requester_id": 5,
    "approved_by_id": 5,
    "is_active": false,
    "user_specific": false,
    "expiry_timestamp": "2025-11-15T12:00:00Z"
  }
]
```

**Error Responses:**
- `403 Forbidden` - Only managers and admins can view pending requests

---

### 4. Approve or Reject Request

**POST** `/api/communication-rules/approve`

Managers can approve/reject requests for their department. Admins can approve/reject any request.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "rule_id": 2,
  "approve": true,
  "reason": "Approved by HR manager"
}
```

**Parameters:**
- `rule_id` (required) - ID of the rule to approve/reject
- `approve` (required) - `true` to approve, `false` to reject
- `reason` (optional) - Additional reason/comment

**Response (200 OK):**
```json
{
  "id": 2,
  "dept_a_id": 2,
  "dept_b_id": 3,
  "rule_type": "temporary",
  "reason": "Need to discuss HR policies | Approval: Approved by HR manager",
  "requester_id": 5,
  "approved_by_id": 2,
  "is_active": true,
  "user_specific": false,
  "expiry_timestamp": "2025-11-15T12:00:00Z"
}
```

**Error Responses:**
- `403 Forbidden` - You can only approve rules involving your department (if not admin)
- `404 Not Found` - Rule not found

---

### 5. List Communication Rules

**GET** `/api/communication-rules/?skip=0&limit=100&dept_id=2&rule_type=permanent`

Retrieve communication rules with optional filters.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `dept_id` (optional) - Filter by department ID
- `rule_type` (optional) - Filter by type: `permanent` or `temporary`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "dept_a_id": 1,
    "dept_b_id": 2,
    "rule_type": "permanent",
    "reason": "Finance and IT coordination",
    "approved_by_id": 1,
    "is_active": true,
    "user_specific": false,
    "expiry_timestamp": null
  }
]
```

---

### 6. Delete Communication Rule

**DELETE** `/api/communication-rules/{rule_id}`

Only admins can delete communication rules.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

**Error Responses:**
- `403 Forbidden` - Only admins can delete rules
- `404 Not Found` - Rule not found

---

## Messages

### 1. Send Message

**POST** `/api/messages/send`

Send a message to a user in another department. The system automatically checks if communication is permitted based on active rules.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "receiver_id": 5,
  "subject": "System Maintenance Schedule",
  "message": "We will be performing maintenance on Friday evening..."
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "sender_id": 1,
  "receiver_id": 5,
  "subject": "System Maintenance Schedule",
  "message": "We will be performing maintenance on Friday evening...",
  "status": "sent",
  "reason": null,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

**Error Responses:**
- `403 Forbidden` - Communication not permitted with this user
  - Response includes `reason` field explaining why (e.g., "No active communication rule", "Rule expired")
- `404 Not Found` - Receiver not found / Same department communication

---

### 2. Get Message History

**GET** `/api/messages/?skip=0&limit=100&status=sent`

Retrieve message history for the current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `status` (optional) - Filter by status: `sent` or `blocked`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "sender_id": 1,
    "receiver_id": 5,
    "subject": "System Maintenance Schedule",
    "message": "We will be performing maintenance...",
    "status": "sent",
    "reason": null,
    "timestamp": "2025-11-14T10:30:00Z"
  }
]
```

---

## Audit & Logging

### 1. Get Audit Trail for Rules

**GET** `/api/audit/rules?skip=0&limit=100&rule_id=1`

Retrieve audit logs for communication rules (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `rule_id` (optional) - Filter by specific rule ID

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "rule_id": 1,
    "action": "created",
    "performed_by": "admin@example.com",
    "timestamp": "2025-11-14T09:00:00Z"
  }
]
```

**Error Responses:**
- `403 Forbidden` - Only admins can view audit logs

---

### 2. Get Message Audit Log

**GET** `/api/audit/messages?skip=0&limit=100&status=blocked`

Retrieve audit logs for messages (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `status` (optional) - Filter by status: `sent` or `blocked`

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "sender_id": 2,
    "receiver_id": 3,
    "status": "blocked",
    "reason": "No active communication rule",
    "timestamp": "2025-11-14T10:15:00Z"
  }
]
```

---

### 3. Get User Activity Report

**GET** `/api/audit/user-activity/{user_id}`

Retrieve activity report for a specific user (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user_id": 1,
  "user_email": "john@example.com",
  "department": "IT",
  "role": "admin",
  "activities": [
    {
      "timestamp": "2025-11-14T09:00:00Z",
      "action": "created permanent rule",
      "details": "Finance <-> IT"
    },
    {
      "timestamp": "2025-11-14T10:30:00Z",
      "action": "sent message",
      "details": "to jane@example.com"
    }
  ]
}
```

**Error Responses:**
- `403 Forbidden` - Only admins can view user activity
- `404 Not Found` - User not found

---

## Error Handling

### Standard Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Status Code | Meaning |
|------------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource successfully created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input or request parameters |
| 401 | Unauthorized - Invalid or expired token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

### Example Error Response

```json
{
  "detail": "Communication not permitted with this user: No active communication rule between departments"
}
```

---

## Data Models

### User
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "dept_id": 2,
  "role_id": 1,
  "role": {
    "id": 1,
    "name": "admin"
  },
  "department": {
    "id": 2,
    "name": "IT"
  }
}
```

### Department
```json
{
  "id": 2,
  "name": "IT"
}
```

### Role
```json
{
  "id": 1,
  "name": "admin"
}
```

### CommunicationRule
```json
{
  "id": 1,
  "dept_a_id": 1,
  "dept_b_id": 2,
  "rule_type": "permanent",
  "reason": "Finance and IT coordination",
  "requester_id": null,
  "approved_by_id": 1,
  "is_active": true,
  "user_specific": false,
  "expiry_timestamp": null
}
```

### Message
```json
{
  "id": 1,
  "sender_id": 1,
  "receiver_id": 5,
  "subject": "System Maintenance",
  "message": "Message content here",
  "status": "sent",
  "reason": null,
  "timestamp": "2025-11-14T10:30:00Z"
}
```

---

## Quick Start for Frontend

### 1. Initialize API Client
```javascript
const API_BASE = "http://localhost:8000";
let authToken = null;

async function apiCall(method, endpoint, data = null) {
  const headers = {
    "Content-Type": "application/json"
  };
  
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  
  const config = {
    method,
    headers
  };
  
  if (data) {
    config.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "API Error");
  }
  
  return response.status === 204 ? null : await response.json();
}
```

### 2. Login
```javascript
async function login(email, password) {
  const formData = new FormData();
  formData.append("username", email);
  formData.append("password", password);
  
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    body: formData
  });
  
  const data = await response.json();
  authToken = data.access_token;
  return data;
}
```

### 3. Get Current User
```javascript
async function getCurrentUser() {
  return await apiCall("GET", "/api/auth/me");
}
```

### 4. Send Message
```javascript
async function sendMessage(receiverId, subject, message) {
  return await apiCall("POST", "/api/messages/send", {
    receiver_id: receiverId,
    subject,
    message
  });
}
```

---

## Support & Contact

For API issues or questions, please refer to the backend documentation or contact the development team.

**Last Updated:** November 14, 2025
