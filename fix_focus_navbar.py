#!/usr/bin/env python3
"""
Remove .ignoresSafeArea(edges: .all) from the outer iOSFocusView body
so the tab bar (navbar) is no longer hidden in portrait mode.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"

with open(path, "r") as f:
    content = f.read()

old = "        .ignoresSafeArea(edges: .all)\n"
if old in content:
    content = content.replace(old, "", 1)
    with open(path, "w") as f:
        f.write(content)
    print("✓ Removed .ignoresSafeArea(edges: .all) from iOSFocusView body")
else:
    print("✗ String not found — checking what's there:")
    for i, line in enumerate(content.splitlines()):
        if "ignoresSafeArea" in line:
            print(f"  Line {i+1}: {repr(line)}")

# Verify
with open(path, "r") as f:
    lines = content.splitlines()
outer_ignore = [l for l in lines if "ignoresSafeArea(edges: .all)" in l]
if outer_ignore:
    print(f"  Still present: {outer_ignore}")
else:
    print("✓ .ignoresSafeArea(edges: .all) no longer on outer view")

# Confirm the landscape overlay still has its own ignoresSafeArea
inner = [l for l in lines if "ignoresSafeArea" in l]
for l in inner:
    print(f"  Remaining ignoresSafeArea: {l.strip()}")
