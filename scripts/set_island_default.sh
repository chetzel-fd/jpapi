#!/bin/bash
# Force-set Island as default browser for the logged-in user by editing LSHandlers
# No external tools. Removes conflicting handlers first, then inserts Island.

set -e

BUNDLE_ID="io.island.Island"
TARGET_USER=$(stat -f "%Su" /dev/console)

if [ -z "$TARGET_USER" ] || [ "$TARGET_USER" = "root" ] || [ "$TARGET_USER" = "loginwindow" ]; then
    echo "[ERROR] No logged-in user found" >&2
    exit 1
fi

USER_HOME=$(dscl . -read /Users/$TARGET_USER NFSHomeDirectory 2>/dev/null | awk '{print $2}')
if [ -z "$USER_HOME" ]; then
    USER_HOME="/Users/$TARGET_USER"
fi

PLIST_PATH="$USER_HOME/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist"
PLIST_DIR="$(dirname "$PLIST_PATH")"

mkdir -p "$PLIST_DIR"

/usr/bin/python3 <<PYCODE
import os, plistlib
plist_path = os.path.expanduser(r"$PLIST_PATH")
bundle_id = r"$BUNDLE_ID"

# Keys we will own
url_schemes = ["http", "https"]
content_types = ["public.html", "public.xhtml", "public.url"]

handlers = []
if os.path.exists(plist_path):
    try:
        with open(plist_path, 'rb') as f:
            data = plistlib.load(f)
            handlers = data.get('LSHandlers', []) or []
    except Exception:
        handlers = []

# Filter out any existing handlers we will manage
filtered = []
for h in handlers:
    if h.get('LSHandlerURLScheme') in url_schemes:
        continue
    if h.get('LSHandlerContentType') in content_types:
        continue
    filtered.append(h)

# Prepend our Island handlers so they win
new_handlers = []
for scheme in url_schemes:
    new_handlers.append({
        'LSHandlerURLScheme': scheme,
        'LSHandlerRoleAll': bundle_id
    })

for ctype in content_types:
    # role viewer for public.url, role all for html types
    if ctype == 'public.url':
        new_handlers.append({
            'LSHandlerContentType': ctype,
            'LSHandlerRoleViewer': bundle_id
        })
    else:
        new_handlers.append({
            'LSHandlerContentType': ctype,
            'LSHandlerRoleAll': bundle_id
        })

result = {'LSHandlers': new_handlers + filtered}

os.makedirs(os.path.dirname(plist_path), exist_ok=True)
with open(plist_path, 'wb') as f:
    plistlib.dump(result, f)

print('Wrote Island handlers at top for http/https/html/url')
PYCODE

# Ensure ownership is correct
chown "$TARGET_USER":"staff" "$PLIST_PATH" 2>/dev/null || true

# Flush prefs and LS registration for user domain
sudo -u "$TARGET_USER" killall cfprefsd 2>/dev/null || true
/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -kill -r -domain user >/dev/null 2>&1 || true

# Verify
/usr/bin/defaults read "$USER_HOME/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure" LSHandlers 2>/dev/null | \
  /usr/bin/awk '/LSHandlerURLScheme = (http|https);/{p=1;print;next} p&&/LSHandler/{print; if (++n==4) p=0}' || true

echo "[INFO] Island default set attempt complete for $TARGET_USER"
