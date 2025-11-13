# PrivateRoute API Testing Guide

## 1. CREATE DEPARTMENTS
Create multiple departments so users can communicate across them.

**Endpoint:** POST /api/departments
**Authorization:** Required (you're already logged in as admin)

Body:
```json
{"name": "HR"}
```

Then create more:
- {"name": "Finance"}
- {"name": "Operations"}
- {"name": "Sales"}

---

## 2. CREATE USERS
Create users in different departments with different roles.

**Endpoint:** POST /api/users
**Authorization:** Admin only (you have this)

Examples:

User 1 - Manager in HR:
```json
{
  "name": "John Manager",
  "email": "john@example.com",
  "password": "password123",
  "dept_id": 2,
  "role_id": 2
}
```

User 2 - Regular User in Finance:
```json
{
  "name": "Jane Finance",
  "email": "jane@example.com",
  "password": "password123",
  "dept_id": 3,
  "role_id": 3
}
```

User 3 - Regular User in HR:
```json
{
  "name": "Bob HR",
  "email": "bob@example.com",
  "password": "password123",
  "dept_id": 2,
  "role_id": 3
}
```

User 4 - Auditor:
```json
{
  "name": "Alice Auditor",
  "email": "alice@example.com",
  "password": "password123",
  "dept_id": 1,
  "role_id": 4
}
```

---

## 3. PERMANENT COMMUNICATION RULES
Allow departments to communicate permanently (Admin only).

**Endpoint:** POST /api/communication-rules/permanent
**Authorization:** Admin only

Example - Allow HR and Finance to communicate:
```json
{
  "dept_a_id": 2,
  "dept_b_id": 3,
  "rule_type": "permanent",
  "reason": "Cross-departmental project collaboration"
}
```

---

## 4. TEST MESSAGING (SAME DEPARTMENT)
Users in the same department can always message each other.

**Endpoint:** POST /api/messages/send
**Authorization:** Required

As the admin user (who's in IT dept_id=1), try sending to Bob (IT dept):
```json
{
  "receiver_id": 4,
  "subject": "Test Message",
  "message_content": "This is a test message within the same department"
}
```

Expected: ✅ Message SENT (same department = always allowed)

---

## 5. TEST PERMISSION BLOCKING
Try to send to a user you don't have permission for.

**Endpoint:** POST /api/messages/send

Try sending from admin to Jane (Finance) with no rules:
```json
{
  "receiver_id": 5,
  "subject": "Test",
  "message_content": "Can I message you?"
}
```

Expected: ❌ Message BLOCKED (no communication rule exists)
Response: 403 Forbidden - "No communication rule found between departments"

---

## 6. TEST PERMANENT RULES
After creating the permanent rule for HR↔Finance, try messaging again.

Send message from admin (IT) to Jane (Finance):
```json
{
  "receiver_id": 5,
  "subject": "Now Allowed",
  "message_content": "Now we can communicate!"
}
```

Expected: ✅ Message SENT (permanent rule exists)

---

## 7. TEMPORARY ACCESS REQUEST
Regular users can request temporary access.

**Endpoint:** POST /api/communication-rules/request
**Authorization:** Any authenticated user

Login as john@example.com (Manager in HR), then:
```json
{
  "target_dept_id": 1,
  "reason": "Need to coordinate with IT on system upgrade",
  "expiry_hours": 24
}
```

Response: Returns rule with is_active=False (pending approval)

---

## 8. VIEW PENDING REQUESTS
Managers can see pending requests for their department.

**Endpoint:** GET /api/communication-rules/pending
**Authorization:** Manager or Admin

As the admin (or a manager), you'll see the pending request.

---

## 9. APPROVE/REJECT REQUEST
Manager or Admin approves the request.

**Endpoint:** POST /api/communication-rules/approve
**Authorization:** Manager or Admin

```json
{
  "rule_id": 1,
  "approve": true,
  "reason": "Approved for system upgrade coordination"
}
```

Now the temporary rule is active and users can message!

---

## 10. TEST USER SEARCH
Search for users you can actually message (filtered by permissions).

**Endpoint:** GET /api/users/search
**Authorization:** Required

Parameters:
- q: search by name or email (optional)
- dept_id: filter by department (optional)

Example:
- `/api/users/search?q=john` - Find users named John you can message
- `/api/users/search?dept_id=3` - Find users in Finance dept_id=3 you can message

---

## 11. VIEW YOUR MESSAGES
Get all messages you sent or received.

**Endpoint:** GET /api/messages/sent
- See all messages you sent

**Endpoint:** GET /api/messages/received
- See all messages you received

---

## 12. AUDIT LOGS (Admin/Auditor Only)
View comprehensive audit information.

**Endpoint:** GET /api/audit/communication-rules
- See all communication rules

**Endpoint:** GET /api/audit/message-logs
- See all message logs with filters

Parameters:
- sender_id: filter by sender
- receiver_id: filter by receiver
- status_filter: 'sent' or 'blocked'
- start_date: messages from this date
- end_date: messages until this date

**Endpoint:** GET /api/audit/user-activity/{user_id}
- Get complete activity report for a user
- Shows all rules requested/approved
- Shows all messages sent/received

---

## TESTING WORKFLOW SUMMARY

1. ✅ Create 3-4 departments
2. ✅ Create 4-5 users with different roles
3. ✅ Test same-department messaging (should work)
4. ✅ Test cross-department without rules (should be blocked)
5. ✅ Create a permanent rule
6. ✅ Test cross-department with rule (should work)
7. ✅ Request temporary access
8. ✅ Approve temporary access
9. ✅ View messages and audit logs
10. ✅ Try different user roles (Manager, User, Auditor)

---

## QUICK ROLE REFERENCE

| Role | Permissions |
|------|-------------|
| **Admin** (role_id=1) | Create users, departments, permanent rules, delete rules, approve requests, view all data |
| **Manager** (role_id=2) | Approve/reject temporary access requests, send messages |
| **User** (role_id=3) | Request temporary access, send/receive messages |
| **Auditor** (role_id=4) | View-only access to audit logs, cannot send messages or make changes |

---

## API DOCUMENTATION
Visit: http://localhost:8000/docs (Swagger UI)
Or: http://localhost:8000/redoc (ReDoc)

Both provide interactive testing for all endpoints!
