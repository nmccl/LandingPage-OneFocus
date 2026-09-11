import re

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/OneFocusApp.swift"

with open(path, 'r') as f:
    content = f.read()

old = """            #if os(macOS)
            // Handle the OAuth callback URL (onefocus://auth/callback)
            .onOpenURL { url in
                authManager.handleOAuthCallback(url: url)
            }"""

new = """            // Handle the OAuth callback URL (onefocus://auth/callback) on both platforms
            .onOpenURL { url in
                authManager.handleOAuthCallback(url: url)
            }
            #if os(macOS)"""

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print("SUCCESS: iOS onOpenURL handler added")
else:
    # Try to find the actual text
    idx = content.find("#if os(macOS)\n            // Handle the OAuth callback URL")
    if idx != -1:
        print(f"Found at index {idx}, context:")
        print(repr(content[idx-5:idx+200]))
    else:
        print("Pattern not found. Searching for onOpenURL...")
        idx2 = content.find(".onOpenURL")
        if idx2 != -1:
            print(repr(content[idx2-100:idx2+200]))
        else:
            print("onOpenURL not found at all")
