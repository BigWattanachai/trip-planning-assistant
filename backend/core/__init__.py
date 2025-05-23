"""
Core package for Trip Planning Assistant Backend.
This package contains core functionality like state management.
"""

from .state_manager import StateManager, state_manager

__all__ = [
    'StateManager',
    'state_manager'
]
