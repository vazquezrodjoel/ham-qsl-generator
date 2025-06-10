#!/usr/bin/env python3
"""
Ham Radio QSL Card Generator with Configuration Support
Version: 1.3.0
Last Modified: 2025-05-30
Author: Joel Vazquez, WE0DX
License: MIT

This script reads ham radio contacts from a CSV file and generates
QSL cards using an image template. Features:
- Configuration file for easy customization
- Support for multiple cards per callsign (configurable contacts per card)
- POTA references and additional comments
- Digital mode color coding
- Confirmation text with optional border
- Output directory management

Requirements:
pip install Pillow

Usage:
python qsl_generator.py contacts.csv [template.jpg] --config config.json

# Update existing config with missing defaults
python qsl_generator.py --update-config

# Create new default config
python qsl_generator.py --create-default-config

# Reset config with backup
python qsl_generator.py --reset-config

# Use custom config file name
python qsl_generator.py --update-config -c my_config.json

Changelog:
v1.4.0 - Added configurable option to verify updates from Github Repository
v1.3.0 - Added configurable fonts per section from the configuration json file.
v1.2.0 - Added configurable contact limits, improved Additional Info section
v1.1.0 - Added confirmation text border control, output directory management
v1.0.0 - Initial release
"""

import csv
import json
import argparse
from datetime import datetime
from collections import defaultdict
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import shutil
from pathlib import Path
import requests
from packaging import version
import urllib.request
import tempfile

__version__ = "1.4.0"
__author__ = "Author: Joel Vazquez, WE0DX"
__email__ = "joelvazquez@we0dx.us"
__license__ = "MIT"

