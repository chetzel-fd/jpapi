# Tools Directory

This directory contains operational utilities and maintenance tools for JPAPI.

## 📁 Contents

### Performance Monitoring
- `performance_monitor.py` - Tracks JPAPI performance metrics and architecture compliance

### Infrastructure
- `start_redis.sh` - Redis server startup script
- `fanduel_proxy_server.py` - Proxy server utility

## 🚀 Usage

```bash
# Performance monitoring
python3 scripts/tools/performance_monitor.py report

# Start Redis
./scripts/tools/start_redis.sh

# Proxy server
python3 scripts/tools/fanduel_proxy_server.py
```

## 📊 Performance Monitor

The performance monitor tracks:
- Bash vs Python operation split (target: 20%/80%)
- Execution times and success rates
- Architecture compliance metrics

Run `python3 scripts/tools/performance_monitor.py --help` for more options.
