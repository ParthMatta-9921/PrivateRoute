"""
Password strength validator for PrivateRoute
Ensures passwords meet security requirements
"""
import re
from typing import Tuple

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength and return (is_valid, message)
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    """
    
    errors = []
    
    # Check length
    if len(password) < 8:
        errors.append("at least 8 characters")
    
    # Check uppercase
    if not re.search(r'[A-Z]', password):
        errors.append("at least one uppercase letter (A-Z)")
    
    # Check lowercase
    if not re.search(r'[a-z]', password):
        errors.append("at least one lowercase letter (a-z)")
    
    # Check digit
    if not re.search(r'[0-9]', password):
        errors.append("at least one number (0-9)")
    
    # Check special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("at least one special character (!@#$%^&*)")
    
    if errors:
        message = f"Password must contain: {', '.join(errors)}"
        return False, message
    
    return True, "Password is strong"


# Example usage
if __name__ == "__main__":
    test_passwords = [
        "weak",
        "WeakPass123",
        "StrongPass123!",
        "AnotherGood@Pass456"
    ]
    
    for pwd in test_passwords:
        is_valid, message = validate_password_strength(pwd)
        print(f"Password: {pwd}")
        print(f"Valid: {is_valid}")
        print(f"Message: {message}\n")
