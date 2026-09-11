path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"
with open(path) as f:
    content = f.read()

# The fix: hide the toolbar only when the landscape overlay is ACTUALLY showing
# i.e. landscape AND not dismissed — same condition as the overlay itself
old = """        .toolbar(isLandscape ? .hidden : .visible, for: .tabBar)
        .toolbarVisibility(isLandscape ? .hidden : .visible, for: .tabBar)"""

new = """        // Hide the tab bar only while the landscape focus overlay is actually
        // visible. When the user dismisses it (userDismissedLandscape = true),
        // the overlay is gone and the tab bar must be restored — even if the
        // device is still in landscape (e.g. iPad in a keyboard case).
        .toolbar((isLandscape && !userDismissedLandscape) ? .hidden : .visible, for: .tabBar)
        .toolbarVisibility((isLandscape && !userDismissedLandscape) ? .hidden : .visible, for: .tabBar)"""

if old in content:
    content = content.replace(old, new, 1)
    print("✓ Fixed toolbar visibility to use overlay state, not just isLandscape")
else:
    print("✗ Could not find toolbar lines")

with open(path, 'w') as f:
    f.write(content)
print("Done")
