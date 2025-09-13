import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from shared_func.cognito_func import is_authenticated, get_current_user, logout_user

def test_is_authenticated():
    """Test authentication check"""
    result = is_authenticated()
    assert isinstance(result, bool)

def test_get_current_user():
    """Test getting current user"""
    user = get_current_user()
    assert user is None or isinstance(user, dict)

def test_logout_user():
    """Test user logout"""
    try:
        logout_user()
        assert True
    except Exception:
        assert False, "Logout should not raise exception"
