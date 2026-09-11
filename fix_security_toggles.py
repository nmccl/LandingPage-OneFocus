#!/usr/bin/env python3
"""
Fix requireAuth and biometricUnlock bugs in AccountSettingsView.swift:
1. Bad @State init creates a keyless UserSettings() - replace with safe defaults
2. Toggles only save on Save button click - add immediate onChange write-through
3. Draft struct cleanup - remove unused showNameInMenu, add memberwise init
4. saveAndClose only needs to save displayName now
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"

with open(path, "r") as f:
    content = f.read()

original_len = len(content)
fixes_applied = 0

# ---------------------------------------------------------------------------
# Fix 1: Replace bad @State draft init
# ---------------------------------------------------------------------------
old1 = '    @State private var draft: Draft = Draft(from: UserSettings()) // Default value, will be updated onAppear'
new1 = '    // Draft seeded with safe defaults; onAppear immediately replaces it with live userSettings values.\n    @State private var draft: Draft = Draft(displayName: "", requireAuth: false, biometricUnlock: false, emailUpdates: false, analytics: true)'
if old1 in content:
    content = content.replace(old1, new1, 1)
    fixes_applied += 1
    print("Fix 1 applied: replaced bad @State draft init")
else:
    print("Fix 1 SKIPPED: anchor not found (may already be fixed)")

# ---------------------------------------------------------------------------
# Fix 2: Add onChange write-through for requireAuth, biometricUnlock, analytics
# ---------------------------------------------------------------------------
old2 = '        .onChange(of: draft.emailUpdates) { newValue in handleEmailUpdates(subscribed: newValue) }'
new2 = ('        .onChange(of: draft.emailUpdates) { newValue in handleEmailUpdates(subscribed: newValue) }\n'
        '        // Write security + preference toggles through to userSettings immediately\n'
        '        // so they persist even if the user closes the panel without clicking Save.\n'
        '        .onChange(of: draft.requireAuth)     { newValue in userSettings.requireAuth     = newValue }\n'
        '        .onChange(of: draft.biometricUnlock) { newValue in userSettings.biometricUnlock = newValue }\n'
        '        .onChange(of: draft.analytics)       { newValue in userSettings.analytics       = newValue }')
if old2 in content:
    content = content.replace(old2, new2, 1)
    fixes_applied += 1
    print("Fix 2 applied: added onChange write-through for toggles")
else:
    print("Fix 2 SKIPPED: anchor not found (may already be fixed)")

# ---------------------------------------------------------------------------
# Fix 3: Replace Draft struct - remove showNameInMenu, add memberwise init
# ---------------------------------------------------------------------------
old3 = ('private struct Draft {\n'
        '    var displayName: String\n'
        '    var showNameInMenu: Bool\n'
        '    var requireAuth: Bool\n'
        '    var biometricUnlock: Bool\n'
        '    var emailUpdates: Bool\n'
        '    var analytics: Bool\n'
        '    init(from settings: UserSettings) {\n'
        '        displayName     = settings.userName\n'
        '        showNameInMenu  = true\n'
        '        requireAuth     = settings.requireAuth\n'
        '        biometricUnlock = settings.biometricUnlock\n'
        '        emailUpdates    = settings.emailUpdates\n'
        '        analytics       = settings.analytics\n'
        '    }\n'
        '}')
new3 = ('private struct Draft {\n'
        '    var displayName: String\n'
        '    var requireAuth: Bool\n'
        '    var biometricUnlock: Bool\n'
        '    var emailUpdates: Bool\n'
        '    var analytics: Bool\n'
        '    /// Memberwise init — used for the initial @State value before onAppear fires.\n'
        '    init(displayName: String, requireAuth: Bool, biometricUnlock: Bool,\n'
        '         emailUpdates: Bool, analytics: Bool) {\n'
        '        self.displayName     = displayName\n'
        '        self.requireAuth     = requireAuth\n'
        '        self.biometricUnlock = biometricUnlock\n'
        '        self.emailUpdates    = emailUpdates\n'
        '        self.analytics       = analytics\n'
        '    }\n'
        '    /// Convenience init that copies live settings into the draft.\n'
        '    init(from settings: UserSettings) {\n'
        '        self.displayName     = settings.userName\n'
        '        self.requireAuth     = settings.requireAuth\n'
        '        self.biometricUnlock = settings.biometricUnlock\n'
        '        self.emailUpdates    = settings.emailUpdates\n'
        '        self.analytics       = settings.analytics\n'
        '    }\n'
        '}')
if old3 in content:
    content = content.replace(old3, new3, 1)
    fixes_applied += 1
    print("Fix 3 applied: updated Draft struct (removed showNameInMenu, added memberwise init)")
else:
    print("Fix 3 SKIPPED: anchor not found (may already be fixed)")

# ---------------------------------------------------------------------------
# Fix 4: Update saveAndClose to only save displayName
# ---------------------------------------------------------------------------
old4 = ('    private func saveAndClose() {\n'
        '        isSaving = true\n'
        '        let trimmed = draft.displayName.trimmingCharacters(in: .whitespacesAndNewlines)\n'
        '        userSettings.userName        = trimmed.isEmpty ? "Friend" : trimmed\n'
        '        userSettings.requireAuth     = draft.requireAuth\n'
        '        userSettings.biometricUnlock = draft.biometricUnlock\n'
        '        userSettings.emailUpdates    = draft.emailUpdates\n'
        '        userSettings.analytics       = draft.analytics\n'
        '        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {\n'
        '            isSaving = false\n'
        '            closePanel()\n'
        '        }\n'
        '    }')
new4 = ('    private func saveAndClose() {\n'
        '        isSaving = true\n'
        '        let trimmed = draft.displayName.trimmingCharacters(in: .whitespacesAndNewlines)\n'
        '        userSettings.userName = trimmed.isEmpty ? "Friend" : trimmed\n'
        '        // requireAuth, biometricUnlock, emailUpdates, and analytics are already\n'
        '        // written through to userSettings live via onChange handlers above.\n'
        '        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {\n'
        '            isSaving = false\n'
        '            closePanel()\n'
        '        }\n'
        '    }')
if old4 in content:
    content = content.replace(old4, new4, 1)
    fixes_applied += 1
    print("Fix 4 applied: saveAndClose now only saves displayName")
else:
    print("Fix 4 SKIPPED: anchor not found (may already be fixed)")

# ---------------------------------------------------------------------------
# Write back
# ---------------------------------------------------------------------------
with open(path, "w") as f:
    f.write(content)

print(f"\nDone. {fixes_applied} fixes applied.")
print(f"File size: {original_len} -> {len(content)} chars")
