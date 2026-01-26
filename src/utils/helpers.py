import random
import string

def generate_strong_password(length=16):
    """
    Generates a 16-character strong password with uppercase, lowercase, 
    digits, and special characters.
    """
    if length < 4:
        length = 4
        
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    
    # Ensure at least one of each type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*")
    ]
    
    # Fill remaining length
    password.extend(random.choice(chars) for _ in range(length - 4))
    
    # Shuffle to avoid predictable pattern
    random.shuffle(password)
    
    return "".join(password)

# JS script to detect password fields and notify Python
PASSWORD_DETECTION_SCRIPT = """
(function() {
    function suggestPassword(event) {
        const target = event.target;
        if (target.type === 'password') {
            // We'll notify Python side via a custom event or checking in a loop
            // But since we want "immediate" suggestion, we can trigger a signal.
            // Simplified: Python will check periodically or we can use QWebChannel.
            // For now, let's just make sure we capture the focus.
            console.log("PASSWORD_FIELD_FOCUS");
        }
    }

    document.addEventListener('focusin', suggestPassword);
})();
"""
