"""
Utilities package for the tech-news-curator application.

This package provides utility functions and helpers used across
the application, including logging configuration and common helpers.
"""

from .logger import configure_logging

__all__ = ['configure_logging']