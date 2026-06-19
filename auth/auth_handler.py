from db.supabase_client import supabase


def sign_up(email: str, password: str) -> tuple[bool, str]:
    """Create a new user account. Returns (success, message)."""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            return True, "Account created! You can now log in."
        return False, "Sign up failed. Try again."
    except Exception as e:
        return False, str(e)


def sign_in(email: str, password: str) -> tuple[bool, str]:
    """Log in an existing user. Returns (success, message_or_user_id)."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return True, response.user.id
        return False, "Invalid email or password."
    except Exception as e:
        return False, "Invalid email or password."


def sign_out():
    """Log out the current user."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass