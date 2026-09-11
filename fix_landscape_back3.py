#!/usr/bin/env python3
"""
Fix the landscape back arrow behavior:
- Add @State private var userDismissedLandscape = false to iOSFocusView
- Change the landscape condition to: landscape && !userDismissedLandscape
- Reset userDismissedLandscape to false when orientation changes back to portrait
  (so next landscape entry re-triggers the overlay)
- Change the back arrow action from selectedTab = .home to userDismissedLandscape = true
- Remove the now-unneeded @Binding selectedTab from iOSFocusView and LandscapeFocusOverlay
  (and revert iOSMainView to iOSFocusView() without the binding)
"""

focus_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"
main_path  = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/iOSMainView.swift"

# ─── iOSMainView: revert to no binding ───────────────────────────────────────
with open(main_path, "r") as f:
    msrc = f.read()

msrc = msrc.replace(
    "iOSFocusView(selectedTab: $selectedTab)",
    "iOSFocusView()"
)
with open(main_path, "w") as f:
    f.write(msrc)
print("✓ iOSMainView.swift: reverted to iOSFocusView() (no binding needed)")

# ─── iOSFocusView ─────────────────────────────────────────────────────────────
with open(focus_path, "r") as f:
    src = f.read()

# 1. Remove @Binding selectedTab from iOSFocusView struct
src = src.replace(
    "struct iOSFocusView: View {\n    @Binding var selectedTab: IOSNavigationTab\n    @EnvironmentObject private var focusTimer:",
    "struct iOSFocusView: View {\n    @EnvironmentObject private var focusTimer:"
)

# 2. Add userDismissedLandscape state after showingUpgradeSheet
src = src.replace(
    "    @State private var showingSessionCapAlert = false\n    @State private var showingUpgradeSheet    = false",
    "    @State private var showingSessionCapAlert    = false\n    @State private var showingUpgradeSheet      = false\n    @State private var userDismissedLandscape   = false"
)

# 3. Change the landscape condition to include !userDismissedLandscape
src = src.replace(
    "                if landscape {\n                    LandscapeFocusOverlay(\n                        selectedTab: $selectedTab,\n                        dailyCapReached: dailyCapReached,",
    "                if landscape && !userDismissedLandscape {\n                    LandscapeFocusOverlay(\n                        onDismiss: { userDismissedLandscape = true },\n                        dailyCapReached: dailyCapReached,"
)

# 4. Reset userDismissedLandscape when orientation goes back to portrait
# The existing .onChange(of: landscape) sets isLandscape — extend it
src = src.replace(
    "            .onChange(of: landscape) { isLandscape = $0 }",
    "            .onChange(of: landscape) { newValue in\n                isLandscape = newValue\n                // When the device returns to portrait, reset the dismissed\n                // flag so the overlay re-triggers on next landscape entry.\n                if !newValue { userDismissedLandscape = false }\n            }"
)

# 5. Remove @Binding selectedTab from LandscapeFocusOverlay and replace with onDismiss closure
src = src.replace(
    "private struct LandscapeFocusOverlay: View {\n    @EnvironmentObject private var focusTimer:   FocusTimerManager\n    @EnvironmentObject private var userSettings: UserSettings\n    @Binding var selectedTab: IOSNavigationTab",
    "private struct LandscapeFocusOverlay: View {\n    @EnvironmentObject private var focusTimer:   FocusTimerManager\n    @EnvironmentObject private var userSettings: UserSettings\n    let onDismiss: () -> Void"
)

# 6. Change the back arrow action from selectedTab = .home to onDismiss()
src = src.replace(
    "                        Button {\n                            selectedTab = .home\n                        } label: {",
    "                        Button {\n                            onDismiss()\n                        } label: {"
)

with open(focus_path, "w") as f:
    f.write(src)
print("✓ iOSFocusView.swift: userDismissedLandscape flag + onDismiss closure applied")

# ─── Verify ───────────────────────────────────────────────────────────────────
with open(focus_path, "r") as f:
    verify = f.read()

checks = [
    ("userDismissedLandscape" in verify,          "userDismissedLandscape state exists"),
    ("onDismiss: { userDismissedLandscape" in verify, "onDismiss passed to overlay"),
    ("let onDismiss: () -> Void" in verify,        "onDismiss closure in overlay"),
    ("onDismiss()" in verify,                      "onDismiss() called in back arrow"),
    ("if !newValue { userDismissedLandscape = false }" in verify, "reset on portrait"),
    ("@Binding var selectedTab" not in verify,     "no leftover selectedTab binding"),
]
for ok, label in checks:
    print(f"{'✓' if ok else '✗'} {label}")
