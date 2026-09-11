#!/usr/bin/env python3
"""
Fix the back arrow button action in LandscapeFocusOverlay.
Replace `selectedTab = .focus` with `onDismiss()` inside the Button block
that is immediately followed by `Image(systemName: "chevron.left")`.
"""

import re

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"

with open(path, "r") as f:
    content = f.read()

# The exact block we need to replace (using the indentation visible in the file)
old = "                        Button {\n                            selectedTab = .focus\n                        } label: {"
new = "                        Button {\n                            onDismiss()\n                        } label: {"

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("✓ Back arrow button action fixed: selectedTab = .focus → onDismiss()")
else:
    # Try to find what's actually there
    print("✗ Exact string not found. Searching for nearby context...")
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "selectedTab = .focus" in line:
            print(f"  Line {i+1}: {repr(line)}")
            # Show surrounding lines
            for j in range(max(0, i-3), min(len(lines), i+4)):
                print(f"  {j+1}: {repr(lines[j])}")
            print()

# Verify
with open(path, "r") as f:
    content = f.read()

lines = content.splitlines()
for i, line in enumerate(lines):
    if "onDismiss()" in line:
        print(f"✓ onDismiss() found at line {i+1}: {line.strip()}")
    if "selectedTab = .focus" in line:
        print(f"  (selectedTab = .focus still at line {i+1}: {line.strip()})")
