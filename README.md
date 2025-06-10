# Ham Radio QSL Card Generator

**Version:** 1.4.0  
**Author:** Joel Vazquez, WE0DX  
**License:** MIT

A Python script that reads ham radio contacts from a CSV file and generates professional QSL cards using customizable image templates. Perfect for amateur radio operators who want to automate their QSL card creation process.

## Features

- **Template Support**: Use your own QSL card design templates or generate blank cards
- **CSV Import**: Import contacts from popular logging software (ADIF CSV format)
- **Multi-Contact Cards**: Configurable number of contacts per card (default: 5)
- **Callsign Batching**: Group multiple contacts by callsign on single cards
- **Digital Mode Highlighting**: Automatic color coding for digital modes (FT8, PSK31, etc.)
- **POTA Support**: Display Parks on the Air (POTA) references
- **Configuration Management**: JSON-based configuration with easy management commands
- **Font Customization**: Configurable fonts for different sections
- **Output Control**: Customizable output directory and image quality
- **Verify for Updates**: Will check for available updates from Github repo

## Requirements

- Python 3.6+
- Pillow (PIL) library

```bash
pip install Pillow
```

## Installation

1. Clone or download this repository
2. Install dependencies: `pip install Pillow`
3. Place your QSL card template image in the same directory (optional)
4. Prepare your contacts CSV file

## Quick Start
## Installation

### Quick Install (All Platforms)
```bash
# Clone the repository
git clone https://github.com/vazquezrodjoel/ham-qsl-generator.git
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

### Basic Usage

```bash
# Generate cards with default settings
python qsl_generator.py contacts.csv

# Use a specific template image
python qsl_generator.py contacts.csv template.jpg

# Use custom configuration file
python qsl_generator.py contacts.csv --config my_config.json
```

### Configuration Management

```bash
# Create default configuration file
python qsl_generator.py --create-default-config

# Update existing config with new defaults
python qsl_generator.py --update-config

# Reset configuration (creates backup)
python qsl_generator.py --reset-config
```
### Update Management

```bash
# Check for updates from GitHub repository
python qsl_generator.py --check-updates
```
```bash
# Update script from GitHub (interactive)
python qsl_generator.py --update-script
```
```bash
# Disable automatic update checking for this run
python qsl_generator.py --disable-update-check
```          

## CSV Format

Your CSV file should contain the following columns (case-insensitive):

| Column | Description | Required |
|--------|-------------|----------|
| call | Callsign | Yes |
| qso_date | Date (YYYY-MM-DD, MM/DD/YYYY, etc.) | Yes |
| time_on | Time (HHMM or HH:MM format) | Yes |
| freq | Frequency in MHz or Hz | Yes |
| mode | Operating mode (SSB, CW, FT8, etc.) | Yes |
| submode | Sub-mode (optional) | No |
| rst_sent | RST sent | No |
| rst_rcvd | RST received | No |
| band | Band (auto-calculated if not provided) | No |
| comment_intl | Comments | No |
| pota_ref | POTA reference (e.g., K-1234) | No |

### Example CSV

```csv
call,qso_date,time_on,freq,mode,submode,rst_sent,rst_rcvd,comment_intl,pota_ref
W1ABC,2024-05-15,1430,14.074,MFSK,FT8,+03,-10,Great signal!,K-1234
VE2XYZ,2024-05-15,1445,21.200,SSB,,59,59,Thanks for POTA!,K-1234
JA1TEST,2024-05-16,0800,7.074,MFSK,FT4,-05,+12,First JA contact,
```

## Configuration

The script uses a JSON configuration file (`qsl_config.json` by default) to customize appearance and behavior. Key configuration sections include:

### Card Dimensions
```json
"card": {
  "width": 1650,
  "height": 1050
}
```

### Table Layout
```json
"table": {
  "max_contacts": 5,
  "x": 50,
  "y_percent": 0.45,
  "width_margin": 470,
  "height_percent": 0.3
}
```

### Fonts
```json
"fonts": {
  "primary": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
  "bold": "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
  "sizes": {
    "xlarge": 32,
    "large": 24,
    "medium": 18,
    "small": 14
  }
}
```

### Colors
```json
"colors": {
  "digital_mode": "#cc6600",
  "voice_mode": "#0066ff",
  "pota_ref": "#0066cc",
  "comment": "#006600"
}
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--config` | Specify configuration file |
| `--output-dir` | Output directory |
| `--batch-by-call` | Group contacts by callsign |
| `--sample` | Show first 3 contacts and exit |
| `--max-contacts` | Maximum contacts per card |
| `--quality` | Output image quality (1-100) |
| `--update-config` | Update config with missing defaults |
| `--create-default-config` | Create new default config |
| `--reset-config` | Reset config with backup |

## Output

The script generates PNG files in the specified output directory:

- **Single card per callsign**: `W1ABC.png`
- **Multiple cards per callsign**: `W1ABC_card_1_of_3.png`

Cards include:
- QSL confirmation text with contact count
- Formatted contact table with date, time, frequency, mode, RST reports
- Additional information section with comments and POTA references
- Digital mode color highlighting
- Professional layout matching your template

## Template Images

- Supports common image formats (PNG, JPG, etc.)
- Automatically resized to configured card dimensions
- If no template provided, generates cards with white background
- Template should be designed for standard QSL card proportions

## Supported Modes

### Digital Modes (Orange highlighting)
- FT8, FT4, PSK31, PSK63, RTTY, JT4, JT9, JT65
- MSK144, Q65, FSK441, WSPR, JS8, VARA

### Voice Modes (Blue highlighting)
- SSB, USB, LSB, AM, FM, PHONE

### Band Detection
Automatic band detection from frequency:
- 160m, 80m, 40m, 20m, 15m, 10m
- 6m, 2m, 70cm

## Troubleshooting

### Font Issues
If you see "Warning: Using default fonts", install system fonts or specify font paths in configuration:

**Ubuntu/Debian:**
```bash
sudo apt-get install fonts-ubuntu
```

**Windows:** Use system fonts like `arial.ttf`, `calibri.ttf`

**macOS:** Use system fonts in `/System/Library/Fonts/`

### Template Not Found
Ensure template image path is correct or use `--create-default-config` to see expected paths.

### CSV Import Issues
- Ensure CSV has required columns (`call`, `qso_date`, `time_on`, `freq`, `mode`)
- Check date format (YYYY-MM-DD recommended)
- Verify frequency is in MHz or Hz

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Joel Vazquez, WE0DX**  
Email: joelvazquez@we0dx.us

## Acknowledgments
- Python Pillow library for image processing capabilities
- POTA (Parks on the Air) program.

---

**73!** 📻