# Omnidocs - Universal Documentation Converter

A powerful Python tool to convert documentation sites (GitBook, MkDocs, Docusaurus, etc.) to PDF and Markdown formats. Perfect for creating offline documentation, building LLM training datasets, and making documentation accessible for AI applications.

## Features

- **Universal Documentation Support**: Works with GitBook, MkDocs, Docusaurus, and other documentation platforms
- **Multiple Output Formats**: Convert to PDF, Markdown, or both simultaneously
- **LLM-Ready Output**: Generate clean Markdown files perfect for AI/LLM consumption
- **Automatic Link Discovery**: Intelligently discovers all documentation pages from navigation menus
- **High-Quality PDF Output**: Preserves formatting, styles, and layout using Playwright
- **Customizable Options**: Configure page format, margins, and other settings
- **Fast & Efficient**: Optimized processing with progress tracking
- **Easy Installation**: Simple pip install with minimal dependencies

## Why Omnidocs?

- **Make Docs LLM-Ready**: Convert any documentation site to clean Markdown for use with Large Language Models
- **Offline Access**: Create PDF versions of online documentation for offline reading
- **Knowledge Base Creation**: Build comprehensive knowledge bases for RAG (Retrieval Augmented Generation) systems
- **Documentation Archival**: Archive documentation sites before they change or disappear
- **Training Data Generation**: Create datasets for fine-tuning language models

## Installation

### Prerequisites

- Python 3.8 or higher
- Playwright browsers (automatically installed)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/1to3for5vi7ate9x/omnidocs.git
cd omnidocs

# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Install via pip (when published)

```bash
pip install omnidocs
playwright install chromium
```

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Convert to PDF (default)
omnidocs https://docs.example.com/

# Convert to Markdown (LLM-ready format)
omnidocs https://docs.example.com/ --format markdown

# Convert to both PDF and Markdown
omnidocs https://docs.example.com/ --format both
```

#### Advanced Options

```bash
# Specify custom output directory
omnidocs https://docs.example.com/ \
  --format markdown \
  --output-dir my_docs

# Customize PDF formatting
omnidocs https://docs.example.com/ \
  --format pdf \
  --page-format Letter \
  --margin-top 15mm \
  --margin-bottom 15mm \
  --no-background

# Convert to both formats with custom settings
omnidocs https://docs.example.com/ \
  --format both \
  --output-dir documentation \
  --timeout 120
```

### Python API

```python
from gitbooktopdf import DocumentationConverter

# Convert to PDF
converter = DocumentationConverter(
    base_url="https://docs.example.com/",
    output_format="pdf"
)
converter.convert()

# Convert to Markdown
converter = DocumentationConverter(
    base_url="https://docs.example.com/",
    output_format="markdown"
)
converter.convert()

# Convert to both formats
converter = DocumentationConverter(
    base_url="https://docs.example.com/",
    output_format="both"
)
converter.convert()
```

#### Advanced Python Usage

```python
from gitbooktopdf import DocumentationConverter, MarkdownConverter

# Custom PDF options
pdf_options = {
    'format': 'A4',
    'print_background': True,
    'margin': {
        'top': '20mm',
        'bottom': '20mm',
        'left': '15mm',
        'right': '15mm'
    }
}

# Create converter with custom options
converter = DocumentationConverter(
    base_url="https://docs.example.com/",
    output_format="both",
    pdf_options=pdf_options
)

# Customize timeouts
converter.page_load_timeout = 90000  # 90 seconds
converter.network_idle_timeout = 10000  # 10 seconds

# Run conversion
converter.convert()

# Direct markdown conversion
markdown_converter = MarkdownConverter(
    base_url="https://docs.example.com/",
    output_dir="markdown_output"
)
links = ["https://docs.example.com/page1", "https://docs.example.com/page2"]
markdown_files = markdown_converter.convert_to_markdown(links)
markdown_converter.combine_markdown_files(markdown_files)
```

## CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `url` | | Documentation site URL (required) | - |
| `--format` | `-f` | Output format (pdf, markdown, both) | `pdf` |
| `--output-dir` | `-o` | Directory for output files | `{domain}_output` |
| `--final-pdf` | | Name of merged PDF | `{domain}_documentation.pdf` |
| `--page-format` | | PDF page format (A4, Letter, etc.) | `A4` |
| `--no-background` | | Disable background graphics | False |
| `--margin-top` | | Top margin | `20mm` |
| `--margin-bottom` | | Bottom margin | `20mm` |
| `--margin-left` | | Left margin | `20mm` |
| `--margin-right` | | Right margin | `20mm` |
| `--timeout` | | Page load timeout (seconds) | `60` |

## Output Formats

### PDF Output
- High-quality PDF with preserved formatting
- Configurable page size and margins
- Background graphics and images included
- Suitable for printing and offline reading

### Markdown Output
- Clean, readable Markdown format
- Metadata headers with source URLs
- Combined single file or individual files
- Perfect for:
  - LLM training and fine-tuning
  - RAG (Retrieval Augmented Generation) systems
  - Knowledge base creation
  - Version control and diffing
  - Text analysis and processing

## Project Structure

```
omnidocs/
├── src/
│   └── gitbooktopdf/           # Package directory (legacy name for compatibility)
│       ├── __init__.py           # Package initialization
│       ├── converter.py          # Main converter class
│       ├── markdown_converter.py # Markdown conversion module
│       └── cli.py                # Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_converter.py        # Converter tests
│   └── test_cli.py             # CLI tests
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
├── README.md                   # This file
└── .gitignore                 # Git ignore rules
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/1to3for5vi7ate9x/omnidocs.git
cd omnidocs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gitbooktopdf --cov-report=html

