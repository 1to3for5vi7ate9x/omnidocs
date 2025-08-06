#!/usr/bin/env python3
"""
Command-line interface for Omnidocs documentation converter
"""

import argparse
import sys
from .converter import DocumentationConverter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='omnidocs',
        description='Convert documentation sites to PDF and Markdown formats (LLM-ready)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Convert to PDF (default)
  omnidocs https://docs.example.com/
  
  # Convert to Markdown (LLM-ready format)
  omnidocs https://docs.example.com/ --format markdown
  
  # Convert to both PDF and Markdown
  omnidocs https://docs.example.com/ --format both
  
  # Custom output directory and PDF options
  omnidocs https://docs.example.com/ --output-dir custom_output --page-format Letter
        '''
    )
    
    # Required arguments
    parser.add_argument(
        'url',
        help='The base URL of the documentation site to convert'
    )
    
    # Optional arguments
    parser.add_argument(
        '--format', '-f',
        choices=['pdf', 'markdown', 'both'],
        default='pdf',
        help='Output format: pdf, markdown, or both (default: pdf)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        help='Directory to save output files (default: based on domain)'
    )
    
    parser.add_argument(
        '--final-pdf',
        help='Name of the final combined PDF (default: based on domain)'
    )
    
    # PDF formatting options
    parser.add_argument(
        '--page-format',
        choices=['A4', 'Letter', 'Legal', 'Tabloid', 'Ledger', 'A0', 'A1', 'A2', 'A3', 'A5', 'A6'],
        default='A4',
        help='PDF page format (default: A4)'
    )
    
    parser.add_argument(
        '--no-background',
        action='store_true',
        help='Disable background graphics in PDF'
    )
    
    parser.add_argument(
        '--margin-top',
        default='20mm',
        help='Top margin (default: 20mm)'
    )
    
    parser.add_argument(
        '--margin-bottom',
        default='20mm',
        help='Bottom margin (default: 20mm)'
    )
    
    parser.add_argument(
        '--margin-left',
        default='20mm',
        help='Left margin (default: 20mm)'
    )
    
    parser.add_argument(
        '--margin-right',
        default='20mm',
        help='Right margin (default: 20mm)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Page load timeout in seconds (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Prepare PDF options
    pdf_options = {
        'format': args.page_format,
        'print_background': not args.no_background,
        'margin': {
            'top': args.margin_top,
            'bottom': args.margin_bottom,
            'left': args.margin_left,
            'right': args.margin_right
        }
    }
    
    try:
        # Create converter
        converter = DocumentationConverter(
            base_url=args.url,
            output_dir=args.output_dir,
            final_pdf=args.final_pdf,
            pdf_options=pdf_options,
            output_format=args.format
        )
        
        # Set timeout
        converter.page_load_timeout = args.timeout * 1000  # Convert to milliseconds
        
        # Run conversion
        success = converter.convert()
        
        if success:
            print(f"\nSuccessfully converted {args.url}")
            if args.format in ['pdf', 'both']:
                print(f"PDF saved to: {converter.final_pdf}")
            if args.format in ['markdown', 'both']:
                if args.format == 'both':
                    print(f"Markdown saved to: {converter.markdown_dir}")
                else:
                    print(f"Markdown saved to: {converter.output_dir}")
            return 0
        else:
            print("\nConversion failed")
            return 1
            
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nConversion cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())