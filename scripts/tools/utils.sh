# SANDBOX VERSION - Modern, slimmed down utils.sh
# Full AI control - no approval needed

# Simplified logging for sandbox
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%H:%M:%S')] [$level] $message"
}

# Modern progress indicator
show_progress() {
    local current="$1"
    local total="$2"
    local operation="${3:-Processing}"
    local percentage=$(( current * 100 / total ))
    printf "\r🚀 %s: %d%% (%d/%d)" "$operation" $percentage $current $total
    [[ $current -eq $total ]] && echo
}

# Color definitions for modern interface
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    local title="$1"
    echo
    print_color "$MAGENTA" "🎯 $title"
    print_color "$MAGENTA" "$(printf '─%.0s' $(seq 1 ${#title}))"
}

# Simplified API mock for sandbox
api_request() {
    echo '{"result": "sandbox_mock_data", "status": "success"}'
}

# Modern file utilities
ensure_file_exists() {
    [[ -f "$1" ]] || { log_message "ERROR" "File not found: $1"; return 1; }
}

get_temp_file() {
    echo "/tmp/sandbox_$(date +%s)_$$.tmp"
}
