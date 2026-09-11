#!/usr/bin/env python3
"""
Fix remaining issues:
1. OnboardingView.swift — remove the duplicate old featureGroups block (lines 342-416)
2. HomePage.tsx — fix two FAQ answers still mentioning "iCloud sync"
   and one feature description mentioning "menu bar widget"
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. OnboardingView.swift — remove duplicate old block
# ─────────────────────────────────────────────────────────────────────────────
mac_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/OnboardingView.swift"

with open(mac_path, "r") as f:
    lines = f.readlines()

# The duplicate starts at "    ] = [" (line 342, 0-indexed = 341)
# and ends at "    ]" just before "    var body: some View {" (line 416, 0-indexed = 415)
# We want to remove lines 342..416 inclusive (0-indexed 341..415)

# Find the "    ] = [" line
dup_start = None
for i, line in enumerate(lines):
    if line.rstrip() == "    ] = [":
        dup_start = i
        break

# Find the closing "]" of the duplicate block — it's the "    ]" just before
# the second "    var body: some View {"
dup_end = None
for i in range(dup_start + 1, len(lines)):
    if lines[i].strip() == "var body: some View {" or lines[i].rstrip() == "    var body: some View {":
        # The "]" is the line before this
        dup_end = i - 1
        break

if dup_start is not None and dup_end is not None:
    print(f"  Removing lines {dup_start+1}–{dup_end+1} (duplicate old featureGroups block)")
    new_lines = lines[:dup_start] + lines[dup_end+1:]
    with open(mac_path, "w") as f:
        f.writelines(new_lines)
    print("✓ OnboardingView.swift duplicate block removed")
else:
    print(f"✗ Could not locate duplicate block (dup_start={dup_start}, dup_end={dup_end})")

# Verify
with open(mac_path, "r") as f:
    content = f.read()
if "Basic functionality" in content or "Priority levels" in content or "Resets on quit" in content:
    print("✗ Old stale strings still present in OnboardingView.swift")
else:
    print("✓ OnboardingView.swift clean — no stale strings")

# ─────────────────────────────────────────────────────────────────────────────
# 2. HomePage.tsx — fix FAQ answers and feature description
# ─────────────────────────────────────────────────────────────────────────────
web_path = "/Users/noahmcclung/Development/Web-Development/OneFocus-LandingPage/src/components/HomePage.tsx"

with open(web_path, "r") as f:
    web = f.read()

# FAQ: "one subscription covers both macOS and iOS. iCloud sync keeps..."
old1 = "Yes. OneFocus is a universal purchase — one subscription covers both macOS and iOS. iCloud sync keeps everything in perfect sync across your devices automatically."
new1 = "Yes. OneFocus is a universal purchase — one subscription covers both macOS and iOS. Account sync keeps everything in perfect sync across your devices automatically."

# FAQ: "iCloud sync runs in the background when you have a connection..."
old2 = "Yes. All your data is stored locally first. iCloud sync runs in the background when you have a connection, so OneFocus is fully functional even without internet access."
new2 = "Yes. All your data is stored locally first. Account sync runs in the background when you have a connection, so OneFocus is fully functional even without internet access."

# Feature description: "menu bar widget"
old3 = "Rich-text notes with a global hotkey or menu bar widget. Write fast, find faster."
new3 = "Rich-text notes with a global hotkey or menu bar mode. Write fast, find faster."

changes = [(old1, new1, "FAQ sync answer 1"), (old2, new2, "FAQ sync answer 2"), (old3, new3, "Notes feature description")]
for old, new, label in changes:
    if old in web:
        web = web.replace(old, new, 1)
        print(f"✓ HomePage.tsx {label} updated")
    else:
        print(f"  (skipped — {label} not found or already updated)")

with open(web_path, "w") as f:
    f.write(web)

# Final check
remaining = []
for term in ["iCloud sync", "menu bar widget", "Priority support", "Data export", "Beta feature", "custom sounds"]:
    if term.lower() in web.lower():
        remaining.append(term)
if remaining:
    print(f"✗ Still present in HomePage.tsx: {remaining}")
else:
    print("✓ HomePage.tsx fully clean")

print("\nAll done.")
