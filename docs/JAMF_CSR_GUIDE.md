# 🔐 Jamf Pro Built-in CA Certificate Signing Guide

Following the official Jamf Learning Hub directions: [Creating a Signing Certificate Using Jamf Pro's Built-in CA](https://learn.jamf.com/en-US/bundle/technical-articles/page/Creating_a_Signing_Certificate_Using_Jamf_Pros_Built-in_CA_to_Use_for_Signing_Configuration_Profiles_and_Packages.html)

## ✅ Step 1: CSR Generated Successfully

Your CSR has been generated with the following details:
- **Common Name**: Code Signing Certificate
- **Organization**: Your Organization
- **Organizational Unit**: IT Department
- **Country**: US
- **State**: New York
- **City**: Your City
- **Email**: admin@example.com

**Generated Files:**
- `Code_Signing_Certificate_csr.pem` - Certificate Signing Request
- `Code_Signing_Certificate_private_key.pem` - Private Key (keep secure!)

## 📋 Step 2: Upload CSR to Jamf Pro

1. **Log into your Jamf Pro instance**
2. **Navigate to**: Settings → Global Management → Certificate Authority
3. **Click**: "Create Certificate Authority"
4. **Select**: "Built-in Certificate Authority"
5. **Upload the CSR file**: `Code_Signing_Certificate_csr.pem`
6. **Configure the certificate**:
   - **Certificate Name**: "Code Signing Certificate"
   - **Certificate Type**: Select "Code Signing" (if available)
   - **Validity Period**: Set as needed (e.g., 1 year)
7. **Click**: "Save"

## 📥 Step 3: Download the Signed Certificate

1. **Navigate to**: Settings → Global Management → Certificate Authority
2. **Find your certificate**: "Code Signing Certificate"
3. **Click**: "Download" or "Export"
4. **Save as**: `Code_Signing_Certificate_signed.pem` or similar

## 🔑 Step 4: Import Certificate and Private Key into Keychain

### Import the Certificate:
```bash
# Import the signed certificate
security import Code_Signing_Certificate_signed.pem -k ~/Library/Keychains/login.keychain

# Or use Keychain Access app:
# 1. Open Keychain Access
# 2. File → Import Items
# 3. Select the signed certificate file
# 4. Choose "login" keychain
```

### Import the Private Key:
```bash
# Import the private key
security import Code_Signing_Certificate_private_key.pem -k ~/Library/Keychains/login.keychain

# Or use Keychain Access app:
# 1. Open Keychain Access
# 2. File → Import Items
# 3. Select the private key file
# 4. Choose "login" keychain
```

## 🔍 Step 5: Verify the Certificate

```bash
# Check if the certificate is available for code signing
security find-identity -v -p codesigning

# You should see something like:
# 1) ABC1234567890ABCDEF1234567890ABCDEF1234 "Code Signing Certificate"
```

## 📦 Step 6: Sign Your Package

Once the certificate is imported and verified:

```bash
# Sign your package using JPAPI
jpapi certificate sign --package "/path/to/your-package.pkg" --identity "Code Signing Certificate"

# Or sign directly with codesign
codesign --sign "Code Signing Certificate" --force --verbose /path/to/your-package.pkg
```

## 🔍 Step 7: Verify the Signature

```bash
# Verify the signed package
codesign --verify --verbose /path/to/your-package_signed.pkg

# Check package info
pkgutil --pkg-info-plist /path/to/your-package_signed.pkg
```

## 🚨 Troubleshooting

### If the certificate doesn't appear in code signing identities:
1. **Check certificate type**: Make sure it was created as a "Code Signing" certificate in Jamf Pro
2. **Verify keychain**: Ensure both certificate and private key are in the same keychain
3. **Check permissions**: Make sure the private key is accessible

### If codesign fails:
1. **Check certificate validity**: `security find-certificate -c "Code Signing Certificate" -p | openssl x509 -text -noout`
2. **Verify extended key usage**: Look for "Code Signing" in the output
3. **Check keychain access**: Ensure the certificate is in the correct keychain

## 📚 Additional Resources

- [Jamf Pro Built-in CA Documentation](https://learn.jamf.com/en-US/bundle/technical-articles/page/Creating_a_Signing_Certificate_Using_Jamf_Pros_Built-in_CA_to_Use_for_Signing_Configuration_Profiles_and_Packages.html)
- [Apple Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [JPAPI Certificate Management Documentation](docs/CERTIFICATE_MANAGEMENT.md)

## 🎯 Expected Result

After completing these steps, you should have:
- ✅ A code signing certificate in your keychain
- ✅ The ability to sign packages with `codesign`
- ✅ A signed version of your package
- ✅ Full integration with JPAPI's package signing features

---

**Generated on**: $(date)  
**CSR File**: `Code_Signing_Certificate_csr.pem`  
**Private Key**: `Code_Signing_Certificate_private_key.pem`  
**Next Action**: Upload CSR to Jamf Pro's built-in CA


