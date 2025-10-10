# Deployment Scripts

This directory contains scripts for deploying and distributing JPAPI.

## 📁 Contents

### Public Deployment
- `deploy_to_public.sh` - Main public repository deployment script
- `sanitize_for_public.sh` - Data sanitization for public release
- `quick_clean_for_public.sh` - Quick cleanup for public deployment
- `simple_public_push.sh` - Simple push to public repository

### Production Uploads
- `upload_to_production.py` - Production environment uploads

## 🚀 Usage

### Public Deployment
```bash
# Full deployment with sanitization
./scripts/deploy/deploy_to_public.sh

# Quick deployment
./scripts/deploy/simple_public_push.sh

# Sanitize data only
./scripts/deploy/sanitize_for_public.sh
```

### Production Uploads
```bash
# Upload to production
python3 scripts/deploy/upload_to_production.py
```

## 🔒 Security

All deployment scripts include:
- Sensitive data sanitization
- Credential removal
- Company-specific information filtering
- Safe file exclusions

## 📚 Guidelines

- Always test deployment scripts in a safe environment first
- Review sanitization output before public deployment
- Keep deployment scripts up to date with project changes
- Document any new deployment procedures
