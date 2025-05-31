# Ham Radio QSL Card Generator

A Python script that generates professional QSL cards from ham radio contact CSV files with customizable templates and configuration options.

## Features

- **Configurable Layout**: JSON configuration for complete customization
- **Multiple Card Support**: Handle multiple contacts per card (configurable limit)
- **Template Support**: Use custom background images or blank cards
- **Digital Mode Highlighting**: Color-coded digital modes
- **POTA Integration**: Display POTA references and comments
- **Batch Processing**: Group contacts by callsign with automatic card numbering
- **Output Management**: Smart directory handling with user prompts

## System Requirements

### Windows
- **OS**: Windows 10/11 (64-bit recommended)
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 500MB free space
- **Fonts**: Arial (arial.ttf, arialbd.ttf) - usually pre-installed

### macOS
- **OS**: macOS 10.15 (Catalina) or later
- **Python**: 3.8 or higher (install via Homebrew recommended)
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 500MB free space
- **Fonts**: Arial or system fonts

### Linux
- **OS**: Ubuntu 18.04+, Debian 10+, CentOS 8+, or equivalent
- **Python**: 3.8 or higher
- **Memory**: 1GB RAM minimum, 2GB recommended
- **Storage**: 500MB free space
- **Fonts**: Liberation fonts or Microsoft fonts package

## Installation

### Quick Install (All Platforms)
```bash
# Clone the repository
git clone https://github.com/yourusername/qsl-card-generator.git
cd qsl-card-generator

# Install dependencies
pip install -r requirements.txt

# Run with sample data
python qsl_generator.py sample_contacts.csv
```

### Platform-Specific Installation

#### Windows
```powershell
# Install Python from python.org or Microsoft Store
# Open Command Prompt or PowerShell as Administrator

# Install dependencies
pip install Pillow

# Optional: Install fonts if needed
# Download Arial fonts to C:\Windows\Fonts\
```

#### macOS
```bash
# Install Python via Homebrew
brew install python3

# Install dependencies
pip3 install Pillow

# Optional: Install Microsoft fonts
brew install --cask font-microsoft-office
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install system dependencies
sudo apt install python3-tk fonts-liberation

# Install Python dependencies
pip3 install Pillow

# Optional: Install Microsoft fonts
sudo apt install ttf-mscorefonts-installer
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip
# Fedora
sudo dnf install python3 python3-pip

# Install dependencies
pip3 install Pillow

# Install fonts
sudo yum install liberation-fonts
# or
sudo dnf install liberation-fonts
```

## Usage Examples

### Basic Usage
```bash
# Generate cards from CSV file
python qsl_generator.py contacts.csv

# Use custom template image
python qsl_generator.py contacts.csv template.jpg

# Specify output directory
python qsl_generator.py contacts.csv -d my_qsl_cards

# Use custom configuration
python qsl_generator.py contacts.csv -c my_config.json
```

### Advanced Usage
```bash
# Batch contacts by callsign (multiple cards per station)
python qsl_generator.py contacts.csv --batch-by-call

# Preview first 3 contacts without generating cards
python qsl_generator.py contacts.csv --sample

# Complete example with all options
python qsl_generator.py my_contacts.csv my_template.jpg \
  --config custom_config.json \
  --output-dir final_cards \
  --batch-by-call
```

### CSV File Format
Your CSV file should contain these columns (case-insensitive):
```csv
call,qso_date,time_on,freq,mode,submode,rst_sent,rst_rcvd,band,comment_intl,pota_ref
W1ABC,2024-01-15,1430,14.074,DATA,FT8,+05,-12,20m,73 from grid FN42,
K2XYZ,2024-01-15,1445,14.230,SSB,,59,57,20m,Nice signal!,K-1234
```

### Configuration Examples

#### Basic Configuration (qsl_config.json)
```json
{
  "table": {
    "max_contacts": 8
  },
  "fonts": {
    "sizes": {
      "large": 28,
      "medium": 20
    }
  },
  "confirmation_text": {
    "show_border": false
  }
}
```

#### Advanced Configuration
```json
{
  "card": {
    "width": 1800,
    "height": 1200
  },
  "colors": {
    "digital_mode": "#ff6600",
    "pota_ref": "#0080ff"
  },
  "table": {
    "max_contacts": 10,
    "y_percent": 0.40
  }
}
```

## Repository Setup Instructions

### 1. Initialize Git Repository
```bash
# Create new directory
mkdir qsl-card-generator
cd qsl-card-generator

# Initialize git
git init
git branch -M main
```

### 2. Create Project Structure
```
qsl-card-generator/
├── qsl_generator.py          # Main script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # License file
├── .gitignore              # Git ignore rules
├── config/
│   ├── default_config.json # Default configuration
│   └── sample_config.json  # Example configurations
├── examples/
│   ├── sample_contacts.csv # Sample data
│   └── sample_template.jpg # Sample template
├── docs/
│   ├── CONFIGURATION.md    # Configuration guide
│   └── TROUBLESHOOTING.md  # Common issues
└── tests/
    └── test_generator.py   # Unit tests
```

### 3. Create Essential Files

#### requirements.txt
```
Pillow>=9.0.0
```

#### .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# QSL Generator specific
qsl_cards/
output/
*.png
*.jpg
*.jpeg
!examples/*.jpg
!examples/*.png
config/local_*.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

#### LICENSE (MIT License)
```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 4. Create and Push to GitHub
```bash
# Add all files
git add .
git commit -m "Initial commit: QSL Card Generator v1.2.0"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/qsl-card-generator.git
git push -u origin main
```

## Configuration Guide

### Card Dimensions
- **Standard QSL**: 1650x1050 (5.5" x 3.5" at 300 DPI)
- **Large Format**: 1800x1200 (6" x 4" at 300 DPI)
- **Custom**: Adjust `card.width` and `card.height`

### Color Schemes
```json
{
  "colors": {
    "header_bg": "#2c3e50",
    "header_text": "white",
    "digital_mode": "#e74c3c",
    "pota_ref": "#3498db",
    "comment": "#27ae60"
  }
}
```

### Font Configuration
```json
{
  "fonts": {
    "primary": "arial.ttf",
    "bold": "arialbd.ttf",
    "sizes": {
      "large": 24,
      "medium": 18,
      "small": 14
    }
  }
}
```

## Troubleshooting

### Common Issues

**"Font not found" error**
- Windows: Ensure Arial fonts are in C:\Windows\Fonts\
- macOS: Install Microsoft Office fonts
- Linux: Install `fonts-liberation` or `ttf-mscorefonts-installer`

**"Permission denied" when clearing output directory**
- Close any image viewers showing QSL cards
- Run terminal as administrator (Windows)
- Check file permissions

**Cards look too small/large**
- Adjust DPI settings in your image viewer
- Modify `card.width` and `card.height` in config
- Check template image resolution

**CSV parsing errors**
- Ensure CSV has proper headers
- Check for special characters in callsigns
- Verify date/time formats

### Performance Tips

- Use smaller template images for faster processing
- Limit contacts per card for better readability
- Process large datasets in batches
- Use SSD storage for better I/O performance

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: [your-email@example.com]
- **QRZ**: [Your callsign]

## Changelog

### v1.2.0 (2024-05-30)
- Added configurable contact limits per card
- Improved Additional Information section layout
- Added output directory management
- Enhanced configuration options

### v1.1.0 (2024-05-15)
- Added confirmation text border control
- Improved font handling
- Better error handling

### v1.0.0 (2024-05-01)
- Initial release
- Basic QSL card generation
- Template support
- CSV import functionality