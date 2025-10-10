# Streamlit Management Guide

## 🧹 Cleanup Commands

### Kill all running Streamlit processes:
```bash
python3 streamlit_manager.py kill
```

### Full cleanup (kill processes + remove temp files):
```bash
python3 streamlit_manager.py cleanup
```

### Check status:
```bash
python3 streamlit_manager.py status
```

### List all Streamlit files:
```bash
python3 streamlit_manager.py list
```

## 🎛️ Interactive Management

Run the interactive manager:
```bash
python3 streamlit_manager.py
```

This gives you a menu to:
1. List files
2. Run specific files
3. Kill all processes
4. Cleanup
5. Check status

## 📁 Current Streamlit Files

- `object_manager.py` - **Main production file** (use this one)
- `object_manager_clean.py` - Clean version with fancy styling
- `object_manager_v5.py` - Over-engineered version (avoid)

## 🚀 Running the Main App

```bash
# Run the main production app
python3 -m streamlit run src/apps/streamlit/object_manager.py --server.port 8501
```

## 🧽 Quick Cleanup

If things get messy:
```bash
# Kill everything
pkill -f streamlit

# Clean temp files
rm -f *.html
rm -f src/apps/streamlit/navigation.py
rm -f src/apps/streamlit/dropdown_components.py
rm -f src/apps/streamlit/javascript_handler.py
```

## 📝 Best Practices

1. **Use `object_manager.py`** for actual work
2. **Run cleanup regularly** to avoid port conflicts
3. **Use the manager script** instead of manual commands
4. **Delete experimental files** when done testing
