# Dependency Security Assessment: oktaloginwrapper

## Package Information

- **Name**: oktaloginwrapper
- **Version**: 0.2.2 (latest as of search)
- **Source**: PyPI (Python Package Index)
- **GitHub**: https://github.com/B-Souty/OktaLoginWrapper
- **Author**: B-Souty (benjamin.souty@gmail.com)
- **License**: MIT License
- **Dependencies**: `lxml`, `requests` (both standard, well-maintained packages)

## Usage Statistics

- **GitHub Stars**: 9
- **GitHub Forks**: 10
- **Last Updated**: March 2024
- **Open Issues**: 0
- **PyPI Downloads**: Limited data available

## Security Assessment

### ✅ Positive Indicators

1. **Official PyPI Package**: Listed on the official Python Package Index
2. **MIT License**: Open source, permissive license
3. **Source Available**: Code is publicly available on GitHub
4. **Standard Dependencies**: Uses well-known packages (`requests`, `lxml`)
5. **No Known Vulnerabilities**: No security advisories found in search
6. **Active Repository**: Repository exists and is accessible

### ⚠️ Concerns

1. **Low Adoption**: Very small user base (9 stars, 10 forks)
2. **Limited Security Reviews**: No public security audits found
3. **Single Maintainer**: Appears to be maintained by one person
4. **Limited Documentation**: Basic documentation, no enterprise security guidance
5. **No Security Disclosure Process**: No clear security reporting process documented

## Recommendations for Enterprise Deployment

### Option 1: Pre-Install via Jamf (Recommended)

**Best Practice**: Install `oktaloginwrapper` as a separate Jamf policy before deploying this script.

**Benefits**:
- Control over when/where package is installed
- Can review package before deployment
- Can pin to specific version
- Better audit trail
- Users don't need admin rights

**Implementation**:
```bash
# In a separate Jamf policy or script:
pip3 install --user oktaloginwrapper
# Or for system-wide:
pip3 install oktaloginwrapper
```

### Option 2: Use Script with Auto-Install (Current)

**Current Behavior**: Script automatically installs if missing

**Security Considerations**:
- Package is downloaded from PyPI (trusted source)
- Installation happens at runtime
- Users may need admin rights for system-wide install
- Less control over version

**Mitigation**:
- Set `GP_NO_AUTO_INSTALL=1` to disable auto-install
- Pre-install via Jamf policy instead

### Option 3: Alternative Implementation

If security concerns are too high, consider:

1. **Implement Custom Okta Auth**: Use Okta's official API with proper OAuth/OIDC flow
2. **Use Official Okta SDK**: If available for Python
3. **Use Different Library**: Research other Okta authentication libraries

## Code Review Checklist

Before deploying, consider reviewing:

1. ✅ Source code on GitHub: https://github.com/B-Souty/OktaLoginWrapper
2. ✅ Check for hardcoded credentials or secrets
3. ✅ Verify it only uses standard Okta API endpoints
4. ✅ Ensure it doesn't log or store passwords
5. ✅ Check for proper error handling
6. ✅ Verify HTTPS usage for all connections

## Risk Assessment

**Risk Level**: **Medium-Low**

- Package appears legitimate and functional
- Small user base means less testing in production
- No known security issues, but also no security audits
- MIT license allows code review
- Dependencies (`requests`, `lxml`) are well-established and secure

## Recommendation

For enterprise deployment via Jamf:

1. **Pre-install the package** via a separate Jamf policy
2. **Pin to a specific version** (e.g., 0.2.2) to avoid unexpected updates
3. **Review the source code** before deployment
4. **Monitor for updates** and security advisories
5. **Consider setting `GP_NO_AUTO_INSTALL=1`** in the script to prevent runtime installs

This approach gives you:
- Better control
- Audit trail
- Version management
- Security review opportunity

## Alternative: Disable Auto-Install

To disable auto-installation in the script, set:

```bash
export GP_NO_AUTO_INSTALL=1
./download_globalprotect.sh
```

Or in Jamf policy, add as an environment variable.

