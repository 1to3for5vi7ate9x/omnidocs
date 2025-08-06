#!/usr/bin/env python3
"""
Markdown conversion module for documentation sites
"""

import os
import re
from typing import List, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.sync_api import sync_playwright, Error as PlaywrightError


class MarkdownConverter:
    """Convert documentation sites to Markdown format"""
    
    def __init__(self, base_url: str, output_dir: Optional[str] = None):
        """
        Initialize the markdown converter
        
        Args:
            base_url: The base URL of the documentation site
            output_dir: Directory to save markdown files
        """
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'
        
        # Generate output directory based on domain if not provided
        parsed_url = urlparse(self.base_url)
        domain_name = parsed_url.netloc.replace('www.', '').replace('.', '_')
        
        self.output_dir = output_dir or f"{domain_name}_markdown"
        self.combined_file = f"{domain_name}_documentation.md"
        
        # Timeouts
        self.page_load_timeout = 60000  # milliseconds
        self.network_idle_timeout = 5000  # milliseconds
    
    def clean_markdown(self, content: str) -> str:
        """
        Clean and format markdown content
        
        Args:
            content: Raw markdown content
            
        Returns:
            Cleaned markdown content
        """
        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Fix common markdown issues
        content = re.sub(r'```\n\n', '```\n', content)
        content = re.sub(r'\n\n```', '\n```', content)
        
        # Remove trailing whitespace
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)
        
        return content.strip()
    
    def extract_content_with_playwright(self, url: str) -> tuple[str, str]:
        """
        Extract content from a page using Playwright
        
        Args:
            url: URL to extract content from
            
        Returns:
            Tuple of (title, markdown_content)
        """
        title = ""
        content = ""
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()
                page.set_default_timeout(self.page_load_timeout)
                
                # Navigate to page
                page.goto(url, wait_until="networkidle", timeout=self.page_load_timeout)
                page.wait_for_timeout(self.network_idle_timeout)
                
                # Extract title
                title = page.title() or "Untitled"
                
                # Try to find main content area
                content_selectors = [
                    'main',
                    'article',
                    '[role="main"]',
                    '.content',
                    '.main-content',
                    '.documentation-content',
                    '.markdown-body',
                    '.doc-content',
                    '#content',
                    '.page-content',
                    '.post-content',
                    'body'  # Fallback to entire body
                ]
                
                html_content = None
                for selector in content_selectors:
                    if page.locator(selector).count() > 0:
                        html_content = page.locator(selector).first.inner_html()
                        break
                
                if not html_content:
                    html_content = page.content()
                
                # Convert HTML to markdown
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove navigation, sidebar, footer elements
                for element in soup.select('nav, .sidebar, .navigation, footer, .footer, aside'):
                    element.decompose()
                
                # Convert to markdown
                content = md(
                    str(soup),
                    heading_style="ATX",
                    code_language="python",
                    bullets="-",
                    strip=['script', 'style']
                )
                
                content = self.clean_markdown(content)
                
                context.close()
                browser.close()
                
        except Exception as e:
            print(f"  Error extracting content from {url}: {e}")
            # Fallback to basic extraction
            try:
                response = requests.get(url, timeout=20)
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string if soup.title else "Untitled"
                
                # Remove unwanted elements
                for element in soup.select('script, style, nav, .sidebar, footer'):
                    element.decompose()
                
                content = md(str(soup.body) if soup.body else str(soup))
                content = self.clean_markdown(content)
            except:
                content = f"Failed to extract content from {url}"
        
        return title, content
    
    def convert_to_markdown(self, links: List[str]) -> List[str]:
        """
        Convert a list of URLs to markdown files
        
        Args:
            links: List of URLs to convert
            
        Returns:
            List of generated markdown file paths
        """
        print("\n--- Starting Markdown Conversion ---")
        markdown_files = []
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        for i, url in enumerate(links):
            print(f"Processing ({i+1}/{len(links)}): {url}")
            
            # Extract content
            title, content = self.extract_content_with_playwright(url)
            
            # Generate filename
            path_part = urlparse(url).path.strip('/')
            filename_base = self.sanitize_filename(
                path_part.replace('/', '_')
            ) if path_part else "index"
            output_filename = os.path.join(
                self.output_dir,
                f"{i:03d}_{filename_base}.md"
            )
            
            # Add metadata header
            markdown_content = f"""---
title: {title}
source: {url}
---

# {title}

{content}
"""
            
            # Save markdown file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            markdown_files.append(output_filename)
            print(f"  Saved: {output_filename}")
        
        return markdown_files
    
    def sanitize_filename(self, name: str) -> str:
        """Remove invalid characters for filenames"""
        name = re.sub(r'^https?://[^/]+/', '', name)
        name = re.sub(r'[^\w\-]+', '_', name)
        name = name.strip('_').strip('-')
        return name[:100]
    
    def combine_markdown_files(self, markdown_files: List[str]) -> bool:
        """
        Combine individual markdown files into a single file
        
        Args:
            markdown_files: List of markdown file paths
            
        Returns:
            True if successful, False otherwise
        """
        if not markdown_files:
            print("No markdown files to combine")
            return False
        
        print(f"\n--- Combining {len(markdown_files)} markdown files ---")
        
        try:
            with open(self.combined_file, 'w', encoding='utf-8') as outfile:
                # Write main title
                outfile.write(f"# Documentation from {self.base_url}\n\n")
                outfile.write("---\n\n")
                outfile.write("## Table of Contents\n\n")
                
                # Generate table of contents
                toc_entries = []
                for i, filepath in enumerate(markdown_files):
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            lines = infile.readlines()
                            for line in lines:
                                if line.startswith('title:'):
                                    title = line.replace('title:', '').strip()
                                    toc_entries.append(f"{i+1}. [{title}](#{i+1}-{title.lower().replace(' ', '-')})")
                                    break
                
                outfile.write('\n'.join(toc_entries))
                outfile.write("\n\n---\n\n")
                
                # Combine all files
                for i, filepath in enumerate(markdown_files):
                    if os.path.exists(filepath):
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                            # Skip the metadata section for combined file
                            if content.startswith('---'):
                                # Find the end of metadata
                                lines = content.split('\n')
                                start_idx = 0
                                count = 0
                                for idx, line in enumerate(lines):
                                    if line.strip() == '---':
                                        count += 1
                                        if count == 2:
                                            start_idx = idx + 1
                                            break
                                content = '\n'.join(lines[start_idx:])
                            
                            outfile.write(f"\n## {i+1}. {content.strip()}\n\n")
                            outfile.write("---\n\n")
                
                print(f"Successfully created: {self.combined_file}")
                return True
                
        except Exception as e:
            print(f"Error combining markdown files: {e}")
            return False