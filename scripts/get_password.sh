#!/bin/bash
# Helper script to get password via osascript

MESSAGE="$1"
TITLE="${2:-GlobalProtect Downloader}"

# Escape special characters for AppleScript
MESSAGE_ESC=$(echo "$MESSAGE" | sed 's/"/\\"/g' | sed "s/'/\\\'/g")
TITLE_ESC=$(echo "$TITLE" | sed 's/"/\\"/g' | sed "s/'/\\\'/g")

osascript <<APPLESCRIPT
try
    set theDialog to display dialog "$MESSAGE_ESC" default answer "" with title "$TITLE_ESC" buttons {"OK", "Cancel"} default button "OK" with hidden answer
    set theAnswer to text returned of theDialog
    return theAnswer
on error number -128
    return ""
on error
    return ""
end try
APPLESCRIPT

