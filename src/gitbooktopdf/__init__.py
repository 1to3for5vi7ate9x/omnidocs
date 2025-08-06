"""
Omnidocs - Universal Documentation Converter

A tool to convert GitBook and other documentation sites to PDF and Markdown formats.
Makes documentation LLM-ready and easily accessible.
"""

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .converter import DocumentationConverter, GitBookToPDFConverter
from .markdown_converter import MarkdownConverter
from .cli import main

__all__ = [
    'DocumentationConverter',
    'GitBookToPDFConverter',  # Backward compatibility
    'MarkdownConverter', 
    'main'
]