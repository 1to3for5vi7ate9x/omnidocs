"""Tests for CLI interface"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gitbooktopdf.cli import main


class TestCLI:
    """Test suite for CLI interface"""
    
    @patch('gitbooktopdf.cli.GitBookToPDFConverter')
    def test_main_with_valid_url(self, mock_converter_class):
        """Test CLI with valid URL"""
        mock_converter = MagicMock()
        mock_converter.convert.return_value = True
        mock_converter.final_pdf = "output.pdf"
        mock_converter_class.return_value = mock_converter
        
        with patch('sys.argv', ['gitbooktopdf', 'https://docs.example.com/']):
            result = main()
        
        assert result == 0
        mock_converter_class.assert_called_once()
        mock_converter.convert.assert_called_once()
    
    @patch('gitbooktopdf.cli.GitBookToPDFConverter')
    def test_main_with_custom_options(self, mock_converter_class):
        """Test CLI with custom options"""
        mock_converter = MagicMock()
        mock_converter.convert.return_value = True
        mock_converter.final_pdf = "custom.pdf"
        mock_converter_class.return_value = mock_converter
        
        with patch('sys.argv', [
            'gitbooktopdf',
            'https://docs.example.com/',
            '--output-dir', 'custom_output',
            '--final-pdf', 'custom.pdf',
            '--format', 'Letter',
            '--no-background',
            '--timeout', '120'
        ]):
            result = main()
        
        assert result == 0
        
        # Check that converter was initialized with correct arguments
        call_args = mock_converter_class.call_args
        assert call_args.kwargs['output_dir'] == 'custom_output'
        assert call_args.kwargs['final_pdf'] == 'custom.pdf'
        assert call_args.kwargs['pdf_options']['format'] == 'Letter'
        assert call_args.kwargs['pdf_options']['print_background'] is False
    
    @patch('gitbooktopdf.cli.GitBookToPDFConverter')
    def test_main_with_conversion_failure(self, mock_converter_class):
        """Test CLI when conversion fails"""
        mock_converter = MagicMock()
        mock_converter.convert.return_value = False
        mock_converter_class.return_value = mock_converter
        
        with patch('sys.argv', ['gitbooktopdf', 'https://docs.example.com/']):
            result = main()
        
        assert result == 1
    
    @patch('gitbooktopdf.cli.GitBookToPDFConverter')
    def test_main_with_invalid_url(self, mock_converter_class):
        """Test CLI with invalid URL"""
        mock_converter_class.side_effect = ValueError("Invalid URL")
        
        with patch('sys.argv', ['gitbooktopdf', 'not-a-url']):
            result = main()
        
        assert result == 1
    
    @patch('gitbooktopdf.cli.GitBookToPDFConverter')
    def test_main_with_keyboard_interrupt(self, mock_converter_class):
        """Test CLI handling of keyboard interrupt"""
        mock_converter = MagicMock()
        mock_converter.convert.side_effect = KeyboardInterrupt()
        mock_converter_class.return_value = mock_converter
        
        with patch('sys.argv', ['gitbooktopdf', 'https://docs.example.com/']):
            result = main()
        
        assert result == 130  # Standard exit code for keyboard interrupt
    
    def test_help_option(self):
        """Test CLI help option"""
        with patch('sys.argv', ['gitbooktopdf', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0