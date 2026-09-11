#!/usr/bin/env python3
"""
Fix 'Type of expression is ambiguous without a type annotation' in AccountSettingsView.
The .onChange on ToggleRow confuses the type checker.
Move the email update logic to a Group/VStack-level .onChange instead.
"""

import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"
with open(path) as f:
    src = f.read()

old = '''    private var preferencesCard: some View {
        SettingsCard(title: "Preferences", subtitle: "Small account behaviors") {
            VStack(spacing: AppConstants.Spacing.md) {
                ToggleRow(
                    title: "Email Updates",
                    subtitle: "Receive feature updates and tips.",
                    isOn: $draft.emailUpdates
                )
                .onChange(of: draft.emailUpdates) { (subscribed: Bool) in
                    guard let email = authManager.currentUser?.email else { return }
                    let name = authManager.currentUser?.userMetadata["full_name"] as? String
                    Task {
                        if subscribed {
                            await EmailUpdateService.subscribe(email: email, name: name)
                        } else {
                            await EmailUpdateService.unsubscribe(email: email)
                        }
                    }
                }
                Divider().background(AppConstants.Colors.divider)
                ToggleRow(
                    title: "Analytics",
                    subtitle: "Help improve OneFocus by sending anonymous usage data.",
                    isOn: $draft.analytics
                )
            }
        }
    }'''

new = '''    private var preferencesCard: some View {
        SettingsCard(title: "Preferences", subtitle: "Small account behaviors") {
            VStack(spacing: AppConstants.Spacing.md) {
                ToggleRow(
                    title: "Email Updates",
                    subtitle: "Receive feature updates and tips.",
                    isOn: $draft.emailUpdates
                )
                Divider().background(AppConstants.Colors.divider)
                ToggleRow(
                    title: "Analytics",
                    subtitle: "Help improve OneFocus by sending anonymous usage data.",
                    isOn: $draft.analytics
                )
            }
            .onChange(of: draft.emailUpdates) { subscribed in
                guard let email = authManager.currentUser?.email else { return }
                let name = authManager.currentUser?.userMetadata["full_name"] as? String
                Task {
                    if subscribed {
                        await EmailUpdateService.subscribe(email: email, name: name)
                    } else {
                        await EmailUpdateService.unsubscribe(email: email)
                    }
                }
            }
        }
    }'''

if old in src:
    src = src.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(src)
    print("✅ Fixed preferencesCard in AccountSettingsView.swift")
else:
    print("⚠️  Pattern not found — checking for partial match:")
    idx = src.find("private var preferencesCard")
    if idx != -1:
        print(repr(src[idx:idx+600]))
    sys.exit(1)
