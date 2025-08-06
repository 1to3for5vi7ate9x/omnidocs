#!/usr/bin/env python3
"""
Documentation Converter
Convert GitBook and other documentation sites to PDF and Markdown formats
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from pypdf import PdfWriter
import time
import re
from typing import List, Dict, Optional
from .markdown_converter import MarkdownConverter


class DocumentationConverter:
    """Convert documentation sites to various formats (PDF, Markdown)"""
    
    def __init__(
        self,
        base_url: str,
        output_dir: Optional[str] = None,
        final_pdf: Optional[str] = None,
        pdf_options: Optional[Dict] = None,
        output_format: str = "pdf"
    ):
        """
        Initialize the converter
        
        Args:
            base_url: The base URL of the documentation site
            output_dir: Directory to save individual files
            final_pdf: Name of the final combined PDF
            pdf_options: Playwright PDF options
            output_format: Output format ('pdf', 'markdown', or 'both')
        """
        # Validate and normalize URL
        if not base_url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'
        self.output_format = output_format.lower()
        
        if self.output_format not in ['pdf', 'markdown', 'both']:
            raise ValueError("Output format must be 'pdf', 'markdown', or 'both'")
        
        # Generate output names based on domain if not provided
        parsed_url = urlparse(self.base_url)
        domain_name = parsed_url.netloc.replace('www.', '').replace('.', '_')
        
        # Set output directories based on format
        if self.output_format == 'markdown':
            self.output_dir = output_dir or f"{domain_name}_markdown"
        elif self.output_format == 'both':
            self.output_dir = output_dir or f"{domain_name}_output"
            self.pdf_dir = os.path.join(self.output_dir, "pdfs")
            self.markdown_dir = os.path.join(self.output_dir, "markdown")
        else:  # pdf
            self.output_dir = output_dir or f"{domain_name}_pdfs"
        
        self.final_pdf = final_pdf or f"{domain_name}_documentation.pdf"
        
        # PDF options with defaults
        self.pdf_options = pdf_options or {}
        self.pdf_options.setdefault('format', 'A4')
        self.pdf_options.setdefault('print_background', True)
        self.pdf_options.setdefault('margin', {
            'top': '20mm',
            'bottom': '20mm',
            'left': '20mm',
            'right': '20mm'
        })
        
        # Timeouts
        self.page_load_timeout = 60000  # milliseconds
        self.network_idle_timeout = 5000  # milliseconds
        
        self.session = requests.Session()
    
    def sanitize_filename(self, name: str) -> str:
        """Remove invalid characters for filenames"""
        name = re.sub(r'^https?://[^/]+/', '', name)
        name = re.sub(r'[^\w\-]+', '_', name)
        name = name.strip('_').strip('-')
        return name[:100]
    
    def discover_links(self) -> List[str]:
        """
        Find all relevant documentation links from the base URL
        
        Returns:
            List of documentation URLs to convert
        """
        print(f"Starting link discovery from: {self.base_url}")
        doc_links = []
        processed = {self.base_url}
        
        try:
            response = self.session.get(self.base_url, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple common selectors for navigation areas
            nav_selectors = [
                'nav',
                '[role="navigation"]',
                '.sidebar',
                '.nav-sidebar',
                '.docs-sidebar',
                '.toc',
                '.table-of-contents',
                'aside',
                '.menu',
                '.navigation',
                '.gitbook-sidebar',
                '.book-summary'
            ]
            
            nav_area = None
            for selector in nav_selectors:
                nav_area = soup.select_one(selector)
                if nav_area:
                    print(f"  Found navigation area using selector: {selector}")
                    break
            
            if not nav_area:
                print("Warning: Could not find navigation element. Using entire page.")
                nav_area = soup.body
            
            # Find all links in navigation
            page_links = nav_area.find_all('a', href=True)
            temp_links = []
            
            for link in page_links:
                href = link['href']
                absolute_url = urljoin(self.base_url, href)
                parsed_url = urlparse(absolute_url)
                cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                
                # Only include links from the same domain
                if (parsed_url.netloc == urlparse(self.base_url).netloc and
                    cleaned_url not in processed):
                    # Avoid non-documentation files
                    path_part = parsed_url.path
                    if '.' not in os.path.basename(path_part) or \
                       path_part.lower().endswith(('.html', '.htm', '/')):
                        print(f"    Found doc link: {cleaned_url}")
                        processed.add(cleaned_url)
                        temp_links.append(cleaned_url)
            
            # Start with base URL if not in links
            if self.base_url not in temp_links:
                doc_links.append(self.base_url)
            
            # Add unique links
            doc_links.extend(list(dict.fromkeys(temp_links)))
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {self.base_url}: {e}")
            if not doc_links:
                doc_links.append(self.base_url)
        except Exception as e:
            print(f"  Error processing {self.base_url}: {e}")
            if not doc_links:
                doc_links.append(self.base_url)
        
        print(f"Found {len(doc_links)} documentation pages to convert")
        return doc_links
    
    def convert_to_pdfs(self, links: List[str]) -> List[str]:
        """
        Convert a list of URLs to individual PDF files
        
        Args:
            links: List of URLs to convert
            
        Returns:
            List of generated PDF file paths
        """
        print("\n--- Starting PDF Conversion ---")
        pdf_files = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()
                page.set_default_timeout(self.page_load_timeout)
                
                for i, page_url in enumerate(links):
                    try:
                        # Generate filename
                        path_part = urlparse(page_url).path.strip('/')
                        filename_base = self.sanitize_filename(
                            path_part.replace('/', '_')
                        ) if path_part else "index"
                        output_filename = os.path.join(
                            self.output_dir,
                            f"{i:03d}_{filename_base}.pdf"
                        )
                        
                        print(f"Processing ({i+1}/{len(links)}): {page_url}")
                        
                        # Navigate and wait for content
                        page.goto(page_url, wait_until="networkidle", timeout=self.page_load_timeout)
                        page.wait_for_timeout(self.network_idle_timeout)
                        
                        # Generate PDF
                        pdf_options_with_path = self.pdf_options.copy()
                        pdf_options_with_path["path"] = output_filename
                        page.pdf(**pdf_options_with_path)
                        
                        pdf_files.append(output_filename)
                        print(f"  Saved: {output_filename}")
                        
                    except PlaywrightError as e:
                        print(f"  FAILED (Playwright Error) for {page_url}: {e}")
                    except Exception as e:
                        print(f"  FAILED (General Error) for {page_url}: {e}")
                
                context.close()
                browser.close()
                
        except Exception as e:
            print(f"\nError during Playwright execution: {e}")
        
        return pdf_files
    
    def merge_pdfs(self, pdf_files: List[str]) -> bool:
        """
        Merge individual PDFs into a single file
        
        Args:
            pdf_files: List of PDF file paths to merge
            
        Returns:
            True if successful, False otherwise
        """
        if not pdf_files:
            print("No PDFs to merge")
            return False
        
        print(f"\n--- Merging {len(pdf_files)} PDFs into {self.final_pdf} ---")
        merger = PdfWriter()
        
        try:
            for pdf_path in pdf_files:
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    try:
                        merger.append(pdf_path)
                        print(f"  Appending: {os.path.basename(pdf_path)}")
                    except Exception as e:
                        print(f"  Error appending {pdf_path}: {e}")
                else:
                    print(f"  Skipping missing/empty file: {pdf_path}")
            
            if len(merger.pages) > 0:
                merger.write(self.final_pdf)
                print(f"Successfully created: {self.final_pdf}")
                
                # Optimize the PDF
                try:
                    optimizer = PdfWriter()
                    optimizer.append(self.final_pdf)
                    optimizer.write(self.final_pdf)
                    optimizer.close()
                    print(f"Optimized: {self.final_pdf}")
                except Exception as e:
                    print(f"  Warning: Could not optimize PDF: {e}")
                
                return True
            else:
                print("No valid PDFs were merged")
                return False
                
        except Exception as e:
            print(f"Error during PDF merge: {e}")
            return False
        finally:
            merger.close()
    
    def convert(self) -> bool:
        """
        Main conversion process
        
        Returns:
            True if successful, False otherwise
        """
        print(f"Converting documentation from: {self.base_url}")
        print(f"Output format: {self.output_format}")
        print(f"Output directory: {self.output_dir}\n")
        
        # Create output directories
        if self.output_format == 'both':
            os.makedirs(self.pdf_dir, exist_ok=True)
            os.makedirs(self.markdown_dir, exist_ok=True)
        else:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Discover links
        links = self.discover_links()
        if not links:
            print("No documentation links found")
            return False
        
        success = True
        
        # Convert based on format
        if self.output_format in ['pdf', 'both']:
            # Convert to PDFs
            if self.output_format == 'both':
                # Temporarily set output_dir to pdf_dir
                original_dir = self.output_dir
                self.output_dir = self.pdf_dir
            
            pdf_files = self.convert_to_pdfs(links)
            pdf_success = self.merge_pdfs(pdf_files)
            
            if self.output_format == 'both':
                self.output_dir = original_dir
            
            success = success and pdf_success
        
        if self.output_format in ['markdown', 'both']:
            # Convert to Markdown
            if self.output_format == 'both':
                markdown_converter = MarkdownConverter(self.base_url, self.markdown_dir)
            else:
                markdown_converter = MarkdownConverter(self.base_url, self.output_dir)
            
            markdown_files = markdown_converter.convert_to_markdown(links)
            markdown_success = markdown_converter.combine_markdown_files(markdown_files)
            
            success = success and markdown_success
        
        print("\n--- Conversion Complete ---")
        return success


# Backward compatibility
GitBookToPDFConverter = DocumentationConverter