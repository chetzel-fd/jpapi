# 🔐 Certificate Management with JPAPI

JPAPI now includes comprehensive certificate management capabilities that integrate with Jamf Pro's built-in Certificate Authority (CA) for creating, managing, and signing packages and configuration profiles.

## 🚀 Quick Start

### Generate a CSR and Get it Signed

```bash
# Generate a CSR for package signing
jpapi certificate csr --common-name "Package Signing Certificate" --organization "Your Company"

# Upload the CSR to Jamf Pro for signing
jpapi certificate upload --csr "Package_Signing_Certificate_csr.pem" --certificate-name "My Signing Cert"

# Sign a package
jpapi certificate sign --package "my_package.pkg" --certificate-id "123"
```

### Package Signing Examples

```bash
# List available code signing identities
jpapi certificate manage --identities

# Sign a package with existing identity
jpapi certificate sign --package "/path/to/package.pkg" --identity "Developer ID Application: Your Name (ABC1234567)"

# Sign a package with Jamf Pro certificate
jpapi certificate sign --package "/path/to/package.pkg" --certificate-id "123"

# Sign a configuration profile
jpapi certificate sign --profile "my_profile.mobileconfig" --certificate-id "123"
```

## 📋 Available Commands

### Certificate Management (`jpapi certificate`)

#### Generate CSR (`csr`)
Creates a Certificate Signing Request for use with Jamf Pro's built-in CA.

```bash
jpapi certificate csr --common-name "My Certificate" --organization "My Company"
```

**Options:**
- `--common-name`, `-cn`: Common Name (CN) for the certificate (required)
- `--organization`, `-o`: Organization name
- `--organizational-unit`, `-ou`: Organizational Unit
- `--country`, `-c`: Country code (default: US)
- `--state`, `-st`: State or Province
- `--city`, `-l`: City or Locality
- `--email`, `-e`: Email address
- `--key-size`: RSA key size (1024, 2048, 4096) (default: 2048)
- `--output`: Output file path (auto-generated if not specified)
- `--key-output`: Private key output file path
- `--profile-signing`: Generate CSR specifically for profile signing

#### Manage Certificates (`manage`)
Manage certificates in Jamf Pro.

```bash
# List all certificates
jpapi certificate manage --list

# Get certificate details
jpapi certificate manage --info "123"

# Download certificate
jpapi certificate manage --download "123"

# Delete certificate
jpapi certificate manage --delete "123"

# List Certificate Authorities
jpapi certificate manage --ca-list
```

#### Sign Packages and Profiles (`sign`)
Sign packages and configuration profiles using Jamf Pro certificates or code signing identities.

```bash
# Sign a package
jpapi certificate sign --package "package.pkg" --identity "Developer ID Application: Your Name (ABC1234567)"

# Sign a profile
jpapi certificate sign --profile "profile.mobileconfig" --certificate-id "123"
```

**Options:**
- `--package`, `-p`: Path to package file (.pkg) to sign
- `--profile`: Path to mobileconfig file to sign
- `--certificate-id`, `-c`: Certificate ID from Jamf Pro
- `--identity`: Code signing identity (if not using Jamf Pro cert)
- `--output`, `-o`: Output path for signed file

#### Upload CSR (`upload`)
Upload CSR to Jamf Pro for signing by the built-in CA.

```bash
jpapi certificate upload --csr "my_csr.pem" --certificate-name "My Certificate"
```

**Options:**
- `--csr`: Path to CSR file (required)
- `--ca-id`: Certificate Authority ID (uses default if not specified)
- `--certificate-name`: Name for the certificate in Jamf Pro
- `--download-cert`: Download the signed certificate after upload

### CrowdStrike Integration (`jpapi crowdstrike`)

#### Create Profiles (`create`)
Create CrowdStrike-specific configuration profiles.

```bash
# Create Full Disk Access profile
jpapi crowdstrike create --type fda --name "CrowdStrike FDA"

# Create PPPC profile
jpapi crowdstrike create --type pppc --bundle-id "com.crowdstrike.falcon.App"

# Create network profile
jpapi crowdstrike create --type network --name "CrowdStrike Network"
```

**Options:**
- `--type`: Type of profile (fda, pppc, network) (required)
- `--name`: Profile name (auto-generated if not specified)
- `--output`: Output file path
- `--organization`: Organization name (default: FanDuel Group)
- `--bundle-id`: CrowdStrike bundle identifier

#### Sign Profiles (`sign`)
Sign CrowdStrike profiles with proper metadata.

```bash
jpapi crowdstrike sign --profile "crowdstrike_fda.mobileconfig"
```

#### Deploy Profiles (`deploy`)
Deploy CrowdStrike profiles directly to Jamf Pro.

