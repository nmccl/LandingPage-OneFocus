#!/usr/bin/env python3
"""
Add a minimal back arrow to LandscapeFocusOverlay so iPad users in landscape
can navigate back to Home without rotating the device.

Changes:
1. iOSMainView.swift  — pass selectedTab binding into iOSFocusView
2. iOSFocusView.swift — add @Binding selectedTab to iOSFocusView and
                        LandscapeFocusOverlay, add back arrow button
"""

# ─── 1. iOSMainView.swift ─────────────────────────────────────────────────────
main_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/iOSMainView.swift"

with open(main_path, "r") as f:
    src = f.read()

old_focus_tab = '            Tab("Focus", systemImage: "brain.head.profile", value: IOSNavigationTab.focus) {\n                iOSFocusView()\n            }'
new_focus_tab = '            Tab("Focus", systemImage: "brain.head.profile", value: IOSNavigationTab.focus) {\n                iOSFocusView(selectedTab: $selectedTab)\n            }'

if old_focus_tab in src:
    src = src.replace(old_focus_tab, new_focus_tab)
    with open(main_path, "w") as f:
        f.write(src)
    print("✓ iOSMainView.swift: selectedTab binding passed to iOSFocusView")
else:
    print("✗ iOSMainView.swift: pattern not found")

# ─── 2. iOSFocusView.swift ────────────────────────────────────────────────────
focus_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"

with open(focus_path, "r") as f:
    src2 = f.read()

# 2a. Add @Binding selectedTab to iOSFocusView struct
old_focus_struct = """struct iOSFocusView: View {
    @EnvironmentObject private var focusTimer:     FocusTimerManager
    @EnvironmentObject private var userSettings:   UserSettings
    @EnvironmentObject private var historyManager: HistoryManager
    @EnvironmentObject private var proAccess:      ProAccessManager
    @EnvironmentObject private var themeManager:   ThemeManager
    @State private var showingSessionCapAlert = false
    @State private var showingUpgradeSheet    = false"""

new_focus_struct = """struct iOSFocusView: View {
    @Binding var selectedTab: IOSNavigationTab
    @EnvironmentObject private var focusTimer:     FocusTimerManager
    @EnvironmentObject private var userSettings:   UserSettings
    @EnvironmentObject private var historyManager: HistoryManager
    @EnvironmentObject private var proAccess:      ProAccessManager
    @EnvironmentObject private var themeManager:   ThemeManager
    @State private var showingSessionCapAlert = false
    @State private var showingUpgradeSheet    = false"""

if old_focus_struct in src2:
    src2 = src2.replace(old_focus_struct, new_focus_struct)
    print("✓ iOSFocusView: @Binding selectedTab added to iOSFocusView")
else:
    print("✗ iOSFocusView: iOSFocusView struct header pattern not found")

# 2b. Pass selectedTab into LandscapeFocusOverlay call
old_landscape_call = """                    LandscapeFocusOverlay(
                        dailyCapReached: dailyCapReached,
                        showingSessionCapAlert: $showingSessionCapAlert,
                        showingUpgradeSheet: $showingUpgradeSheet
                    )"""

new_landscape_call = """                    LandscapeFocusOverlay(
                        selectedTab: $selectedTab,
                        dailyCapReached: dailyCapReached,
                        showingSessionCapAlert: $showingSessionCapAlert,
                        showingUpgradeSheet: $showingUpgradeSheet
                    )"""

if old_landscape_call in src2:
    src2 = src2.replace(old_landscape_call, new_landscape_call)
    print("✓ iOSFocusView: selectedTab passed to LandscapeFocusOverlay")
else:
    print("✗ iOSFocusView: LandscapeFocusOverlay call pattern not found")

# 2c. Add @Binding selectedTab to LandscapeFocusOverlay struct and add back arrow
old_overlay_struct = """private struct LandscapeFocusOverlay: View {
    @EnvironmentObject private var focusTimer:   FocusTimerManager
    @EnvironmentObject private var userSettings: UserSettings
    let dailyCapReached: Bool
    @Binding var showingSessionCapAlert: Bool
    @Binding var showingUpgradeSheet: Bool
    // Subtle pulse when running
    @State private var pulse = false
    var body: some View {
        GeometryReader { geo in
            ZStack {
                Color.black.ignoresSafeArea()
                VStack(spacing: 0) {
                    Spacer()"""

new_overlay_struct = """private struct LandscapeFocusOverlay: View {
    @EnvironmentObject private var focusTimer:   FocusTimerManager
    @EnvironmentObject private var userSettings: UserSettings
    @Binding var selectedTab: IOSNavigationTab
    let dailyCapReached: Bool
    @Binding var showingSessionCapAlert: Bool
    @Binding var showingUpgradeSheet: Bool
    // Subtle pulse when running
    @State private var pulse = false
    var body: some View {
        GeometryReader { geo in
            ZStack {
                Color.black.ignoresSafeArea()
                // Minimal back arrow — top-left, so iPad landscape users can
                // navigate away without rotating the device.
                VStack {
                    HStack {
                        Button {
                            selectedTab = .home
                        } label: {
                            Image(systemName: "chevron.left")
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(.white.opacity(0.45))
                                .frame(width: 44, height: 44)
                        }
                        .buttonStyle(.plain)
                        .padding(.leading, 20)
                        .padding(.top, 16)
                        Spacer()
                    }
                    Spacer()
                }
                VStack(spacing: 0) {
                    Spacer()"""

if old_overlay_struct in src2:
    src2 = src2.replace(old_overlay_struct, new_overlay_struct)
    print("✓ iOSFocusView: back arrow added to LandscapeFocusOverlay")
else:
    print("✗ iOSFocusView: LandscapeFocusOverlay struct pattern not found")

with open(focus_path, "w") as f:
    src2_written = src2
    f.write(src2_written)
print("✓ iOSFocusView.swift written")
