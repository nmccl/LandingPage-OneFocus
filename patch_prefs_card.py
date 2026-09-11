import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSAccountSettingsView.swift"
with open(path) as f:
    src = f.read()

# Find the preferencesCard section and replace it
marker = "    // MARK: - Preferences Card"
idx = src.find(marker)
if idx == -1:
    print("ERROR: MARK not found")
    sys.exit(1)

# Find the end of the preferencesCard (the closing brace before MARK: - Danger Card)
danger_marker = "    // MARK: - Danger Card"
end_idx = src.find(danger_marker, idx)
if end_idx == -1:
    print("ERROR: Danger Card MARK not found")
    sys.exit(1)

old_section = src[idx:end_idx]
print("Old section preview:", repr(old_section[:200]))

new_section = '''    // MARK: - Preferences Card
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
    }
    '''

new_src = src[:idx] + new_section + src[end_idx:]
with open(path, 'w') as f:
    f.write(new_src)
print("SUCCESS: preferencesCard patched")
