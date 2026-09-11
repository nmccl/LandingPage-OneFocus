#!/usr/bin/env python3
"""
Patch iOSAccountSettingsView to add email updates, analytics, biometric toggles.
Uses exact whitespace matching (blank lines between MARK and private var).
"""

import os

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"
ios_acct = f"{BASE}/Views/iOS/Tabs/iOSAccountSettingsView.swift"

def patch(path, find, replace):
    with open(path) as f:
        src = f.read()
    if find not in src:
        print(f"⚠️  Pattern not found: {find[:100]!r}")
        return False
    new = src.replace(find, replace, 1)
    with open(path, 'w') as f:
        f.write(new)
    print(f"✅ Patched: {os.path.basename(path)}")
    return True

# ─── 1. Add require auth + biometric toggles to securityCard ─────────────────
patch(ios_acct,
    '    // MARK: - Security Card\n\n    private var securityCard: some View {\n        iOSSettingsCard {\n            VStack(alignment: .leading, spacing: AppConstants.Spacing.md) {\n                iOSSettingsCardHeader(icon: "lock.fill", title: "Security", iconColor: AppConstants.Colors.textSecondary)',
    '''    // MARK: - Security Card

    private var securityCard: some View {
        iOSSettingsCard {
            VStack(alignment: .leading, spacing: AppConstants.Spacing.md) {
                iOSSettingsCardHeader(icon: "lock.fill", title: "Security", iconColor: AppConstants.Colors.textSecondary)
                iOSSettingsToggleRow(
                    title: "Require App Lock",
                    subtitle: "Lock OneFocus when you leave the app.",
                    isOn: Binding(
                        get: { userSettings.requireAuth },
                        set: { userSettings.requireAuth = $0 }
                    )
                )
                Divider().background(AppConstants.Colors.divider)
                iOSSettingsToggleRow(
                    title: "Biometric Unlock",
                    subtitle: "Use Face ID or Touch ID to unlock.",
                    isOn: Binding(
                        get: { userSettings.biometricUnlock },
                        set: { userSettings.biometricUnlock = $0 }
                    )
                )
                .disabled(!userSettings.requireAuth)
                .opacity(userSettings.requireAuth ? 1 : 0.55)
                Divider().background(AppConstants.Colors.divider)'''
)

# ─── 2. Add email updates + analytics to preferencesCard ─────────────────────
patch(ios_acct,
    '    // MARK: - Preferences Card\n\n    private var preferencesCard: some View {\n        iOSSettingsCard {\n            VStack(alignment: .leading, spacing: AppConstants.Spacing.md) {\n                iOSSettingsCardHeader(icon: "gearshape.fill", title: "Preferences", iconColor: AppConstants.Colors.textSecondary)\n                iOSSettingsToggleRow(\n                    title: "Haptic Feedback",\n                    subtitle: "Vibration on interactions",\n                    isOn: Binding(\n                        get: { userSettings.hapticEnabled },\n                        set: { userSettings.hapticEnabled = $0 }\n                    )\n                )\n            }\n        }\n    }',
    '''    // MARK: - Preferences Card

    private var preferencesCard: some View {
        iOSSettingsCard {
            VStack(alignment: .leading, spacing: AppConstants.Spacing.md) {
                iOSSettingsCardHeader(icon: "gearshape.fill", title: "Preferences", iconColor: AppConstants.Colors.textSecondary)
                iOSSettingsToggleRow(
                    title: "Haptic Feedback",
                    subtitle: "Vibration on interactions",
                    isOn: Binding(
                        get: { userSettings.hapticEnabled },
                        set: { userSettings.hapticEnabled = $0 }
                    )
                )
                Divider().background(AppConstants.Colors.divider)
                iOSSettingsToggleRow(
                    title: "Email Updates",
                    subtitle: "Get notified when new releases launch.",
                    isOn: Binding(
                        get: { userSettings.emailUpdates },
                        set: { newVal in
                            userSettings.emailUpdates = newVal
                            guard let email = authManager.currentUser?.email else { return }
                            let name = userSettings.userName
                            _Concurrency.Task {
                                if newVal {
                                    await EmailUpdateService.subscribe(email: email, name: name)
                                } else {
                                    await EmailUpdateService.unsubscribe(email: email)
                                }
                            }
                        }
                    )
                )
                Divider().background(AppConstants.Colors.divider)
                iOSSettingsToggleRow(
                    title: "Analytics",
                    subtitle: "Help improve OneFocus with anonymous usage data.",
                    isOn: Binding(
                        get: { userSettings.analytics },
                        set: { userSettings.analytics = $0 }
                    )
                )
            }
        }
    }'''
)

print("\n✅ iOSAccountSettingsView patched.")
