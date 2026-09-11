#!/usr/bin/env python3
"""
Update PrivacyInfo.xcprivacy to add NSPrivacyAccessedAPICategoryPasteboard
since the app uses NSPasteboard (macOS) and UIPasteboard (iOS) for clipboard.
Reason code: C56D.1 — App uses clipboard API to read/write user-initiated content
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/PrivacyInfo.xcprivacy"

with open(path) as f:
    content = f.read()

# Check if pasteboard already declared
if "NSPrivacyAccessedAPICategoryPasteboard" in content:
    print("~ Pasteboard already in PrivacyInfo.xcprivacy")
else:
    # Insert pasteboard entry before the closing </array> of NSPrivacyAccessedAPITypes
    pasteboard_entry = """        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryPasteboard</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>C56D.1</string>
            </array>
        </dict>
    </array>"""

    old = "    </array>\n</dict>"
    new = f"{pasteboard_entry}\n</dict>"

    if old in content:
        content = content.replace(old, new, 1)
        with open(path, "w") as f:
            f.write(content)
        print("✓ Added NSPrivacyAccessedAPICategoryPasteboard to PrivacyInfo.xcprivacy")
    else:
        print("✗ Could not find closing </array> in PrivacyInfo.xcprivacy")

print("\nFinal content:")
with open(path) as f:
    print(f.read())
