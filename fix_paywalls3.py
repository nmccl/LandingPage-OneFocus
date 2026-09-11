#!/usr/bin/env python3
"""Fix remaining iCloud references in HomePage.tsx"""

web_path = "/Users/noahmcclung/Development/Web-Development/OneFocus-LandingPage/src/components/HomePage.tsx"

with open(web_path, "r") as f:
    web = f.read()

# Feature card heading
web = web.replace(
    '<h3 className="text-lg font-medium mb-1">iCloud Sync</h3>',
    '<h3 className="text-lg font-medium mb-1">Account Sync</h3>',
    1
)

# Privacy FAQ answer — this one is about data privacy, keep "iCloud account" as it's accurate for the privacy context
# Actually the app uses Supabase not iCloud — update to be accurate
old_privacy = 'a: "Absolutely. Your notes, tasks, and clipboard history are stored on your device and synced only through your private iCloud account. We never have access to your data. See our Privacy Policy for full details."'
new_privacy = 'a: "Absolutely. Your notes, tasks, and clipboard history are stored on your device and synced only through your private account. We never have access to your data. See our Privacy Policy for full details."'

if old_privacy in web:
    web = web.replace(old_privacy, new_privacy, 1)
    print("✓ Privacy FAQ answer updated")
else:
    print("  (Privacy FAQ not found exactly — skipping)")

with open(web_path, "w") as f:
    f.write(web)

# Final verification
with open(web_path, "r") as f:
    final = f.read()

remaining = [line.strip() for line in final.splitlines() if "iCloud" in line]
if remaining:
    print(f"✗ iCloud still present:")
    for r in remaining:
        print(f"  {r}")
else:
    print("✓ HomePage.tsx — no more iCloud references")

print("Done.")