```bash
jpapi crowdstrike deploy --profile "crowdstrike_fda.mobileconfig" --sign-before-deploy
```

**Options:**
- `--profile`, `-p`: Path to mobileconfig file (required)
- `--name`: Profile name in Jamf Pro
- `--description`: Profile description
- `--category`: Profile category
- `--scope`: Deployment scope
- `--sign-before-deploy`: Sign profile before deployment

#### Generate CSR (`csr`)
Generate CSR specifically for CrowdStrike certificate.

```bash
jpapi crowdstrike csr --upload
```

## 🔧 Technical Details

### CSR Generation
- Uses the `cryptography` library for secure key generation
- Supports RSA key sizes: 1024, 2048, 4096 bits
- Generates both CSR and private key files
- Private keys are secured with 600 permissions
- Supports all standard X.509 certificate fields

### Jamf Pro Integration
- Uploads CSRs to Jamf Pro's built-in CA
- Lists and manages certificates via JAMF API
- Downloads signed certificates
- Integrates with existing authentication system

### Profile Signing
- Adds signature metadata to mobileconfig files
- Supports verification of signed profiles
- Integrates with Jamf Pro certificate management
- Maintains profile integrity and authenticity

### CrowdStrike-Specific Features
- Pre-configured FDA profiles with proper code requirements
- PPPC profiles for privacy preferences
- Network configuration profiles
- Automated deployment to Jamf Pro
- Proper certificate chain validation

## 🛡️ Security Features

### Key Management
- Private keys are generated locally and never transmitted
- Secure file permissions (600) on private key files
- Support for hardware security modules (future enhancement)

### Certificate Validation
- Verifies certificate chain integrity
- Checks certificate expiration dates
- Validates code signing requirements
- Ensures proper certificate usage

### Profile Integrity
- Cryptographic signature verification
- Metadata integrity checks
- Tamper detection
- Audit trail for signed profiles

## 📚 Examples

### Complete Workflow: Sign a Package

```bash
# 1. Check available signing identities
jpapi certificate manage --identities

# 2. Sign your package
jpapi certificate sign --package "/Users/charles.hetzel/Desktop/onboardingBundle-chetzel-20250914.pkg" \
  --identity "Developer ID Application: Your Name (ABC1234567)"

# 3. Verify the signature
codesign --verify --verbose /Users/charles.hetzel/Desktop/onboardingBundle-chetzel-20250914_signed.pkg

# 4. Upload to Jamf Pro (if needed)
# Use existing JPAPI commands to upload the signed package
```

### Certificate Management Workflow

```bash
# 1. List existing certificates
jpapi certificate manage --list

# 2. Generate new CSR
jpapi certificate csr --common-name "New Signing Certificate" \
  --organization "My Company" \
  --organizational-unit "IT Department"

# 3. Upload CSR to Jamf Pro
jpapi certificate upload --csr "New_Signing_Certificate_csr.pem" \
  --certificate-name "IT Department Signing Cert"

# 4. Download the signed certificate
jpapi certificate manage --download "456"

# 5. Use certificate to sign profiles
jpapi certificate sign --profile "my_profile.mobileconfig" --certificate-id "456"
```

## 🔍 Troubleshooting

### Common Issues

**CSR Generation Fails**
```bash
# Check Python cryptography library
pip install cryptography

# Verify file permissions
ls -la *.pem
```

**Certificate Upload Fails**
```bash
# Check Jamf Pro connectivity
jpapi auth status

# Verify CSR format
openssl req -in my_csr.pem -text -noout
```

**Profile Signing Issues**
```bash
# List available certificates
jpapi certificate manage --list

# Check certificate details
jpapi certificate manage --info "123"
```

### Debug Mode
```bash
# Enable debug output
jpapi --debug certificate csr --common-name "Debug Cert"
```

## 🔗 Related Documentation

- [Jamf Pro Certificate Authority Documentation](https://learn.jamf.com/en-US/bundle/technical-articles/page/Creating_a_Signing_Certificate_Using_Jamf_Pros_Built-in_CA_to_Use_for_Signing_Configuration_Profiles_and_Packages.html)
- [Configuration Profile Signing Best Practices](https://developer.apple.com/documentation/devicemanagement/configuration_profile_signing)
- [CrowdStrike Falcon Documentation](https://falcon.crowdstrike.com/documentation)

## 🆘 Support

For issues with certificate management:

1. Check the troubleshooting section above
2. Verify your Jamf Pro permissions for certificate management
3. Ensure your environment has the required Python dependencies
4. Review the debug output for detailed error information

---

**Built with ❤️ for JAMF administrators and security teams**
