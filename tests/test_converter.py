"""Tests for GitBookToPDFConverter"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gitbooktopdf.converter import GitBookToPDFConverter


class TestGitBookToPDFConverter:
    """Test suite for GitBookToPDFConverter"""
    
    def test_init_with_valid_url(self):
        """Test initialization with valid URL"""
        converter = GitBookToPDFConverter("https://docs.example.com/")
        assert converter.base_url == "https://docs.example.com/"
        assert converter.output_dir == "docs_example_com_pdfs"
        assert converter.final_pdf == "docs_example_com_documentation.pdf"
    
    def test_init_with_custom_options(self):
        """Test initialization with custom options"""
        converter = GitBookToPDFConverter(
            "https://docs.example.com",
            output_dir="custom_output",
            final_pdf="custom.pdf"
        )
        assert converter.output_dir == "custom_output"
        assert converter.final_pdf == "custom.pdf"
    
    def test_init_with_invalid_url(self):
        """Test initialization with invalid URL"""
        with pytest.raises(ValueError):
            GitBookToPDFConverter("not-a-url")
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        converter = GitBookToPDFConverter("https://docs.example.com/")
        
        # Test various inputs
        assert converter.sanitize_filename("hello/world") == "hello_world"
        assert converter.sanitize_filename("file-name.html") == "file-name_html"
        assert converter.sanitize_filename("special!@#$%chars") == "special_chars"
        assert converter.sanitize_filename("https://example.com/path") == "path"
    
    @patch('gitbooktopdf.converter.requests.Session')
    def test_discover_links(self, mock_session):
        """Test link discovery"""
        converter = GitBookToPDFConverter("https://docs.example.com/")
        
        # Mock HTML response
        mock_response = Mock()
        mock_response.content = b'''
        <html>
            <nav>
                <a href="/page1">Page 1</a>
                <a href="/page2">Page 2</a>
                <a href="https://docs.example.com/page3">Page 3</a>
                <a href="https://other.com/page">External</a>
            </nav>
        </html>
        '''
        mock_response.raise_for_status = Mock()
        
        mock_session.return_value.get.return_value = mock_response
        converter.session = mock_session.return_value
        
        links = converter.discover_links()
        
        # Should include base URL and discovered links from same domain
        assert "https://docs.example.com/" in links
        assert any("page1" in link for link in links)
        assert any("page2" in link for link in links)
        assert any("page3" in link for link in links)
        # Should not include external links
        assert not any("other.com" in link for link in links)
    
    @patch('gitbooktopdf.converter.requests.Session')
    def test_discover_links_with_error(self, mock_session):
        """Test link discovery with network error"""
        converter = GitBookToPDFConverter("https://docs.example.com/")
        
        # Mock network error
        mock_session.return_value.get.side_effect = Exception("Network error")
        converter.session = mock_session.return_value
        
        links = converter.discover_links()
        
        # Should return at least the base URL
        assert links == ["https://docs.example.com/"]
    
    @patch('gitbooktopdf.converter.os.makedirs')
    @patch('gitbooktopdf.converter.GitBookToPDFConverter.discover_links')
    @patch('gitbooktopdf.converter.GitBookToPDFConverter.convert_to_pdfs')
    @patch('gitbooktopdf.converter.GitBookToPDFConverter.merge_pdfs')
    def test_convert_success(self, mock_merge, mock_convert_pdfs, mock_discover, mock_makedirs):
        """Test successful conversion process"""
        converter = GitBookToPDFConverter("https://docs.example.com/")
        
        # Mock successful flow
        mock_discover.return_value = ["https://docs.example.com/page1"]
        mock_convert_pdfs.return_value = ["page1.pdf"]
        mock_merge.return_value = True
        
        result = converter.convert()
        
        assert result is True
        mock_makedirs.assert_called_once()
        mock_discover.assert_called_once()
        mock_convert_pdfs.assert_called_once()
        mock_merge.assert_called_once()
    
    @patch('gitbooktopdf.converter.os.makedirs')
    @patch('gitbooktopdf.converter.GitBookToPDFConverter.discover_links')
    def test_convert_no_links(self, mock_discover, mock_makedirs):
        """Test conversion with no links found"""
        converter = GitBookToPDFConverter("https://docs.example.com/")
        
        mock_discover.return_value = []
        
        result = converter.convert()
        
        assert result is False
        mock_makedirs.assert_called_once()
        mock_discover.assert_called_once()