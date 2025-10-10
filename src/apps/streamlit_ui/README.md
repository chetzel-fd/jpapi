# JPAPI Manager - Streamlit UI

A modern, SOLID-compliant Streamlit dashboard for managing JAMF Pro API data exports and objects.

## Overview

JPAPI Manager is a professional-grade Streamlit application that provides an intuitive interface for managing JAMF Pro API data. Built following SOLID principles, it offers a clean, maintainable architecture that's easy to extend and modify.

## Features

### 🎯 Core Functionality
- **Environment Management**: Switch between Sandbox and Production environments
- **Object Type Support**: Advanced Searches, Policies, Profiles, Scripts
- **Live Data Loading**: Load data from CSV exports with intelligent caching
- **Smart Filtering**: Filter by status, smart groups, and other criteria
- **Bulk Operations**: Select, export, and manage multiple objects

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with responsive layout
- **Interactive Cards**: Object cards with status badges and selection
- **Action Menus**: Contextual actions for data management
- **Settings Panel**: Comprehensive configuration options
- **Real-time Updates**: Live data refresh and status updates

### 🔧 Technical Features
- **SOLID Architecture**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Dependency Injection**: Clean separation of concerns
- **Caching System**: Intelligent data caching with session state
- **Error Handling**: Comprehensive error handling and user feedback
- **Extensible Design**: Easy to add new object types and features

## Architecture

### Directory Structure

```
src/apps/streamlit_ui/
├── app.py                    # Main entry point
├── README.md                 # This file
│
├── core/                     # Core application logic (SOLID)
│   ├── data/                 # Data Layer (SRP)
│   │   ├── interfaces.py     # DataLoader interface (DIP)
│   │   ├── csv_loader.py     # CSV implementation
│   │   ├── cache_manager.py  # Caching logic (SRP)
│   │   └── validators.py     # Data validation (SRP)
│   │
│   ├── services/             # Business Logic Layer (SRP)
│   │   ├── environment_service.py    # Environment management
│   │   ├── object_type_service.py    # Object type logic
│   │   ├── export_service.py         # Export functionality
│   │   └── jpapi_integration.py      # JPAPI CLI integration
│   │
│   └── config/               # Configuration (DIP)
│       ├── settings.py       # App settings
│       ├── paths.py          # Path configuration
│       └── constants.py      # Constants
│
├── ui/                       # UI Layer (SRP)
│   ├── components/           # Reusable UI components
│   │   ├── base.py          # Base component class
│   │   ├── header.py        # Header component
│   │   ├── controls.py      # Control components
│   │   ├── object_card.py   # Object card component
│   │   ├── action_menu.py   # Actions menu component
│   │   └── settings_panel.py # Settings panel component
│   │
│   ├── pages/               # Page-level components
│   │   └── dashboard.py     # Main dashboard page
│   │
│   └── styles/              # Styling
│       └── theme.py         # Theme configuration
│
├── utils/                   # Utilities
│   ├── session_manager.py   # Session state management
│   ├── formatters.py        # Data formatters
│   └── helpers.py           # Helper functions
│
└── legacy/                  # Legacy files (to be removed)
    ├── clean.py
    ├── clean_simple.py
    └── main.py
```

### SOLID Principles Implementation

#### Single Responsibility Principle (SRP)
- Each class has one reason to change
- `CSVLoader` only handles CSV data loading
- `CacheManager` only manages caching
- `EnvironmentService` only manages environments

#### Open/Closed Principle (OCP)
- Components are open for extension, closed for modification
- New object types can be added without changing existing code
- New export formats can be added by implementing interfaces

#### Liskov Substitution Principle (LSP)
- All components can be substituted with their base classes
- Interface implementations are interchangeable
- Derived classes don't break base class contracts

#### Interface Segregation Principle (ISP)
- Small, focused interfaces
- `DataLoaderInterface` only has data loading methods
- `CacheInterface` only has caching methods
- Clients don't depend on unused methods

#### Dependency Inversion Principle (DIP)
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)
- Dependency injection throughout the application

## Usage

### Running the Application

```bash
# Navigate to the streamlit_ui directory
cd src/apps/streamlit_ui

# Run the application
streamlit run app.py
```

### Configuration

The application uses configuration classes for settings:

- **Settings**: Application-wide settings and constants
- **Paths**: Path management and directory configuration
- **Constants**: Application constants and default values

### Adding New Object Types

1. Add configuration to `Settings.OBJECT_TYPES`
2. Implement file patterns for the new type
3. Add JPAPI command mapping
4. The UI will automatically support the new type

### Adding New Export Formats

1. Implement the export logic in `ExportService`
2. Add format configuration
3. Update the UI to support the new format

## Development

### Adding New Components

1. Inherit from `BaseComponent`
2. Implement the `render()` method
3. Add component-specific state management
4. Integrate with the dashboard

### Adding New Services

1. Create service class with single responsibility
2. Add to dependency injection in `Dashboard`
3. Use interfaces for testability
4. Follow SOLID principles

### Testing

The architecture supports comprehensive testing:

- **Unit Tests**: Test individual components and services
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows

## Dependencies

### Core Dependencies
- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `pathlib`: Path management

### Optional Dependencies
- `psutil`: System and process utilities
- `openpyxl`: Excel file support

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Data Loading Issues**: Check CSV file paths and formats
3. **Cache Issues**: Clear session state and restart
4. **Environment Issues**: Verify environment configuration

### Debug Mode

Enable debug mode by setting environment variable:
```bash
export STREAMLIT_DEBUG=true
```

## Contributing

### Code Style
- Follow SOLID principles
- Use type hints
- Write comprehensive docstrings
- Add unit tests for new features

### Pull Request Process
1. Create feature branch
2. Implement changes following SOLID principles
3. Add tests
4. Update documentation
5. Submit pull request

## License

This project is part of the JPAPI suite and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the architecture documentation
3. Create an issue with detailed information
4. Include error messages and steps to reproduce

## Changelog

### Version 2.0.0
- Complete SOLID refactoring
- New component architecture
- Enhanced error handling
- Improved user experience
- Professional directory structure

### Version 1.0.0
- Initial implementation
- Basic functionality
- Legacy architecture