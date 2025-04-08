"""
Storage package for the tech-news-curator application.

This package provides classes for storing and formatting article digests
in various formats including Markdown and Email.
"""

from .markdown_storage import MarkdownStorage
from .email_digest import EmailDigest

__all__ = ['MarkdownStorage', 'EmailDigest']