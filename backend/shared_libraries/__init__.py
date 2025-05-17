"""
Shared libraries for the Trip Planning Assistant application.
This package contains shared functionality used across the application.
"""

# Import the rate_limit_callback if available
try:
    from .callbacks import rate_limit_callback
except ImportError:
    rate_limit_callback = None

__all__ = [
    'rate_limit_callback'
]
