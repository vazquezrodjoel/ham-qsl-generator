# Changelog

All notable changes to the Ham Radio QSL Card Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-06-09

### Added
- **Configurable option for updates**: Option to verify available updates from Github.

### Changed:
- **Documentation**: Updated configuration examples 

## [1.3.0] - 2025-05-30

### Added
- **Configurable fonts per section**: Individual font configuration for different card sections
  - Table headers, table data, additional info sections can now use different fonts
  - Font configuration through `fonts.section_sizes` in JSON config
  - Support for section-specific font sizes (confirmation_text, table_header, table_data, etc.)
- **Enhanced font system**: Improved font loading and management
  - Better error handling for missing fonts
  - Fallback to default fonts when system fonts unavailable
  - Font configuration validation

### Changed
- **Font configuration structure**: Enhanced font configuration with section-specific settings
- **Code organization**: Improved font handling methods and configuration management
- **Documentation**: Updated configuration examples and font setup instructions

### Fixed
- Font loading errors when system fonts are not available
- Inconsistent font sizing across different card sections
- Configuration merge issues with font settings

## [1.2.0] - 2025-05-29

### Added
- **Configurable contact limits**: Maximum contacts per card now configurable via `table.max_contacts`
- **Enhanced Additional Info section**: 
  - Improved layout and spacing for POTA references and comments
  - Dynamic row height calculation based on available space
  - Better text wrapping and truncation
  - Configurable column positions and widths
- **Default message system**: Random selection from configurable default messages when no additional info
- **Advanced configuration options**:
  - Configurable fonts for different sections within Additional Info
  - Line spacing and grid line options
  - Column positioning controls

### Changed
- **Additional Info rendering**: Complete rewrite for better layout and readability
- **Configuration structure**: Extended configuration options for Additional Info section
- **Text formatting**: Improved text truncation and width calculations

### Fixed
- Text overflow issues in Additional Info section
- Inconsistent spacing between POTA references and comments
- Layout issues when mixing comments and POTA references

## [1.1.0] - 2025-05-28

### Added
- **Confirmation text border control**: Optional border around QSL confirmation text
  - Configurable via `confirmation_text.show_border`
  - Customizable text color and positioning
- **Output directory management**: 
  - Automatic output directory creation
  - User prompts for clearing existing content
  - Configurable auto-delete behavior
- **Runtime configuration checking**: 
  - Compare command-line arguments with config file settings
  - Option to save runtime settings to configuration
- **Enhanced configuration management**:
  - `--update-config`: Update existing config with missing defaults
  - `--create-default-config`: Create new default configuration
  - `--reset-config`: Backup and reset configuration
  - Configuration backup system with timestamps

### Changed
- **Configuration file handling**: Improved merge logic for user and default configurations
- **Command-line interface**: Added configuration management options
- **Output handling**: Better control over output directory behavior

### Fixed
- Configuration merge issues with nested dictionaries
- Output directory collision handling
- Missing configuration keys causing errors

## [1.0.0] - 2025-05-27

### Added
- **Initial release** of Ham Radio QSL Card Generator
- **CSV import functionality**: Support for standard ADIF CSV format
- **Template support**: Use custom QSL card template images
- **Multi-contact cards**: Display multiple contacts per card (default: 5)
- **Callsign batching**: Group contacts by callsign on individual cards
- **Digital mode highlighting**: Automatic color coding for digital modes
- **POTA integration**: Display Parks on the Air references
- **Band detection**: Automatic band calculation from frequency
- **Mode handling**: Support for voice, digital, and special modes
- **Professional layout**: 
  - Formatted contact table with headers
  - RST reports and signal strength
  - Date and time formatting
  - Frequency display in MHz
- **JSON configuration**: Comprehensive configuration system
- **Font support**: Configurable fonts and sizes
- **Color customization**: Customizable color scheme
- **Output control**: PNG output with quality settings

### Configuration Features
- Card dimensions and layout
- Table positioning and sizing
- Font paths and sizes  
- Color scheme customization
- Mode definitions and handling
- Band frequency ranges
- Column widths and headers

### Supported Input Formats
- **Dates**: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, YYYYMMDD
- **Times**: HHMM, HH:MM formats
- **Frequencies**: MHz or Hz values
- **Modes**: SSB, CW, FT8, PSK31, RTTY, and many more

### Command Line Options
- Template image specification
- Output directory control
- Configuration file selection
- Batch processing mode
- Sample data preview
- Version information

---

## Development Notes

### Version Numbering
- **Major** (X.y.z): Breaking changes or major feature additions
- **Minor** (x.Y.z): New features, significant improvements
- **Patch** (x.y.Z): Bug fixes, minor improvements

### Upcoming Features (Roadmap)
- Option to update from the github repo.
- Additional output formats (PDF, multi-page layouts)
- QR code generation for electronic QSL
- Batch processing improvements
- Template gallery and sharing

### Known Issues
- Font rendering may vary across different operating systems
- Large template images may require significant memory
- CSV files with non-standard encodings may need preprocessing

### Contributing
Please see README.md for contribution guidelines and development setup instructions.