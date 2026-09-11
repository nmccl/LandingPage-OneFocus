#!/usr/bin/env python3
"""
Add a minimal back arrow to LandscapeFocusOverlay (corrected whitespace patterns).
"""

focus_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"

with open(focus_path, "r") as f:
    src = f.read()

# ─── Fix 1: Add @Binding selectedTab to iOSFocusView ─────────────────────────
old1 = "struct iOSFocusView: View {\n    @EnvironmentObject private var focusTimer:     FocusTimerManager\n    @EnvironmentObject private var userSettings:   UserSettings\n    @EnvironmentObject private var historyManager: HistoryManager\n    @EnvironmentObject private var proAccess:      ProAccessManager\n    @EnvironmentObject private var themeManager:   ThemeManager\n\n    @State private var showingSessionCapAlert = false\n    @State private var showingUpgradeSheet    = false"

new1 = "struct iOSFocusView: View {\n    @Binding var selectedTab: IOSNavigationTab\n    @EnvironmentObject private var focusTimer:     FocusTimerManager\n    @EnvironmentObject private var userSettings:   UserSettings\n    @EnvironmentObject private var historyManager: HistoryManager\n    @EnvironmentObject private var proAccess:      ProAccessManager\n    @EnvironmentObject private var themeManager:   ThemeManager\n\n    @State private var showingSessionCapAlert = false\n    @State private var showingUpgradeSheet    = false"

if old1 in src:
    src = src.replace(old1, new1)
    print("✓ iOSFocusView: @Binding selectedTab added to iOSFocusView")
else:
    print("✗ iOSFocusView struct header not found — check manually")

# ─── Fix 2: Add @Binding selectedTab to LandscapeFocusOverlay ────────────────
old2 = "private struct LandscapeFocusOverlay: View {\n    @EnvironmentObject private var focusTimer:   FocusTimerManager\n    @EnvironmentObject private var userSettings: UserSettings\n\n    let dailyCapReached: Bool\n    @Binding var showingSessionCapAlert: Bool\n    @Binding var showingUpgradeSheet: Bool\n\n    // Subtle pulse when running\n    @State private var pulse = false\n\n    var body: some View {\n        GeometryReader { geo in\n            ZStack {\n                Color.black.ignoresSafeArea()"

new2 = "private struct LandscapeFocusOverlay: View {\n    @EnvironmentObject private var focusTimer:   FocusTimerManager\n    @EnvironmentObject private var userSettings: UserSettings\n    @Binding var selectedTab: IOSNavigationTab\n\n    let dailyCapReached: Bool\n    @Binding var showingSessionCapAlert: Bool\n    @Binding var showingUpgradeSheet: Bool\n\n    // Subtle pulse when running\n    @State private var pulse = false\n\n    var body: some View {\n        GeometryReader { geo in\n            ZStack {\n                Color.black.ignoresSafeArea()\n                // Minimal back arrow — top-left corner so iPad landscape users\n                // can navigate away without rotating the device.\n                VStack {\n                    HStack {\n                        Button {\n                            selectedTab = .home\n                        } label: {\n                            Image(systemName: \"chevron.left\")\n                                .font(.system(size: 16, weight: .medium))\n                                .foregroundColor(.white.opacity(0.45))\n                                .frame(width: 44, height: 44)\n                        }\n                        .buttonStyle(.plain)\n                        .padding(.leading, 20)\n                        .padding(.top, 16)\n                        Spacer()\n                    }\n                    Spacer()\n                }"

if old2 in src:
    src = src.replace(old2, new2)
    print("✓ LandscapeFocusOverlay: @Binding + back arrow added")
else:
    print("✗ LandscapeFocusOverlay struct pattern not found — check manually")

with open(focus_path, "w") as f:
    f.write(src)
print("✓ iOSFocusView.swift written")
