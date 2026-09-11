#!/usr/bin/env python3
"""
Fix 'Type of expression is ambiguous without a type annotation' by:
1. Removing the .onChange from inside SettingsCard's ViewBuilder closure
2. Adding a private func handleEmailUpdates(subscribed:) to the view
3. Adding .onChange(of: draft.emailUpdates) on the ZStack (top-level body)
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"
with open(path) as f:
    src = f.read()

# ── Step 1: Strip the .onChange from the VStack inside SettingsCard ──────────
old_prefs = '''    private var preferencesCard: some View {
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

new_prefs = '''    private var preferencesCard: some View {
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
        }
    }

    private func handleEmailUpdates(subscribed: Bool) {
        guard let email = authManager.currentUser?.email else { return }
        let name = authManager.currentUser?.userMetadata["full_name"] as? String
        Task {
            if subscribed {
                await EmailUpdateService.subscribe(email: email, name: name)
            } else {
                await EmailUpdateService.unsubscribe(email: email)
            }
        }
    }'''

if old_prefs in src:
    src = src.replace(old_prefs, new_prefs, 1)
    print("✅ Step 1: Removed .onChange from preferencesCard VStack")
else:
    # Fallback: find by line range
    lines = src.split('\n')
    start = None
    end = None
    for i, line in enumerate(lines):
        if 'private var preferencesCard' in line:
            start = i
        if start is not None and '// MARK: - Danger Card' in line:
            end = i
            break
    if start is not None and end is not None:
        new_block = '''    private var preferencesCard: some View {
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
        }
    }

    private func handleEmailUpdates(subscribed: Bool) {
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
    '''
        lines = lines[:start] + [new_block] + lines[end:]
        src = '\n'.join(lines)
        print("✅ Step 1 (fallback): Replaced preferencesCard section by line range")
    else:
        print(f"❌ Could not find preferencesCard section. start={start}, end={end}")
        exit(1)

# ── Step 2: Add .onChange(of: draft.emailUpdates) on the ZStack ─────────────
# Insert after the .onAppear line
old_onappear = '        .onAppear { draft = Draft(from: userSettings) }'
new_onappear = '''        .onAppear { draft = Draft(from: userSettings) }
        .onChange(of: draft.emailUpdates) { handleEmailUpdates(subscribed: $0) }'''

if old_onappear in src:
    src = src.replace(old_onappear, new_onappear, 1)
    print("✅ Step 2: Added .onChange(of: draft.emailUpdates) on ZStack")
else:
    print("⚠️  Could not find .onAppear line for Step 2 — checking:")
    idx = src.find('.onAppear')
    print(repr(src[idx:idx+100]))

with open(path, 'w') as f:
    f.write(src)
print("✅ Done — AccountSettingsView.swift updated")
