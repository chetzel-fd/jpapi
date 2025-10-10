"""
Application Constants
Centralized constants for the JPAPI Streamlit UI
"""

# Application Constants
APP_NAME = "JPAPI Manager"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "JAMF Pro API Management Dashboard"

# UI Constants
DEFAULT_PAGE_TITLE = "JPAPI Manager"
DEFAULT_PAGE_ICON = "⚡"
DEFAULT_LAYOUT = "wide"
DEFAULT_SIDEBAR_STATE = "expanded"

# Cache Constants
CACHE_PREFIX = "data_"
CACHE_TTL_SECONDS = 3600  # 1 hour
CACHE_MAX_SIZE_MB = 100

# Export Constants
DEFAULT_EXPORT_FORMAT = "csv"
SUPPORTED_EXPORT_FORMATS = ["csv", "json", "xlsx"]
MAX_EXPORT_ROWS = 10000

# Status Constants
VALID_STATUSES = ["Active", "Deleted", "Inactive"]
DEFAULT_STATUS = "Active"

# Smart Group Constants
SMART_TRUE_VALUES = [True, 1, "True", "true", "1"]
SMART_FALSE_VALUES = [False, 0, "False", "false", "0"]

# File Pattern Constants
CSV_FILE_EXTENSIONS = [".csv"]
JSON_FILE_EXTENSIONS = [".json"]
EXCEL_FILE_EXTENSIONS = [".xlsx", ".xls"]

# Environment Constants
DEFAULT_ENVIRONMENT = "sandbox"
ENVIRONMENT_SANDBOX = "sandbox"
ENVIRONMENT_PRODUCTION = "production"

# Object Type Constants
DEFAULT_OBJECT_TYPE = "searches"
OBJECT_TYPE_SEARCHES = "searches"
OBJECT_TYPE_POLICIES = "policies"
OBJECT_TYPE_PROFILES = "profiles"
OBJECT_TYPE_SCRIPTS = "scripts"

# UI Component Constants
HEADER_HEIGHT = 60
SIDEBAR_WIDTH = 300
CARD_HEIGHT = 120
BUTTON_HEIGHT = 36
BUTTON_WIDTH = 36

# Color Constants
COLOR_PRIMARY = "#1f77b4"
COLOR_SECONDARY = "#ff7f0e"
COLOR_SUCCESS = "#2ca02c"
COLOR_WARNING = "#d62728"
COLOR_INFO = "#17a2b8"

# Status Colors
STATUS_ACTIVE_COLOR = "#28a745"
STATUS_DELETED_COLOR = "#dc3545"
STATUS_INACTIVE_COLOR = "#6c757d"

# Animation Constants
ANIMATION_DURATION_MS = 300
ANIMATION_EASING = "ease-in-out"

# Validation Constants
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 255
REQUIRED_COLUMNS = ["Name", "Status", "Modified"]
OPTIONAL_COLUMNS = ["Smart", "Description", "Category"]

# Error Messages
ERROR_NO_DATA_FOUND = "No data found for the selected criteria"
ERROR_INVALID_ENVIRONMENT = "Invalid environment selected"
ERROR_INVALID_OBJECT_TYPE = "Invalid object type selected"
ERROR_CSV_LOAD_FAILED = "Failed to load CSV data"
ERROR_CACHE_ERROR = "Cache operation failed"

# Success Messages
SUCCESS_DATA_LOADED = "Data loaded successfully"
SUCCESS_CACHE_CLEARED = "Cache cleared successfully"
SUCCESS_DATA_EXPORTED = "Data exported successfully"
SUCCESS_DATA_GATHERED = "Data gathered successfully"
