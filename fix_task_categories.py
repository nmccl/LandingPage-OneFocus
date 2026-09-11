#!/usr/bin/env python3
"""
Add task categories to all paywall surfaces.
Change "Unlimited tasks, notes & clipboard" to two separate lines:
- "Unlimited tasks with categories"
- "Unlimited notes & clipboard"
"""

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"
WEB  = "/Users/noahmcclung/Development/Web-Development/OneFocus-LandingPage/src/components/HomePage.tsx"

# ─────────────────────────────────────────────────────────────────────────────
# 1. UpgradePromptView.swift
# ─────────────────────────────────────────────────────────────────────────────
upgrade_path = f"{BASE}/Views/Components/UpgradePromptView.swift"
with open(upgrade_path, "r") as f:
    content = f.read()

old = '                    UpgradeFeatureRow(icon: "checklist",           text: "Unlimited tasks, notes & clipboard")'
new = ('                    UpgradeFeatureRow(icon: "checklist",           text: "Unlimited tasks with categories")\n'
       '                    UpgradeFeatureRow(icon: "note.text",           text: "Unlimited notes & clipboard history")')

# Also remove the now-redundant separate notes line
old_notes = '\n                    UpgradeFeatureRow(icon: "note.text",           text: "Notes with rich text & folders")'

if old in content:
    content = content.replace(old, new, 1)
    # Remove the separate notes line that follows (now merged above)
    content = content.replace(old_notes, "", 1)
    with open(upgrade_path, "w") as f:
        f.write(content)
    print("✓ UpgradePromptView.swift updated")
else:
    print("✗ UpgradePromptView.swift — string not found")
    if "Unlimited tasks, notes" in content:
        print("  (partial match found)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. iOSOnboardingView.swift
# ─────────────────────────────────────────────────────────────────────────────
ios_path = f"{BASE}/Views/Auth/iOSOnboardingView.swift"
with open(ios_path, "r") as f:
    content = f.read()

old = '        ("checklist",                       "Unlimited tasks, notes & clipboard"),'
new = ('        ("checklist",                       "Unlimited tasks with categories"),\n'
       '        ("doc.on.clipboard",                "Unlimited notes & clipboard history"),')

# Remove the now-redundant separate notes line
old_notes = '\n        ("note.text",                       "Notes with rich text & folders"),'

if old in content:
    content = content.replace(old, new, 1)
    content = content.replace(old_notes, "", 1)
    with open(ios_path, "w") as f:
        f.write(content)
    print("✓ iOSOnboardingView.swift updated")
else:
    print("✗ iOSOnboardingView.swift — string not found")

# ─────────────────────────────────────────────────────────────────────────────
# 3. OnboardingView.swift (macOS) — Tasks proItems already has "Categories & folders"
#    Just verify it's there
# ─────────────────────────────────────────────────────────────────────────────
mac_path = f"{BASE}/Views/Auth/OnboardingView.swift"
with open(mac_path, "r") as f:
    mac = f.read()

if "Categories & folders" in mac:
    print("✓ OnboardingView.swift — 'Categories & folders' already present in Tasks proItems")
else:
    print("✗ OnboardingView.swift — missing categories")

# ─────────────────────────────────────────────────────────────────────────────
# 4. HomePage.tsx
# ─────────────────────────────────────────────────────────────────────────────
with open(WEB, "r") as f:
    web = f.read()

old = '                "Unlimited tasks, notes & clipboard",'
new = ('                "Unlimited tasks with categories",\n'
       '                "Unlimited notes & clipboard history",')

# Remove the now-redundant notes line
old_notes = '\n                "Notes with rich text & folders",'

if old in web:
    web = web.replace(old, new, 1)
    web = web.replace(old_notes, "", 1)
    with open(WEB, "w") as f:
        f.write(web)
    print("✓ HomePage.tsx updated")
else:
    print("✗ HomePage.tsx — string not found")

# Also update the FAQ answer
old_faq = '"Pro gives you unlimited focus sessions with custom durations, unlimited tasks, notes, and clipboard history, rich text notes with folders, clipboard favorites, full statistics and streak tracking, custom themes, account sync across devices, menu bar mode, and global keyboard shortcuts."'
new_faq = '"Pro gives you unlimited focus sessions with custom durations, unlimited tasks with categories, unlimited notes and clipboard history, rich text notes with folders, clipboard favorites, full statistics and streak tracking, custom themes, account sync across devices, menu bar mode, and global keyboard shortcuts."'

with open(WEB, "r") as f:
    web = f.read()
if old_faq in web:
    web = web.replace(old_faq, new_faq, 1)
    with open(WEB, "w") as f:
        f.write(web)
    print("✓ HomePage.tsx FAQ answer updated")
else:
    print("  (FAQ answer not found — may already be updated)")

print("\nDone.")
