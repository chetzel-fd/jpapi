#!/bin/bash
# Start Redis with optimized configuration for JAMF datasets

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REDIS_CONF="$PROJECT_ROOT/config/redis.conf"
REDIS_DATA_DIR="$PROJECT_ROOT/cache/redis"
REDIS_LOG_FILE="$PROJECT_ROOT/logs/redis.log"

# Create necessary directories
mkdir -p "$REDIS_DATA_DIR"
mkdir -p "$(dirname "$REDIS_LOG_FILE")"

echo "🚀 Starting Redis for JAMF Enterprise Backend"
echo "📁 Data directory: $REDIS_DATA_DIR"
echo "📋 Config file: $REDIS_CONF"
echo "📝 Log file: $REDIS_LOG_FILE"

# Check if Redis is already running
if pgrep -f "redis-server.*$REDIS_CONF" > /dev/null; then
    echo "⚠️  Redis is already running with this configuration"
    echo "   Use 'pkill -f redis-server' to stop it first"
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed"
    echo "   Install with: brew install redis (macOS) or apt-get install redis-server (Ubuntu)"
    exit 1
fi

# Validate configuration file
if [ ! -f "$REDIS_CONF" ]; then
    echo "❌ Redis configuration file not found: $REDIS_CONF"
    exit 1
fi

# Test configuration
echo "🔍 Validating Redis configuration..."
if ! redis-server "$REDIS_CONF" --test-memory 1; then
    echo "❌ Redis configuration validation failed"
    exit 1
fi

# Start Redis in background
echo "🔄 Starting Redis server..."
cd "$REDIS_DATA_DIR"

# Start Redis with custom config
redis-server "$REDIS_CONF" \
    --dir "$REDIS_DATA_DIR" \
    --logfile "$REDIS_LOG_FILE" \
    --daemonize yes \
    --pidfile "$REDIS_DATA_DIR/redis.pid"

# Wait for Redis to start
sleep 2

# Check if Redis started successfully
if ! pgrep -f "redis-server.*$REDIS_CONF" > /dev/null; then
    echo "❌ Failed to start Redis server"
    echo "   Check log file: $REDIS_LOG_FILE"
    exit 1
fi

# Test connection
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis server started successfully"
    echo "   Connection: localhost:6379"
    echo "   PID file: $REDIS_DATA_DIR/redis.pid"
    echo "   Log file: $REDIS_LOG_FILE"
    
    # Show memory info
    echo ""
    echo "📊 Redis Memory Info:"
    redis-cli INFO memory | grep -E "(used_memory_human|maxmemory_human|mem_fragmentation_ratio)"
    
    echo ""
    echo "🎯 Ready for JAMF Enterprise Backend on port 8900"
    echo "   Start backend with: python3 src/jamf_backend_enhanced.py"
else
    echo "❌ Redis server started but connection failed"
    echo "   Check log file: $REDIS_LOG_FILE"
    exit 1
fi
