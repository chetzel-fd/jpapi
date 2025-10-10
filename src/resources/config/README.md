# JPAPI Centralized Configuration System

A unified configuration management system for JPAPI that eliminates hardcoded values and provides a single source of truth for all configuration options.

## Overview

The centralized configuration system replaces scattered hardcoded values throughout the JPAPI codebase with a unified, maintainable configuration system. This improves maintainability, reduces errors, and provides a consistent interface for configuration management.

## Features

### 🎯 **Single Source of Truth**
- All configuration in one place
- No more scattered hardcoded values
- Consistent configuration across all components

### 🔧 **Environment-Specific Configuration**
- Different settings for dev/staging/prod
- Environment variable overrides
- Configuration inheritance

### 📊 **Comprehensive Configuration Management**
- Server ports and endpoints
- Timeout values and retry settings
- Path configurations
- Output formats and options
- User management and roles
- Logging configuration

### 🖥️ **GUI Configuration Interface**
- Modern graphical interface
- Real-time configuration updates
- Service management
- Configuration validation

### 💻 **CLI Configuration Commands**
- Command-line configuration management
- Configuration import/export
- Validation and testing
- Batch configuration updates

## Configuration Files

### Core Configuration Files

| File | Purpose | Description |
|------|---------|-------------|
| `server_ports.json` | Server ports | Ports for all JPAPI services |
| `environments.json` | Environment settings | Environment configuration and aliases |
| `output_formats.json` | Output formats | Data formats, status options, filter types |
| `paths.json` | Directory paths | All directory configurations |
| `timeouts.json` | Timeout values | API, cache, and operation timeouts |
| `version.json` | Version information | Version numbers and build info |
| `logging.json` | Logging configuration | Log levels and component settings |
| `users.json` | User management | User roles and signatures |

### Configuration Structure

```json
{
  "server_ports": {
    "backend_fast": 8600,
    "backend_enhanced": 8900,
    "redis": 6379,
    "dashboard": 5000,
    "api_docs": 8080
  },
  "environments": {
    "default": "dev",
    "available": ["dev", "staging", "prod", "test"],
    "aliases": {
      "development": "dev",
      "production": "prod"
    }
  },
  "timeouts": {
    "api_timeout": 30,
    "cache_timeout": 300,
    "operation_timeout": 300,
    "connection_timeout": 10,
    "retry_timeout": 5
  }
}
```

## Usage

### GUI Interface

Launch the configuration GUI:
```bash
# Using the launcher script
./bin/jpapi-gui

# Or directly
python gui/launch_gui.py
```

The GUI provides:
- **Overview**: System status and quick actions
- **Servers**: Port configuration and environment settings
- **Paths**: Directory path management
- **Timeouts**: Timeout value configuration
- **Formats**: Output format options
- **Users**: User management and roles
- **Logging**: Log level configuration
- **Actions**: Import/export and service management

### CLI Commands

#### Show Configuration
```bash
# Show all configuration
jpapi config show

# Show specific section
jpapi config show --section ports

# Output in different formats
jpapi config show --format json
jpapi config show --format yaml
```

#### Set Configuration Values
```bash
# Set port values
jpapi config set ports backend_fast 8600
jpapi config set ports backend_enhanced 8900

# Set timeout values
jpapi config set timeouts api_timeout 30
jpapi config set timeouts cache_timeout 300

# Set environment
jpapi config set environments default prod
```

#### Get Configuration Values
```bash
# Get specific values
jpapi config get ports backend_fast
jpapi config get timeouts api_timeout
jpapi config get environments default
```

#### Import/Export Configuration
```bash
# Export configuration
jpapi config export config_backup.json

# Import configuration
jpapi config import config_backup.json

# Reset to defaults
jpapi config reset
jpapi config reset --section ports
```

#### Validate Configuration
```bash
# Validate configuration
jpapi config validate

# Validate and fix issues
jpapi config validate --fix
```

#### Launch GUI
```bash
# Launch GUI
jpapi config gui

# Launch GUI in background
jpapi config gui --background
```

## Integration

### Using Configuration in Code

```python
from config.central_config import get_port, get_timeout, get_path, get_log_level

# Get configuration values
port = get_port("backend_fast")  # Returns 8600
timeout = get_timeout("api_timeout")  # Returns 30
cache_dir = get_path("cache_dir")  # Returns ~/.jpapi/cache
log_level = get_log_level("api")  # Returns INFO
```

### Updating Configuration Programmatically

```python
from config.central_config import central_config

# Update configuration
central_config.update_config("ports", "backend_fast", 8600)
central_config.update_config("timeouts", "api_timeout", 30)

# Save configuration
central_config.save_all_configs()
```

### Environment Variable Overrides

The system supports environment variable overrides:

```bash
export JAMF_URL="https://your-company.jamfcloud.com"
export JAMF_USERNAME="your-username"
export JAMF_PASSWORD="your-password"
export LOG_LEVEL="DEBUG"
```

## Migration from Hardcoded Values

### Before (Hardcoded)
```python
# Multiple files with hardcoded values
uvicorn.run(app, host="0.0.0.0", port=8600)
timeout=30
cache_dir = "~/.jpapi/cache"
log_level = "INFO"
```

### After (Centralized)
```python
# Single source of truth
from config.central_config import get_port, get_timeout, get_path, get_log_level

port = get_port("backend_fast")
timeout = get_timeout("api_timeout")
cache_dir = get_path("cache_dir")
log_level = get_log_level("api")
```

## Benefits

### 🚀 **Improved Maintainability**
- Single place to update configuration
- No more hunting for hardcoded values
- Consistent configuration across components

### 🔒 **Better Security**
- Centralized credential management
- Environment-specific configurations
- Configuration validation

### 🎛️ **Enhanced Flexibility**
- Runtime configuration changes
- Environment-specific overrides
- Easy configuration testing

### 📊 **Better Monitoring**
- Configuration validation
- Change tracking
- Audit logging

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   ```bash
   # Check if configuration files exist
   ls config/*.json
   
   # Validate configuration
   jpapi config validate
   ```

2. **GUI not starting**
   ```bash
   # Check tkinter availability
   python3 -c "import tkinter"
   
   # Install tkinter if needed
   sudo apt-get install python3-tk  # Ubuntu/Debian
   ```

3. **Port conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8600
   
   # Update port configuration
   jpapi config set ports backend_fast 8601
   ```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
jpapi config show
```

## Future Enhancements

### Planned Features
- Configuration templates and presets
- Real-time configuration validation
- Configuration change notifications
- Advanced user role management
- Configuration backup and restore
- Integration with external configuration systems

### Contributing

To add new configuration options:

1. Update the dataclass in `central_config.py`
2. Add corresponding JSON configuration file
3. Update GUI interface in `jpapi_gui.py`
4. Add CLI commands in `config_command.py`
5. Update documentation

## Support

For issues or questions:
1. Check the troubleshooting section
2. Validate configuration with `jpapi config validate`
3. Review configuration files in `config/` directory
4. Use the GUI for visual configuration management
