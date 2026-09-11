#!/usr/bin/env python3
"""Fix AnalyticsService save/load/clear + wire configure into AuthManager finishSignIn"""

# ── AnalyticsService ──────────────────────────────────────────────────────────
path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/AnalyticsService.swift"
with open(path, "r") as f:
    src = f.read()

# Replace the hardcoded "analytics.events" key in saveEvent
src = src.replace(
    'UserDefaults.standard.set(data, forKey: "analytics.events")',
    'UserDefaults.standard.set(data, forKey: storageKey)'
)
src = src.replace(
    'UserDefaults.standard.data(forKey: "analytics.events")',
    'UserDefaults.standard.data(forKey: storageKey)'
)

# Add removeObject to clearEvents
old_clear = "    func clearEvents() {\n        events.removeAll()\n    }"
new_clear = "    func clearEvents() {\n        events.removeAll()\n        UserDefaults.standard.removeObject(forKey: storageKey)\n    }"
if old_clear in src:
    src = src.replace(old_clear, new_clear)
    print("patched clearEvents")
else:
    print("clearEvents not found")

# Remove the loadEvents() call from init (now loaded lazily)
src = src.replace(
    "    private init() {\n        // Events loaded lazily via configure(userID:) after sign-in.\n    }",
    "    private init() {\n        // Events loaded lazily via configure(userID:) after sign-in.\n    }"
)

# Also remove old init that still calls loadEvents if props patch left it
src = src.replace(
    "    private init() {\n        loadEvents()\n    }",
    "    private init() {\n        // Events loaded lazily via configure(userID:) after sign-in.\n    }"
)

with open(path, "w") as f:
    f.write(src)
print("AnalyticsService patched")

# ── AuthManager: wire configure into finishSignIn ─────────────────────────────
auth_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/AuthManager.swift"
with open(auth_path, "r") as f:
    auth = f.read()

target = "    private func finishSignIn(user: User) async {"
if target in auth and "AnalyticsService.shared.configure" not in auth:
    auth = auth.replace(
        target,
        target + "\n        AnalyticsService.shared.configure(userID: user.id.uuidString)"
    )
    with open(auth_path, "w") as f:
        f.write(auth)
    print("finishSignIn patched")
elif "AnalyticsService.shared.configure" in auth:
    print("finishSignIn already patched")
else:
    print("finishSignIn target NOT FOUND")

print("Done.")