# Run specific test file
pytest tests/test_converter.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Check code style with Flake8
flake8 src/ tests/

# Type checking with MyPy
mypy src/
```

### Building and Publishing

```bash
# Build the package
python -m build

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Examples

### Converting Different Documentation Sites

```bash
# GitBook documentation
omnidocs https://docs.gitbook.com/ --format both

# MkDocs documentation
omnidocs https://www.mkdocs.org/ --format markdown

# Docusaurus documentation
omnidocs https://docusaurus.io/docs --format pdf

# Custom documentation site
omnidocs https://your-docs.example.com/ --format both
```

### Creating LLM Training Data

```python
from gitbooktopdf import DocumentationConverter
import os

# List of documentation sites to convert
sites = [
    "https://docs.python.org/3/",
    "https://docs.djangoproject.com/",
    "https://flask.palletsprojects.com/",
]

# Convert all to markdown for LLM training
for site in sites:
    converter = DocumentationConverter(
        site,
        output_format="markdown",
        output_dir=f"training_data/{os.path.basename(site)}"
    )
    if converter.convert():
        print(f"Converted: {site}")
    else:
        print(f"Failed: {site}")
```

### Building a RAG Knowledge Base

```python
from gitbooktopdf import MarkdownConverter
import os

# Convert documentation for RAG system
converter = MarkdownConverter(
    base_url="https://docs.example.com/",
    output_dir="rag_knowledge_base"
)

# Get all documentation links
links = converter.discover_links()

# Convert to individual markdown files
markdown_files = converter.convert_to_markdown(links)

# Create combined file for easier processing
converter.combine_markdown_files(markdown_files)

print(f"Knowledge base created with {len(markdown_files)} documents")
```

## Troubleshooting

### Common Issues

1. **Playwright not installed**
   ```bash
   playwright install chromium
   ```

2. **Timeout errors**
   - Increase timeout: `--timeout 120`
   - Check your internet connection
   - Some sites may have rate limiting

3. **Missing pages**
   - The tool looks for common navigation selectors
   - Some custom sites may need modifications
   - Check if the site requires authentication

4. **PDF generation fails**
   - Ensure you have write permissions
   - Check disk space
   - Try with `--no-background` option

5. **Markdown formatting issues**
   - Some complex HTML may not convert perfectly
   - Check the individual markdown files for issues
   - The tool preserves as much structure as possible

### Debug Mode

Set environment variable for verbose output:
```bash
export DEBUG=1
omnidocs https://docs.example.com/
```

## Use Cases

### For AI/ML Engineers
- Generate training datasets from documentation
- Create knowledge bases for RAG systems
- Build domain-specific language models
- Extract structured information for analysis

### For Developers
- Create offline documentation archives
- Version control documentation snapshots
- Compare documentation changes over time
- Build searchable documentation databases

### For Technical Writers
- Convert between documentation formats
- Archive documentation before migrations
- Create print-ready PDF versions
- Analyze documentation structure and content

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/) for reliable web automation
- PDF processing with [pypdf](https://github.com/py-pdf/pypdf)
- HTML parsing with [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- Markdown conversion with [markdownify](https://github.com/matthewwithanm/python-markdownify)

## Support

- Email: your.email@example.com
- Issues: [GitHub Issues](https://github.com/1to3for5vi7ate9x/omnidocs/issues)
- Discussions: [GitHub Discussions](https://github.com/1to3for5vi7ate9x/omnidocs/discussions)

## Changelog

### Version 2.0.0 (Current)
- Added Markdown output format for LLM-ready documentation
- Support for converting to both PDF and Markdown simultaneously
- Renamed project to Omnidocs to reflect universal documentation conversion
- Improved link discovery for various documentation platforms
- Added metadata headers to Markdown output
- Combined Markdown file generation

### Version 1.0.0
- Initial release
- Support for GitBook and common documentation platforms
- Automatic link discovery
- Customizable PDF options
- CLI and Python API

## Roadmap

- [ ] Add support for authenticated sites
- [ ] Implement caching for faster re-runs
- [ ] Add progress bar for long conversions
- [ ] Support for custom CSS injection
- [ ] Parallel page processing
- [ ] Docker container support
- [ ] Web UI for easy conversions
- [ ] Export to other formats (EPUB, DOCX)
- [ ] Chunking strategies for LLM context windows
- [ ] Integration with popular LLM frameworks