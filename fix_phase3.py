#!/usr/bin/env python3
"""Phase 3: APS entitlement → production, onboarding copy, iOSHomeView stub text."""

# ── 1. APS entitlement: development → production ─────────────────────────────
ent_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/OneFocus.entitlements"
with open(ent_path, "r") as f:
    ent = f.read()
if "<string>development</string>" in ent:
    ent = ent.replace("<string>development</string>", "<string>production</string>", 1)
    with open(ent_path, "w") as f:
        f.write(ent)
    print("✅ APS entitlement → production")
else:
    print("ℹ️  APS already production or not found")

# ── 2. OnboardingView: remove "(coming soon)" from iPhone & iPad line ─────────
onboard_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/OnboardingView.swift"
with open(onboard_path, "r") as f:
    onboard = f.read()
if '"iPhone & iPad (coming soon)"' in onboard:
    onboard = onboard.replace('"iPhone & iPad (coming soon)"', '"iPhone & iPad"')
    with open(onboard_path, "w") as f:
        f.write(onboard)
    print("✅ Onboarding copy updated (removed 'coming soon')")
else:
    print("ℹ️  Onboarding copy already updated")

# ── 3. iOSHomeView: remove "Task creation coming soon" placeholder text ───────
home_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSHomeView.swift"
with open(home_path, "r") as f:
    home = f.read()
if 'Text("Task creation coming soon")' in home:
    home = home.replace('Text("Task creation coming soon")', 'Text("Tap + to add your first task")')
    with open(home_path, "w") as f:
        f.write(home)
    print("✅ iOSHomeView placeholder text updated")
else:
    print("ℹ️  iOSHomeView placeholder already updated")

print("\nPhase 3 complete.")
