# 📦 JPAPI Distribution Plan

## Target: FanDuel SET MDM Team

**Repository Destination**: https://github.com/orgs/fanduel/teams/setmdm/  
**Prepared Date**: November 25, 2025  
**Version**: 2.0.0

---

## ✅ Pre-Distribution Checklist

### Sanitization Complete
- [x] Removed hardcoded company URLs from auth files
- [x] Updated `users.json` with generic defaults
- [x] Sanitized Dockerfile and docker-compose.yml
- [x] Cleared `authentication.json` credentials
- [x] Updated UI components to use environment variables
- [x] Changed signature defaults to generic "admin"
- [x] Replaced hardcoded paths with dynamic resolution

### Your Installation Preserved
- [x] Local keychain credentials unaffected
- [x] Stored signature config (`~/.jpapi/config.json`) takes precedence
- [x] Environment variables can override defaults

---

## 🚀 Distribution Steps

### Step 1: Create Repository in FanDuel Org

```bash
# Navigate to your jpapi directory
cd /Users/charles.hetzel/Documents/cursor/jpapi

# Add the FanDuel org remote (create repo first in GitHub UI)
git remote add fanduel git@github.com:fanduel/jpapi.git

# Or if repo already exists:
git remote set-url origin git@github.com:fanduel/jpapi.git
```

### Step 2: Clean Git History (Optional but Recommended)

If you want to remove any historical commits with sensitive data:

```bash
# Option A: Fresh start (recommended for distribution)
# Create a new branch with clean history
git checkout --orphan clean-main
git add -A
git commit -m "Initial JPAPI distribution - v2.0.0"
git branch -D main
git branch -m main
git push -f fanduel main

# Option B: Keep history, verify no secrets
git log --all --full-history -- "*password*" "*secret*" "*credential*"
```

### Step 3: Push to FanDuel Organization

```bash
# Push to the FanDuel org repository
git push -u fanduel main

# Push tags if you have version tags
git push fanduel --tags
```

### Step 4: Configure Team Access

1. Go to https://github.com/orgs/fanduel/teams/setmdm/
2. Navigate to **Repositories** tab
3. Add `fanduel/jpapi` repository
4. Set permissions to **Write** or **Maintain** for the SET MDM team

---

## 👥 Team Onboarding Guide

### First-Time Setup for Team Members

```bash
# 1. Clone the repository
git clone git@github.com:fanduel/jpapi.git
cd jpapi

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install jpapi
pip install -e .

# 4. Configure authentication
jpapi setup auth

# 5. Set personal signature
jpapi create signature --set "yourname"
```

### Environment Variables (Optional)

Team members can set these in their shell profile:

```bash
# ~/.zshrc or ~/.bashrc
export JPAPI_SANDBOX_URL="https://fanduelgrouptest.jamfcloud.com"
export JPAPI_PROD_URL="https://fanduelgroup.jamfcloud.com"
export JPAPI_SERVER_NAME="fanduelgrouptest"
export JPAPI_SERVER_URL="https://fanduelgrouptest.jamfcloud.com"
```

---

## 📋 Repository Configuration

### Recommended Branch Protection Rules

1. **main branch**:
   - Require pull request reviews (1 approver)
   - Require status checks to pass
   - Restrict pushes to admins only

2. **develop branch** (optional):
   - Allow direct pushes from team
   - Good for active development

### Recommended Repository Settings

```yaml
# .github/settings.yml (if using probot/settings)
repository:
  name: jpapi
  description: "JAMF Pro API Toolkit for SET MDM Team"
  private: true  # Keep internal
  has_issues: true
  has_wiki: false
  default_branch: main

teams:
  - name: setmdm
    permission: write
```

---

## 🔐 Security Recommendations

### For the Repository

1. **Enable secret scanning** - Detect accidental credential commits
2. **Enable Dependabot** - Keep dependencies updated
3. **Add branch protection** - Prevent force pushes to main
4. **Use CODEOWNERS** - Require reviews from specific people

```
# .github/CODEOWNERS
* @fanduel/setmdm
src/core/auth/* @charles-hetzel
```

### For Team Members

1. **Use keychain** - Never store credentials in files
2. **Set signature** - Identify who created Jamf objects
3. **Use sandbox first** - Test changes before production
4. **Enable dry-run** - Preview destructive operations

---

## 📚 Team Documentation

Share these key docs with the team:

| Document | Purpose |
|----------|---------|
| `README.md` | Quick start and overview |
| `docs/QUICK_START.md` | Detailed setup guide |
| `docs/INTEGRATION_GUIDE.md` | Integration examples |
| `INSTALLATION.md` | Installation options |

---

## 🔄 Maintenance Plan

### Regular Tasks

| Frequency | Task |
|-----------|------|
| Weekly | Review and merge PRs |
| Monthly | Update dependencies |
| Quarterly | Security audit |
| As needed | Add new features |

### Version Control

```bash
# Create a release
git tag -a v2.0.1 -m "Release 2.0.1 - Bug fixes"
git push fanduel --tags
```

---

## 📞 Support Structure

### Internal Support

- **Primary**: Charles Hetzel (charles.hetzel@fanduel.com)
- **Slack**: #set-mdm-jpapi (create this channel)
- **Issues**: https://github.com/fanduel/jpapi/issues

### Issue Templates

Create these in `.github/ISSUE_TEMPLATE/`:

1. `bug_report.md` - For bugs
2. `feature_request.md` - For new features
3. `question.md` - For general questions

---

## ✅ Post-Distribution Verification

After pushing to GitHub:

```bash
# 1. Clone in a new location to verify
cd /tmp
git clone git@github.com:fanduel/jpapi.git jpapi-test
cd jpapi-test

# 2. Search for any remaining sensitive data
grep -r "chetzel\|charles.hetzel\|fanduelgrouptest" --include="*.py" --include="*.json" .

# 3. Test installation
python3 -m venv test-venv
source test-venv/bin/activate
pip install -e .
jpapi --help

# 4. Clean up
cd ..
rm -rf jpapi-test
```

---

## 📊 Summary

| Item | Status |
|------|--------|
| Code sanitization | ✅ Complete |
| Personal data removed | ✅ Complete |
| Environment variables | ✅ Configured |
| Documentation | ✅ Ready |
| Team onboarding guide | ✅ Created |

**Ready for distribution to FanDuel SET MDM team!** 🎉

---

*Document created: November 25, 2025*