class QSLCardGenerator:
    
    def update_config_with_defaults(self, config_file):
        """Update existing config file with any missing default values"""
        print(f"Updating {config_file} with missing default values...")
        
        # Get the default config
        default_config = self.get_default_config()
        
        # Load existing config or create empty dict
        existing_config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    existing_config = json.load(f)
            except Exception as e:
                print(f"Error reading existing config: {e}")
                return False
        
        # Find missing keys
        missing_keys = []
        def find_missing_keys(default_dict, existing_dict, path=""):
            for key, value in default_dict.items():
                current_path = f"{path}.{key}" if path else key
                if key not in existing_dict:
                    missing_keys.append(current_path)
                elif isinstance(value, dict) and isinstance(existing_dict.get(key), dict):
                    find_missing_keys(value, existing_dict[key], current_path)
        
        find_missing_keys(default_config, existing_config)
        
        if not missing_keys:
            print("Configuration file is already up to date!")
            return True
        
        print(f"Found {len(missing_keys)} missing configuration keys:")
        for key in missing_keys:
            print(f"  + {key}")
        
        # Merge configurations (keeping existing values, adding missing defaults)
        updated_config = self.merge_configs(default_config, existing_config)
        
        try:
            # Create backup of existing config
            if os.path.exists(config_file):
                backup_file = f"{config_file}.backup"
                shutil.copy2(config_file, backup_file)
                print(f"Backup created: {backup_file}")
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(updated_config, f, indent=2)
            print(f"Configuration updated successfully: {config_file}")
            return True
            
        except Exception as e:
            print(f"Error updating config file: {e}")
            return False

    def create_default_config_file(self, config_file):
        """Create a new default configuration file"""
        if os.path.exists(config_file):
            response = input(f"Config file '{config_file}' already exists. Overwrite? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Operation cancelled.")
                return False
        
        default_config = self.get_default_config()
        
        try:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Default configuration created: {config_file}")
            return True
        except Exception as e:
            print(f"Error creating default config: {e}")
            return False

    def reset_config_with_backup(self, config_file):
        """Save current config as backup and create new default config"""
        if not os.path.exists(config_file):
            print(f"Config file '{config_file}' does not exist. Creating default configuration.")
            return self.create_default_config_file(config_file)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{config_file}.{timestamp}.old"
        
        try:
            # Create backup
            shutil.copy2(config_file, backup_file)
            print(f"Current configuration backed up to: {backup_file}")
            
            # Create new default config
            default_config = self.get_default_config()
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Default configuration recreated: {config_file}")
            return True
            
        except Exception as e:
            print(f"Error during config reset: {e}")
            return False

    def get_default_config(self):
        """Get the default configuration dictionary"""
        return {
            "output": {
                "default_directory": "qsl_cards",
                "quality": 95
            },
            "template": {
                "default_image": "QSLTemplate.png"
            },
            "generation": {
                "batch_by_call": True
            },
            "card": {
                "width": 1650,
                "height": 1050
            },
            "table": {
                "x": 50,
                "y_percent": 0.45,
                "width_margin": 470,
                "height_percent": 0.3,
                "max_contacts": 5,
                "header_height": 40,
                "min_row_height": 25,
                "max_row_height": 40
            },
            "additional_info": {
                "header_height": 40,
                "x": 50,
                "y_offset": 10,
                "width_margin": 470,
                "height_percent": 0.232,
                "show_default_message": True,
                "default_message": "Thanks for the contact(s)!",
                "default_messages": [
                    "Thanks for the contact(s)!",
                    "73 and thanks for the QSO!",
                    "Great contacts today!",
                    "Happy to work you!",
                    "Thanks for the chat!",
                    "Hope to catch you again on the other bands!",
                    "Enjoyed our QSO!",
                    "Thanks for stopping by!",
                    "Always a pleasure!",
                    "See you on the bands!"
                ],
                "comment_max_width": 800,
                "columns": {
                    "date_band_offset": 10,
                    "comment_offset": 200,
                    "pota_offset": 400
                },
                "fonts": {
                    "header": "bold",
                    "date_band": "medium",
                    "comment": "medium",
                    "pota": "medium",
                    "default_message": "large"
                }
            },
            "confirmation_text": {
                "show_border": False,
                "text_color": "black",
                "position": {
                    "x_offset": 10,
                    "y_offset": -40,
                    "min_y": 50
                }
            },
            "fonts": {
                "primary": "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "bold": "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
                "sizes": {
                "xlarge": 32,
                "large": 24,
                "medium": 18,
                "small": 14,
                "tiny": 12,
                "bold": 26
                },
                "section_sizes": {
                "confirmation_text": "xlarge",
                "table_header": "bold", 
                "table_data": "large",
                "additional_info_header": "bold",
                "additional_info_data": "medium"
                }
            },
            "colors": {
                "header_bg": "#4a4a4a",
                "header_text": "white",
                "row_bg_alt": "#f0f0f0",
                "digital_mode": "#cc6600",
                "voice_mode": "#0066ff",
                "pota_ref": "#0066cc",
                "comment": "#006600",
                "section_bg": "#f8f8f8",
                "default_message": "#666666"
            },
            "columns": {
                "widths_percent": [0.14,0.09,0.11,0.12,0.07,0.07,0.09,0.31],
                "headers": ["Date","UTC","Freq(MHz)","Mode/Sub","RST S","RST R","Band","Notes"]
            },
            "modes": {
                "digital": [
                "FT8",
                "FT4",
                "PSK31",
                "PSK63",
                "RTTY",
                "JT4",
                "JT9",
                "JT65",
                "MSK144",
                "Q65",
                "FSK441",
                "WSPR",
                "JS8",
                "VARA"
                ],
                "digital_main": [
                "MFSK",
                "PSK",
                "RTTY",
                "DATA",
                "DIGITAL"
                ],
                "voice": [
                "SSB",
                "USB",
                "LSB",
                "AM",
                "FM",
                "PHONE"
                ],
                "voice_main": [
                "SSB",
                "AM",
                "FM",
                "PHONE"
                ],
                "special_handling": {
                "FT8": "FT8",
                "MFSK/FT4": "FT4",
                "SSB/USB": "USB",
                "SSB/LSB": "LSB",
                "PHONE/USB": "USB",
                "PHONE/LSB": "LSB"
                }
            },
            "bands": [
                [
                1.8,
                2.0,
                "160m"
                ],
                [
                3.5,
                4.0,
                "80m"
                ],
                [
                7.0,
                7.3,
                "40m"
                ],
                [
                14.0,
                14.35,
                "20m"
                ],
                [
                21.0,
                21.45,
                "15m"
                ],
                [
                28.0,
                29.7,
                "10m"
                ],
                [
                50.0,
                54.0,
                "6m"
                ],
                [
                144.0,
                148.0,
                "2m"
                ],
                [
                420.0,
                450.0,
                "70cm"
                ]
            ],
            "update": {
                "github_repo": "vazquezrodjoel/ham-qsl-generator",  # Change to your repo
                "check_on_startup": True,
                "auto_check_interval_days": 7,
                "last_check_date": None,
                "current_version": "1.3.0",
                "update_script": True,
                "update_config": True,
                "backup_before_update": True
            }
        }

    def get_font_for_section(self, section_name):
        """Get the appropriate font for a given section based on configuration"""
        section_sizes = self.config['fonts'].get('section_sizes', {})
        size_name = section_sizes.get(section_name, 'medium')  # default to medium if not configured
        return self.fonts.get(size_name, self.fonts['medium'])
    
    def check_and_save_runtime_config(self, args, config_file):
        """Check if runtime arguments differ from config and offer to save them"""
        changes = {}
        
        # Check output directory
        config_output = self.config.get('output', {}).get('default_directory', 'qsl_cards')
        if args.output_dir and args.output_dir != config_output:
            changes['output.default_directory'] = args.output_dir
        
        # Check template image path
        config_template = self.config.get('template', {}).get('default_image', None)
        if args.template_image and args.template_image != config_template:
            changes['template.default_image'] = args.template_image
        
        # Check batch mode preference
        config_batch = self.config.get('generation', {}).get('batch_by_call', True)
        if args.batch_by_call != config_batch:
            changes['generation.batch_by_call'] = args.batch_by_call
        
        # Check max contacts per card (if you add this as a command line option)
        if hasattr(args, 'max_contacts') and args.max_contacts:
            config_max = self.config.get('table', {}).get('max_contacts', 5)
            if args.max_contacts != config_max:
                changes['table.max_contacts'] = args.max_contacts
        
        # Check font preferences (if you add font selection as command line options)
        if hasattr(args, 'font_primary') and args.font_primary:
            config_font = self.config.get('fonts', {}).get('primary', 'arial.ttf')
            if args.font_primary != config_font:
                changes['fonts.primary'] = args.font_primary
        
        if hasattr(args, 'font_bold') and args.font_bold:
            config_font_bold = self.config.get('fonts', {}).get('bold', 'arialbd.ttf')
            if args.font_bold != config_font_bold:
                changes['fonts.bold'] = args.font_bold
        
        # Check card dimensions (if you add these as command line options)
        if hasattr(args, 'card_width') and args.card_width:
            config_width = self.config.get('card', {}).get('width', 1650)
            if args.card_width != config_width:
                changes['card.width'] = args.card_width
        
        if hasattr(args, 'card_height') and args.card_height:
            config_height = self.config.get('card', {}).get('height', 1050)
            if args.card_height != config_height:
                changes['card.height'] = args.card_height
        
        # Check output quality (if you add this as a command line option)
        if hasattr(args, 'quality') and args.quality:
            config_quality = self.config.get('output', {}).get('quality', 95)
            if args.quality != config_quality:
                changes['output.quality'] = args.quality
        
        if changes:
            print(f"\nRuntime parameters differ from config file:")
            for key, value in changes.items():
                current_value = self._get_nested_config_value(key)
                print(f"  {key}: {current_value} → {value}")
            
            while True:
                response = input(f"\nSave these settings to {config_file}? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    self.update_config_file(changes, config_file)
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
        return False

    def _get_nested_config_value(self, key_path):
        """Helper method to get current config value using dot notation"""
        keys = key_path.split('.')
        current = self.config
        try:
            for key in keys:
                current = current[key]
            return current
        except KeyError:
            return None

    def update_config_file(self, changes, config_file):
        """Update config file with new values"""
        try:
            # Load current config or create new one
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Apply changes using dot notation
            for key, value in changes.items():
                keys = key.split('.')
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration updated and saved to {config_file}")
            
        except Exception as e:
            print(f"Error saving config: {e}")

    def check_and_clear_output_dir(self, output_dir):
        """Check if output directory has content and ask user if they want to clear it"""
        if os.path.exists(output_dir) and os.listdir(output_dir):
            print(f"\nOutput directory '{output_dir}' contains files:")
            files = os.listdir(output_dir)
            for i, file in enumerate(files[:10]):  # Show first 10 files
                print(f"  - {file}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
            
            ask_before_delete = self.config.get('output', {}).get('ask_before_delete', True)
            if not ask_before_delete:
                try:
                    shutil.rmtree(output_dir)
                    print(f"Auto-cleared directory: {output_dir}")
                    return True
                except Exception as e:
                    print(f"Error clearing directory: {e}")
                    return False

            while True:
                response = input(f"\nDo you want to delete all content in '{output_dir}'? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    try:
                        shutil.rmtree(output_dir)
                        print(f"Cleared directory: {output_dir}")
                        break
                    except Exception as e:
                        print(f"Error clearing directory: {e}")
                        return False
                elif response in ['n', 'no']:
                    print("Keeping existing files. New cards may overwrite files with same names.")
                    break
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
        return True
    
    def check_for_updates(self, force_check=False):
        """Check GitHub repository for newer version"""
        update_config = self.config.get('update', {})
        
        if not update_config.get('github_repo'):
            print("No GitHub repository configured for updates")
            return False
        
        # Check if we should skip automatic checking
        if not force_check and not update_config.get('check_on_startup', True):
            return False
        
        # Check interval (if not forced)
        if not force_check:
            last_check = update_config.get('last_check_date')
            if last_check:
                from datetime import datetime, timedelta
                try:
                    last_check_date = datetime.fromisoformat(last_check)
                    interval_days = update_config.get('auto_check_interval_days', 7)
                    if datetime.now() - last_check_date < timedelta(days=interval_days):
                        return False
                except ValueError:
                    pass
        
        try:
            print("Checking for updates..." if force_check else "Checking for updates (background)...")
            
            repo = update_config['github_repo']
            api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            
            # Make API request with timeout
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')
            current_version = update_config.get('current_version', __version__)
            
            # Update last check date
            self.update_last_check_date()
            
            if version.parse(latest_version) > version.parse(current_version):
                print(f"\n🎉 New version available!")
                print(f"Current version: {current_version}")
                print(f"Latest version:  {latest_version}")
                print(f"Release name:    {release_data.get('name', 'N/A')}")
                print(f"Published:       {release_data.get('published_at', 'N/A')[:10]}")
                
                if release_data.get('body'):
                    print(f"\nRelease notes:")
                    # Truncate release notes if too long
                    notes = release_data['body'][:500]
                    if len(release_data['body']) > 500:
                        notes += "... (truncated)"
                    print(notes)
                
                if force_check:
                    self.prompt_for_update(release_data)
                else:
                    print(f"\nRun with --check-updates to see update options")
                
                return True
            else:
                if force_check:
                    print(f"You're running the latest version ({current_version})")
                return False
                
        except requests.RequestException as e:
            if force_check:
                print(f"Error checking for updates: {e}")
            return False
        except Exception as e:
            if force_check:
                print(f"Unexpected error checking for updates: {e}")
            return False

    def update_last_check_date(self):
        """Update the last check date in config"""
        from datetime import datetime
        
        # Update in-memory config
        if 'update' not in self.config:
            self.config['update'] = {}
        self.config['update']['last_check_date'] = datetime.now().isoformat()
        
        # Save to file if config file exists
        if hasattr(self, 'config_file') and self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                
                if 'update' not in file_config:
                    file_config['update'] = {}
                file_config['update']['last_check_date'] = self.config['update']['last_check_date']
                
                with open(self.config_file, 'w') as f:
                    json.dump(file_config, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not update last check date: {e}")

    def prompt_for_update(self, release_data):
        """Prompt user for update options"""
        print(f"\nUpdate options:")
        print(f"1. Update script only")
        print(f"2. Update script and config")
        print(f"3. Download manually")
        print(f"4. Skip this version")
        print(f"5. Cancel")
        
        while True:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                self.update_script(release_data, update_config=False)
                break
            elif choice == '2':
                self.update_script(release_data, update_config=True)
                break
            elif choice == '3':
                print(f"\nDownload manually from:")
                print(f"https://github.com/{self.config['update']['github_repo']}/releases/latest")
                break
            elif choice == '4':
                print("Skipping this version...")
                break
            elif choice == '5':
                print("Update cancelled")
                break
            else:
                print("Please enter a number between 1 and 5")

    def update_script(self, release_data, update_config=True):
        """Download and update the script"""
        update_config_obj = self.config.get('update', {})
        
        if not update_config_obj.get('update_script', True):
            print("Script updates are disabled in configuration")
            return False
        
        try:
            # Create backup if configured
            if update_config_obj.get('backup_before_update', True):
                self.create_backup()
            
            # Find the script file in release assets
            script_asset = None
            config_asset = None
            
            for asset in release_data.get('assets', []):
                if asset['name'].endswith('.py'):
                    script_asset = asset
                elif asset['name'].endswith('.json') and 'config' in asset['name'].lower():
                    config_asset = asset
            
            if not script_asset:
                print("No Python script found in release assets")
                return False
            
            print(f"Downloading {script_asset['name']}...")
            
            # Download script
            script_url = script_asset['browser_download_url']
            current_script = __file__
            
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
                with urllib.request.urlopen(script_url) as response:
                    shutil.copyfileobj(response, tmp_file)
                temp_path = tmp_file.name
            
            # Replace current script
            shutil.move(temp_path, current_script)
            os.chmod(current_script, 0o755)
            
            print(f"✅ Script updated successfully!")
            
            # Update config if requested and available
            if update_config and config_asset and update_config_obj.get('update_config', True):
                print(f"Downloading {config_asset['name']}...")
                
                config_url = config_asset['browser_download_url']
                config_file = getattr(self, 'config_file', 'qsl_config.json')
                
                # Create backup of current config
                if os.path.exists(config_file):
                    backup_config = f"{config_file}.backup"
                    shutil.copy2(config_file, backup_config)
                    print(f"Config backup created: {backup_config}")
                
                with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
                    with urllib.request.urlopen(config_url) as response:
                        shutil.copyfileobj(response, tmp_file)
                    temp_config_path = tmp_file.name
                
                shutil.move(temp_config_path, config_file)
                print(f"✅ Configuration updated successfully!")
            
            # Update version in config
            self.update_version_in_config(release_data['tag_name'].lstrip('v'))
            
            print(f"\n🎉 Update completed successfully!")
            print(f"Please restart the script to use the new version.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during update: {e}")
            return False

    def create_backup(self):
        """Create backup of current script and config"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup script
        current_script = __file__
        backup_script = f"{current_script}.{timestamp}.backup"
        shutil.copy2(current_script, backup_script)
        print(f"Script backup created: {backup_script}")
        
        # Backup config if exists
        config_file = getattr(self, 'config_file', 'qsl_config.json')
        if os.path.exists(config_file):
            backup_config = f"{config_file}.{timestamp}.backup"
            shutil.copy2(config_file, backup_config)
            print(f"Config backup created: {backup_config}")

    def update_version_in_config(self, new_version):
        """Update the current version in config file"""
        config_file = getattr(self, 'config_file', 'qsl_config.json')
        
        if not os.path.exists(config_file):
            return
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if 'update' not in config:
                config['update'] = {}
            
            config['update']['current_version'] = new_version
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not update version in config: {e}")

    def __init__(self, csv_file, template_image=None, config_file=None):
        self.csv_file = csv_file
        self.template_image = template_image
        self.contacts = []
        
        # Load configuration FIRST
        self.config = self.load_config(config_file)
        # Check for updates on startup (if enabled)
        if self.config.get('update', {}).get('check_on_startup', True):
            self.check_for_updates(force_check=False)

        # THEN resolve template image (command line takes precedence over config)
        if template_image:
            self.template_image = template_image
        else:
            self.template_image = self.config.get('template', {}).get('default_image')
        
        # Print what template we're using for debugging
        if self.template_image:
            print(f"Using template: {self.template_image}")
            if not os.path.exists(self.template_image):
                print(f"WARNING: Template file not found: {self.template_image}")
        else:
            print("No template specified - using blank cards")

        self.load_fonts()
        self.load_contacts()
    
    def load_config(self, config_file):
        """Load configuration from JSON file or create default"""
        default_config = self.get_default_config()
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for missing keys
                return self.merge_configs(default_config, config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        # Save default config if not exists
        if config_file:
            self.save_config(default_config, config_file)
        
        return default_config
    
    def merge_configs(self, default, user):
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config, config_file):
        """Save configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Default configuration saved to {config_file}")
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def load_fonts(self):
        """Load fonts based on configuration"""
        font_config = self.config['fonts']
        sizes = font_config['sizes']
        
        self.fonts = {}
        for size_name, size in sizes.items():
            try:
                if size_name == 'bold':
                    self.fonts[size_name] = ImageFont.truetype(font_config['bold'], size)
                else:
                    self.fonts[size_name] = ImageFont.truetype(font_config['primary'], size)
            except OSError:
                self.fonts[size_name] = ImageFont.load_default()
        
        if any(isinstance(font, type(ImageFont.load_default())) for font in self.fonts.values()):
            print("Warning: Using default fonts")
    
    def load_contacts(self):
        """Load and validate contacts from CSV"""
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    contact = {k.strip().lower(): v.strip() for k, v in row.items() if v}
                    if contact.get('call'):
                        self.contacts.append(contact)
            print(f"Loaded {len(self.contacts)} contacts")
        except Exception as e:
            print(f"Error loading CSV: {e}")
            sys.exit(1)
    
    def format_data(self, contact):
        """Format contact data for display"""
        def format_date(date_str):
            if not date_str:
                return "?"
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']:
                try:
                    return datetime.strptime(date_str, fmt).strftime('%d-%b-%Y')
                except ValueError:
                    continue
            return date_str[:10]
        
        def format_time(time_str):
            if not time_str:
                return "?"
            clean = time_str.replace(':', '').replace('.', '').strip()
            return f"0{clean}" if len(clean) == 3 else clean[:4] if len(clean) >= 4 else time_str[:4]
        
        def format_freq(freq_str):
            if not freq_str:
                return "?"
            try:
                freq = float(freq_str)
                return f"{freq/1000:.3f}" if freq > 1000 else f"{freq:.3f}"
            except ValueError:
                return freq_str[:8]
        
        def format_mode(mode, submode):
            if not mode:
                return "?"
            mode, submode = mode.strip().upper(), (submode or "").strip().upper()
            
            # Handle special cases from config
            special = self.config['modes']['special_handling']
            if mode in special:
                return special[mode]
            if f"{mode}/{submode}" in special:
                return special[f"{mode}/{submode}"]
            
            # Handle digital modes
            if mode in self.config['modes']['digital_main']:
                return submode if submode else mode
            
            return f"{mode}/{submode}"[:10] if submode and submode != mode else mode[:8]
        
        def get_band(freq_str):
            if not freq_str:
                return ""
            try:
                freq = float(freq_str) / 1000 if float(freq_str) > 1000 else float(freq_str)
                for min_f, max_f, band in self.config['bands']:
                    if min_f <= freq <= max_f:
                        return band
                return f"{freq:.0f}MHz"
            except:
                return ""
        
        return [
            format_date(contact.get('qso_date', '')),
            format_time(contact.get('time_on', '')),
            format_freq(contact.get('freq', '')),
            format_mode(contact.get('mode', ''), contact.get('submode', '')),
            contact.get('rst_sent', '')[:4],
            contact.get('rst_rcvd', '')[:4],
            contact.get('band', '') or get_band(contact.get('freq', '')),
            contact.get('comment_intl', '')[:26]
        ]
    
    def is_digital_mode(self, mode, submode):
        """Check if mode is digital based on configuration"""
        mode = (mode or "").strip().upper()
        submode = (submode or "").strip().upper()
        
        digital_modes = self.config['modes']['digital']
        digital_main = self.config['modes']['digital_main']
        
        return (mode in digital_modes or submode in digital_modes or 
                mode in digital_main)
    
    def create_base_image(self):
        """Create base image from template or blank canvas"""
        width = self.config['card']['width']
        height = self.config['card']['height']
        
        if self.template_image and os.path.exists(self.template_image):
            try:
                template = Image.open(self.template_image)
                template = template.resize((width, height), Image.Resampling.LANCZOS)
                return template.convert('RGB') if template.mode != 'RGB' else template
            except Exception as e:
                print(f"Template error: {e}. Using blank card.")
        
        return Image.new('RGB', (width, height), 'white')
    
    def draw_contact_table(self, draw, contacts):
        """Draw the main contact table"""
        config = self.config
        table_cfg = config['table']
        colors = config['colors']
        
        # Calculate dimensions
        card_width = config['card']['width']
        card_height = config['card']['height']
        
        table_x = table_cfg['x']
        table_y = int(card_height * table_cfg['y_percent'])
        table_width = card_width - table_cfg['width_margin']
        table_height = int(card_height * table_cfg['height_percent'])
        
        # Column setup
        col_widths = [int(table_width * w) for w in config['columns']['widths_percent']]
        headers = config['columns']['headers']
        
        # Row calculations
        max_contacts = min(len(contacts), table_cfg['max_contacts'])
        row_height = max(table_cfg['min_row_height'], 
                        (table_height - table_cfg['header_height'] - 20) // (max_contacts + 1))
        row_height = min(row_height, table_cfg['max_row_height'])
        
        # Draw header
        header_y = table_y
        draw.rectangle([table_x, header_y, table_x + table_width, 
                       header_y + table_cfg['header_height']], 
                      fill=colors['header_bg'], outline='black', width=1)
        
        current_x = table_x
        for i, header in enumerate(headers):
            draw.text((current_x + 5, header_y + 6), header, 
                fill=colors['header_text'], font=self.get_font_for_section('table_header'))
            if i < len(col_widths) - 1:
                sep_x = current_x + col_widths[i]
                draw.line([sep_x, header_y, sep_x, header_y + table_cfg['header_height']], 
                         fill='white', width=1)
            current_x += col_widths[i]
        
        # Draw contact rows
        for row_idx, contact in enumerate(contacts[:max_contacts]):
            row_y = header_y + table_cfg['header_height'] + (row_idx * row_height)
            
            # Row background
            bg_color = 'white' if row_idx % 2 == 0 else colors['row_bg_alt']
            draw.rectangle([table_x, row_y, table_x + table_width, row_y + row_height], 
                          fill=bg_color, outline='black', width=1)
            
            # Contact data
            contact_data = self.format_data(contact)
            current_x = table_x
            
            for i, data in enumerate(contact_data):
                if i < len(col_widths):
                    text_color = 'black'
                    if i == 3 and self.is_digital_mode(contact.get('mode'), contact.get('submode')):
                        text_color = colors['digital_mode']
                    
                    max_chars = max(1, col_widths[i] // 8)
                    display_text = str(data)[:max_chars] if data else ''
                    
                    draw.text((current_x + 5, row_y + 6), display_text, 
                        fill=text_color, font=self.get_font_for_section('table_data'))
                    
                    if i < len(col_widths) - 1:
                        sep_x = current_x + col_widths[i]
                        draw.line([sep_x, row_y, sep_x, row_y + row_height], 
                                 fill='gray', width=1)
                    current_x += col_widths[i]
        
        return header_y + table_cfg['header_height'] + (max_contacts * row_height) + 10
    
    def draw_additional_info_section(self, draw, contacts):
        """Draw additional information section (POTA references and comments) with lines"""
        config = self.config
        additional_cfg = config['additional_info']
        
        # Check if we have any additional info or should show default message
        has_additional_info = any(c.get('pota_ref') or c.get('comment_intl') for c in contacts)
        show_default_message = additional_cfg.get('show_default_message', False)
        
        if not has_additional_info and not show_default_message:
            return
        
        colors = config['colors']
        
        # Calculate section dimensions
        card_width = config['card']['width']
        card_height = config['card']['height']
        table_y = int(card_height * config['table']['y_percent'])
        table_height = int(card_height * config['table']['height_percent'])
        section_x = additional_cfg['x']
        section_y = table_y + table_height + additional_cfg['y_offset'] - 25
        section_width = card_width - additional_cfg['width_margin']
        section_height = int(card_height * additional_cfg['height_percent'])
        table_header_height = additional_cfg['header_height']

        # Draw section
        draw.rectangle([section_x, section_y, section_x + section_width,
                    section_y + section_height],
                    fill=colors['section_bg'], outline='black', width=1)
        
        # Header with background - USE CONFIGURABLE FONT
        header_height = table_header_height
        draw.rectangle([section_x, section_y, section_x + section_width,
                    section_y + header_height],
                    fill=colors['header_bg'], outline='black', width=1)
        
        # Get header font from config
        header_font_size = additional_cfg.get('fonts', {}).get('header', 'bold')
        header_font = self.fonts.get(header_font_size, self.fonts['bold'])
        
        draw.text((section_x + 10, section_y + 5), "Additional Information",
                fill=colors['header_text'], font=header_font)
        
        # Calculate available space and row dimensions
        available_height = section_height - header_height - 20
        max_contacts = self.config['table']['max_contacts']
        
        # Filter contacts that have additional info
        contacts_with_info = [c for c in contacts[:max_contacts] 
                            if c.get('pota_ref') or c.get('comment_intl')]
        
        # If no contacts have additional info but we want to show default message
        if not contacts_with_info and show_default_message:
            import random
            
            # Get random message from config
            default_messages = additional_cfg.get('default_messages', ['Thanks for the contact(s)!'])
            if isinstance(default_messages, list) and len(default_messages) > 0:
                default_message = random.choice(default_messages)
            else:
                default_message = additional_cfg.get('default_message', 'Thanks for the contact(s)!')
            
            # Calculate vertical center position for default message
            content_y = section_y + header_height + 10
            content_height = section_height - header_height - 20
            message_y = content_y + (content_height // 2) - 10
            
            # GET DEFAULT MESSAGE FONT FROM CONFIG
            default_msg_font_size = additional_cfg.get('fonts', {}).get('default_message', 'large')
            default_msg_font = self.fonts.get(default_msg_font_size, self.fonts['large'])
            
            # Draw default message centered
            try:
                message_bbox = draw.textbbox((0, 0), default_message, font=default_msg_font)
                message_width = message_bbox[2] - message_bbox[0]
                message_x = section_x + (section_width - message_width) // 2
            except:
                message_x = section_x + (section_width - len(default_message) * 7) // 2
            
            message_color = colors.get('default_message', colors.get('comment', 'black'))
            
            draw.text((message_x, message_y), default_message,
                    fill=message_color, font=default_msg_font)
            return
        
        if not contacts_with_info:
            return
        
        # Calculate dynamic row height based on available space
        base_row_height = additional_cfg.get('base_row_height', 22)
        row_spacing = additional_cfg.get('row_spacing', 5)
        total_row_height = base_row_height + row_spacing
        info_row_height = max(total_row_height, min(35, available_height // len(contacts_with_info)))
        
        # Define column positions and widths from config
        col_positions = {
            'date_band': section_x + additional_cfg['columns']['date_band_offset'],
            'comment': section_x + additional_cfg['columns']['comment_offset'],
            'pota': section_x + additional_cfg['columns']['pota_offset']
        }
        
        # Calculate maximum comment width
        comment_max_width = additional_cfg.get('comment_max_width', None)
        if comment_max_width:
            max_comment_width = comment_max_width
        else:
            estimated_pota_width = 80
            max_comment_width = section_width - (col_positions['comment'] - section_x) - estimated_pota_width - 30
        
        # GET FONTS FROM CONFIG
        date_band_font_size = additional_cfg.get('fonts', {}).get('date_band', 'medium')
        comment_font_size = additional_cfg.get('fonts', {}).get('comment', 'medium')
        pota_font_size = additional_cfg.get('fonts', {}).get('pota', 'medium')
        
        date_band_font = self.fonts.get(date_band_font_size, self.fonts['medium'])
        comment_font = self.fonts.get(comment_font_size, self.fonts['medium'])
        pota_font = self.fonts.get(pota_font_size, self.fonts['medium'])
        
        # Get line configuration options
        show_row_lines = additional_cfg.get('show_row_lines', True)
        show_column_lines = additional_cfg.get('show_column_lines', False)
        line_color = colors.get('grid_lines', 'lightgray')
        line_width = additional_cfg.get('line_width', 1)
        
        # Draw column separator lines if enabled
        if show_column_lines:
            # Vertical line between date/band and comment columns
            comment_line_x = col_positions['comment'] - 10
            draw.line([comment_line_x, section_y + header_height, 
                    comment_line_x, section_y + section_height - 5],
                    fill=line_color, width=line_width)
            
            # Vertical line between comment and POTA columns (only if POTA column is used)
            if any(c.get('pota_ref') for c in contacts_with_info):
                pota_line_x = col_positions['pota'] - 10  
                draw.line([pota_line_x, section_y + header_height,
                        pota_line_x, section_y + section_height - 5],
                        fill=line_color, width=line_width)
        
        for row_idx, contact in enumerate(contacts_with_info):
            # Check if we have enough vertical space
            info_y = section_y + header_height + 10 + (row_idx * info_row_height)
            if info_y + info_row_height > section_y + section_height - 5:
                break
            
            # Draw horizontal row separator line if enabled (after each row except the last)
            if show_row_lines and row_idx < len(contacts_with_info) - 1:
                line_spacing = additional_cfg.get('row_line_spacing', 5)
                line_y = info_y + info_row_height - line_spacing
                draw.line([section_x + 5, line_y, section_x + section_width - 5, line_y],
                        fill=line_color, width=line_width)
            
            callsign = contact.get('call', '').upper()
            pota_ref = contact.get('pota_ref', '').strip().upper()
            comment = contact.get('comment_intl', '')
            
            # Date and Band - USE CONFIGURABLE FONT
            contact_data = self.format_data(contact)
            date_band = f"{contact_data[0]} {contact_data[6]}"
            
            # Measure text width to ensure it fits
            try:
                date_band_bbox = draw.textbbox((0, 0), date_band, font=date_band_font)
                date_band_width = date_band_bbox[2] - date_band_bbox[0]
            except:
                date_band_width = len(date_band) * 7
            
            # Truncate date/band if too long
            if date_band_width > (col_positions['comment'] - col_positions['date_band'] - 10):
                while date_band_width > (col_positions['comment'] - col_positions['date_band'] - 20) and len(date_band) > 5:
                    date_band = date_band[:-4] + "..."
                    try:
                        date_band_bbox = draw.textbbox((0, 0), date_band, font=date_band_font)
                        date_band_width = date_band_bbox[2] - date_band_bbox[0]
                    except:
                        date_band_width = len(date_band) * 7
            
            draw.text((col_positions['date_band'], info_y), date_band,
                    fill='black', font=date_band_font)
            
            # Comment - USE CONFIGURABLE FONT
            comment_end_x = col_positions['comment']
            if comment:
                # Calculate maximum characters that fit in available space
                try:
                    sample_bbox = draw.textbbox((0, 0), "M", font=comment_font)
                    char_width = sample_bbox[2] - sample_bbox[0]
                except:
                    char_width = 8
                
                max_chars = max(10, max_comment_width // char_width)
                comment_text = comment[:max_chars-3] + "..." if len(comment) > max_chars else comment
                
                text_color = colors['digital_mode'] if self.is_digital_mode(
                    contact.get('mode'), contact.get('submode')) else colors['comment']
                
                draw.text((col_positions['comment'], info_y), comment_text,
                        fill=text_color, font=comment_font)
                        
                # Calculate actual end position of comment text
                try:
                    comment_bbox = draw.textbbox((0, 0), comment_text, font=comment_font)
                    comment_width = comment_bbox[2] - comment_bbox[0]
                    comment_end_x = col_positions['comment'] + comment_width + 15
                except:
                    comment_end_x = col_positions['comment'] + len(comment_text) * char_width + 15
            
            # POTA Reference - USE CONFIGURABLE FONT
            if pota_ref:
                pota_text = f"POTA: {pota_ref}"
                
                # Use dynamic positioning if comment exists, otherwise use configured position
                if comment:
                    pota_x = max(comment_end_x, col_positions['pota'])
                else:
                    pota_x = col_positions['pota']
                
                # Measure POTA text width
                try:
                    pota_bbox = draw.textbbox((0, 0), pota_text, font=pota_font)
                    pota_width = pota_bbox[2] - pota_bbox[0]
                except:
                    pota_width = len(pota_text) * 7
                
                # Calculate available space for POTA
                max_pota_width = section_width - (pota_x - section_x) - 20
                
                # Truncate POTA if too long
                if pota_width > max_pota_width:
                    while pota_width > max_pota_width - 20 and len(pota_text) > 8:
                        pota_text = pota_text[:-4] + "..."
                        try:
                            pota_bbox = draw.textbbox((0, 0), pota_text, font=pota_font)
                            pota_width = pota_bbox[2] - pota_bbox[0]
                        except:
                            pota_width = len(pota_text) * 7
                
                draw.text((pota_x, info_y), pota_text,
                        fill=colors['pota_ref'], font=pota_font)

    
    def create_qsl_card(self, callsign, contacts, card_number=1, total_cards=1, total_contacts_for_callsign=None):
        """Create a single QSL card"""
        contacts_for_card = contacts[:self.config['table']['max_contacts']]
        
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Add confirmation text if space available
        table_y = int(self.config['card']['height'] * self.config['table']['y_percent'])
        if table_y > 100:
            # Get positioning from config
            pos_config = self.config.get('confirmation_text', {}).get('position', {})
            x_offset = pos_config.get('x_offset', 10)
            y_offset = pos_config.get('y_offset', -40)
            min_y = pos_config.get('min_y', 50)
            
            confirm_y = max(min_y, table_y + y_offset)
            text_x = self.config['table']['x'] + x_offset
            
            # Create confirmation text
            contact_count = len(contacts_for_card)
            total_qsos = total_contacts_for_callsign or contact_count
            confirm_text = f"QSL - Confirming {total_qsos} QSO{'s' if total_qsos > 1 else ''} with {callsign.upper()}"
            if total_cards > 1:
                confirm_text += f" (Card {card_number} of {total_cards})"
            
            # Text background
            bbox = draw.textbbox((0, 0), confirm_text, font=self.get_font_for_section('confirmation_text'))
            text_width = bbox[2] - bbox[0]
            
            # Get text color from config
            text_color = self.config.get('confirmation_text', {}).get('text_color', 'black')
            
            if self.config.get('confirmation_text', {}).get('show_border', False):
                draw.rectangle([text_x - 10, confirm_y - 5, text_x + text_width + 10,
                            confirm_y + bbox[3] - bbox[1] + 5],
                            fill='white', outline='black', width=1)
            draw.text((text_x, confirm_y), confirm_text, fill=text_color, font=self.get_font_for_section('confirmation_text'))
        
        self.draw_contact_table(draw, contacts_for_card)
        self.draw_additional_info_section(draw, contacts_for_card)
        
        return img
    
    def generate_cards(self, output_dir, batch_by_call=False):
        """Generate QSL cards"""
        if not self.check_and_clear_output_dir(output_dir):
            return 0
        os.makedirs(output_dir, exist_ok=True)
        cards_generated = 0
        max_contacts = self.config['table']['max_contacts']
        
        # Group contacts by callsign
        grouped = defaultdict(list)
        for contact in self.contacts:
            callsign = contact.get('call', '').upper()
            grouped[callsign].append(contact)
        
        print(f"Processing {len(grouped)} unique callsigns with {len(self.contacts)} total contacts")
        print(f"Max contacts per card: {max_contacts}")
        
        for callsign, contacts in grouped.items():
            print(f"Processing {callsign} with {len(contacts)} contacts")
            
            # Split contacts into groups (max_contacts per card)
            contact_groups = []
            for i in range(0, len(contacts), max_contacts):
                contact_groups.append(contacts[i:i+max_contacts])
            
            total_cards_for_callsign = len(contact_groups)
            print(f"  Will create {total_cards_for_callsign} cards for {callsign}")
            
            # Create cards for this callsign
            for card_num, contact_group in enumerate(contact_groups, 1):
                print(f"  Creating card {card_num} of {total_cards_for_callsign} for {callsign} ({len(contact_group)} contacts)")
                
                card = self.create_qsl_card(callsign, contact_group, card_num, total_cards_for_callsign, len(contacts))
                
                # Determine filename based on mode
                if batch_by_call:
                    # Batch mode naming
                    if total_cards_for_callsign == 1:
                        filename = f"{callsign}.png"
                    else:
                        filename = f"{callsign}_card_{card_num}_of_{total_cards_for_callsign}.png"
                else:
                    # Individual mode naming
                    if total_cards_for_callsign == 1:
                        filename = f"{callsign}.png"
                    else:
                        filename = f"{callsign}_{card_num}_of_{total_cards_for_callsign}.png"
                
                filepath = os.path.join(output_dir, filename)
                card.save(filepath, 'PNG', quality=self.config['output']['quality'])
                cards_generated += 1
                print(f"  Saved: {filename}")
        
        return cards_generated

def main():
    parser = argparse.ArgumentParser(description='Generate QSL cards from ham radio contact CSV')
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file containing contacts')
    parser.add_argument('template_image', nargs='?', help='Path to template image (optional)')
    parser.add_argument('-c', '--config', default='qsl_config.json', 
                       help='Configuration file (default: qsl_config.json)')
    parser.add_argument('-d', '--output-dir', 
                       help='Output directory (default: from config file)')
    parser.add_argument('-b', '--batch-by-call', action='store_true', 
                       help='Batch contacts by callsign')
    parser.add_argument('--sample', action='store_true', 
                       help='Show first 3 contacts and exit')
    parser.add_argument('-v', '--version', action='version', 
                       version=f'QSL Card Generator {__version__} by {__author__}')
    parser.add_argument('--info', action='store_true', 
                       help='Show author and version information')
    parser.add_argument('--update-config', action='store_true',
                       help='Update existing config file with missing default values')
    parser.add_argument('--create-default-config', action='store_true',
                       help='Create a new default configuration file')
    parser.add_argument('--reset-config', action='store_true',
                       help='Backup current config and create new default configuration')
    parser.add_argument('--max-contacts', type=int, 
                       help='Maximum contacts per card (default: from config)')
    parser.add_argument('--font-primary', 
                       help='Primary font file path (default: from config)')
    parser.add_argument('--font-bold', 
                       help='Bold font file path (default: from config)')
    parser.add_argument('--card-width', type=int, 
                       help='Card width in pixels (default: from config)')
    parser.add_argument('--card-height', type=int, 
                       help='Card height in pixels (default: from config)')
    parser.add_argument('--quality', type=int, choices=range(1, 101), metavar='[1-100]',
                       help='Output image quality 1-100 (default: from config)')
    parser.add_argument('--auto-delete', action='store_true', 
                       help='Automatically delete output directory contents without asking')
    parser.add_argument('--check-updates', action='store_true',
                   help='Check for updates from GitHub repository')
    parser.add_argument('--update-script', action='store_true',
                    help='Update script from GitHub (interactive)')
    parser.add_argument('--disable-update-check', action='store_true',
                    help='Disable automatic update checking for this run')
    
    args = parser.parse_args()
    
    if args.info:
        print(f"QSL Card Generator {__version__}")
        print(f"Author: {__author__}")
        print(f"Email: {__email__}")
        print(f"License: {__license__}")
        return
    
    # Handle configuration management operations
    if args.update_config or args.create_default_config or args.reset_config:
        # Create a minimal generator instance just for config operations
        generator = QSLCardGenerator.__new__(QSLCardGenerator)
        generator.config = {}  # Initialize empty config
        
        if args.update_config:
            generator.update_config_with_defaults(args.config)
            return
        
        if args.create_default_config:
            generator.create_default_config_file(args.config)
            return
            
        if args.reset_config:
            generator.reset_config_with_backup(args.config)
            return
    
    # Require CSV file for normal operations
    if not args.csv_file:
        parser.error("CSV file is required for QSL card generation")
    
    generator = QSLCardGenerator(args.csv_file, args.template_image, args.config)
    
    # Rest of the existing main() function logic continues unchanged...
    # Use config defaults if no command line args specified
    if not args.output_dir:
        args.output_dir = generator.config.get('output', {}).get('default_directory', 'qsl_cards')
    
    if not args.template_image:
        args.template_image = generator.config.get('template', {}).get('default_image')
    
    if not args.batch_by_call:
        args.batch_by_call = generator.config.get('generation', {}).get('batch_by_call', False)
    
    if args.sample:
        print("Sample contacts:")
        for i, contact in enumerate(generator.contacts[:3]):
            print(f"Contact {i+1}: {contact}")
        return

    # Check if runtime args differ from config and offer to save
    generator.check_and_save_runtime_config(args, args.config)
    
    print(f"Generating cards with template: {args.template_image or 'None'}")
    
    # At the end of main(), before calling generate_cards:
    print(f"Total contacts: {len(generator.contacts)}")
    grouped = defaultdict(list)
    for contact in generator.contacts:
        callsign = contact.get('call', '').upper()
        grouped[callsign].append(contact)

    print(f"Unique callsigns: {len(grouped)}")
    for callsign, contacts in grouped.items():
        print(f"  {callsign}: {len(contacts)} contacts")

    cards_generated = generator.generate_cards(args.output_dir, args.batch_by_call)
    mode = "batched" if args.batch_by_call else "individual"
    print(f"Generated {cards_generated} {mode} QSL cards in {args.output_dir}")


if __name__ == "__main__":
    main()