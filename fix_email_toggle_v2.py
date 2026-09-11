#!/usr/bin/env python3
"""
Fix the preferencesCard in AccountSettingsView by replacing the section
between the MARK comment and the dangerCard MARK using line-range replacement.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"
with open(path) as f:
    lines = f.readlines()

# Find start: line containing "private var preferencesCard"
start = None
end = None
for i, line in enumerate(lines):
    if 'private var preferencesCard' in line:
        start = i
    if start is not None and '// MARK: - Danger Card' in line:
        end = i
        break

if start is None or end is None:
    print(f"ERROR: Could not find section. start={start}, end={end}")
    exit(1)

print(f"Replacing lines {start+1}–{end} (preferencesCard section)")

new_section = '''    private var preferencesCard: some View {
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
    }
    '''

new_lines = lines[:start] + [new_section] + lines[end:]
with open(path, 'w') as f:
    f.writelines(new_lines)
print("✅ preferencesCard fixed in AccountSettingsView.swift")
