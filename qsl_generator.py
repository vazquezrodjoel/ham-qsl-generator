#!/usr/bin/env python3
"""
Ham Radio QSL Card Generator with Configuration Support
Version: 1.2.0
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

Changelog:
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

__version__ = "1.2.0"
__author__ = "Author: Joel Vazquez, WE0DX"
__email__ = "joelvazquez@we0dx.us"
__license__ = "MIT"

class QSLCardGenerator:
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

    def __init__(self, csv_file, template_image=None, config_file=None):
        self.csv_file = csv_file
        self.template_image = template_image
        self.contacts = []
        
        # Load configuration FIRST
        self.config = self.load_config(config_file)
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
        default_config = {
            "output": {
                "default_directory": "qsl_cards",
                "ask_before_delete": False,
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
                "height_percent": 0.30,
                "max_contacts": 5,
                "header_height": 30,
                "min_row_height": 25,
                "max_row_height": 40
            },
            "additional_info": {
                "x": 50,
                "y_offset": 10,
                "width_margin": 100,
                "height_percent": 0.20
            },
            "confirmation_text": {
                "show_border": False,
                "text_color": "black"
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
                  "bold": 20
                }
              },
            "colors": {
                "header_bg": "#4a4a4a",
                "header_text": "white",
                "row_bg_alt": "#f0f0f0",
                "digital_mode": "#cc6600",
                "pota_ref": "#0066cc",
                "comment": "#006600",
                "section_bg": "#f8f8f8"
            },
            "columns": {
                "widths_percent": [0.14, 0.09, 0.11, 0.12, 0.07, 0.07, 0.09, 0.31],
                "headers": ["Date", "Time UTC", "Freq(MHz)", "Mode/Sub", "RST S", "RST R", "Band", "Notes"]
            },
            "modes": {
                "digital": ["FT8", "FT4", "PSK31", "PSK63", "RTTY", "JT4", "JT9", "JT65", 
                           "MSK144", "Q65", "FSK441", "WSPR", "JS8", "VARA"],
                "digital_main": ["MFSK", "PSK", "RTTY", "DATA", "DIGITAL"],
                "special_handling": {
                    "FT8": "FT8",
                    "MFSK/FT4": "FT4"
                }
            },
            "bands": [
                [1.8, 2.0, "160m"], [3.5, 4.0, "80m"], [7.0, 7.3, "40m"],
                [14.0, 14.35, "20m"], [21.0, 21.45, "15m"], [28.0, 29.7, "10m"],
                [50.0, 54.0, "6m"], [144.0, 148.0, "2m"], [420.0, 450.0, "70cm"]
            ]
        }
        
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
                     fill=colors['header_text'], font=self.fonts['small'])
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
                             fill=text_color, font=self.fonts['small'])
                    
                    if i < len(col_widths) - 1:
                        sep_x = current_x + col_widths[i]
                        draw.line([sep_x, row_y, sep_x, row_y + row_height], 
                                 fill='gray', width=1)
                    current_x += col_widths[i]
        
        return header_y + table_cfg['header_height'] + (max_contacts * row_height) + 10
    
    def draw_additional_info_section(self, draw, contacts):
        """Draw additional information section (POTA references and comments)"""
        if not any(c.get('pota_ref') or c.get('comment_intl') for c in contacts):
            return
        
        config = self.config
        additional_cfg = config['additional_info']
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
        
        # Draw section
        draw.rectangle([section_x, section_y, section_x + section_width, 
                       section_y + section_height], 
                      fill=colors['section_bg'], outline='black', width=1)
        
        # Header with background
        header_height = 30
        draw.rectangle([section_x, section_y, section_x + section_width, 
                       section_y + header_height], 
                      fill=colors['header_bg'], outline='black', width=1)
        draw.text((section_x + 10, section_y + 5), "Additional Information", 
                 fill=colors['header_text'], font=self.fonts['bold'])
        
        # Contact info (fixed row height, no vertical centering)
        max_contacts = self.config['table']['max_contacts']
        info_row_height = 20  # Fixed height per row

        
        max_contacts = self.config['table']['max_contacts']
        for row_idx, contact in enumerate(contacts[:max_contacts]):
            callsign = contact.get('call', '').upper()
            pota_ref = contact.get('pota_ref', '').strip().upper()
            comment = contact.get('comment_intl', '')
            
            if not pota_ref and not comment:
                continue
            
            info_y = section_y + header_height + 10 + (row_idx * info_row_height)  # Changed this line
            current_x = section_x + 10
            
            # Date and Band
            contact_data = self.format_data(contact)
            date_band = f"{contact_data[0]} on {contact_data[6]}:"  # Date and Band from formatted data
            draw.text((current_x, info_y), date_band, 
                    fill='black', font=self.fonts['small'])
            current_x += 140  # Increased spacing for longer text
            
            # POTA
            if pota_ref:
                draw.text((current_x, info_y), f"POTA: {pota_ref}", 
                         fill=colors['pota_ref'], font=self.fonts['small'])
                current_x += 105
            
            # Comment
            if comment:
                max_chars = max(20, (section_width - (current_x - section_x) - 20) // 6)
                comment_text = comment[:max_chars-3] + "..." if len(comment) > max_chars else comment
                text_color = colors['digital_mode'] if self.is_digital_mode(
                    contact.get('mode'), contact.get('submode')) else colors['comment']
                
                draw.text((current_x, info_y), comment_text, 
                         fill=text_color, font=self.fonts['tiny'])
    
    def create_qsl_card(self, callsign, contacts, card_number=1, total_cards=1, total_contacts_for_callsign=None):
        """Create a single QSL card"""
        contacts_for_card = contacts[:self.config['table']['max_contacts']]
        
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Add confirmation text if space available
        table_y = int(self.config['card']['height'] * self.config['table']['y_percent'])
        if table_y > 100:
            confirm_y = max(50, table_y - 35)
            contact_count = len(contacts_for_card)
            total_qsos = total_contacts_for_callsign or contact_count
            confirm_text = f"QSL - Confirming {total_qsos} QSO{'s' if total_qsos > 1 else ''} with {callsign.upper()}"
            if total_cards > 1:
                confirm_text += f" (Card {card_number} of {total_cards})"
            
            # Debug: Print font info
            #print(f"DEBUG: Using font for confirmation text: {self.fonts['large']}")
            #print(f"DEBUG: Font size configured: {self.config['fonts']['sizes']['large']}")
            #print(f"DEBUG: Available fonts: {list(self.fonts.keys())}")
            #print(f"DEBUG: All configured font sizes: {self.config['fonts']['sizes']}")
            
            # Use xlarge font if available, otherwise large, or create a temporary large font
            #confirmation_font = self.fonts['bold']
            #print(f"DEBUG: Actually using font: {confirmation_font}")

            # Text background
            bbox = draw.textbbox((0, 0), confirm_text, font=self.fonts['large'])
            text_width = bbox[2] - bbox[0]
            text_x = (self.config['table']['x'] + 10)
            
            # Get text color from config
            text_color = self.config.get('confirmation_text', {}).get('text_color', 'black')

            if self.config.get('confirmation_text', {}).get('show_border', False):
                draw.rectangle([text_x - 10, confirm_y - 5, text_x + text_width + 10, 
                                confirm_y + bbox[3] - bbox[1] + 5], 
                                fill='white', outline='black', width=1)
            draw.text((text_x, confirm_y), confirm_text, fill=text_color, font=self.fonts['bold'])
        
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
    parser.add_argument('csv_file', help='Path to CSV file containing contacts')
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
    
    # Additional configuration options
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
    
    args = parser.parse_args()
    
    if args.info:
        print(f"QSL Card Generator {__version__}")
        print(f"Author: {__author__}")
        print(f"Email: {__email__}")
        print(f"License: {__license__}")
        return
    
    generator = QSLCardGenerator(args.csv_file, args.template_image, args.config)
    
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