"""
Routes package.
Contains API route blueprints for the e-learning application.
"""

from .account_routes import account_bp
from .pmsas_routes import pmsas_bp

__all__ = ['account_bp', 'pmsas_bp']


