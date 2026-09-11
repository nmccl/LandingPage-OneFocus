#!/usr/bin/env python3
"""Fix the Draft struct in AccountSettingsView.swift"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"

with open(path, "r") as f:
    content = f.read()

old3 = ('private struct Draft {\n'
        '    var displayName: String\n'
        '    var showNameInMenu: Bool\n'
        '    var requireAuth: Bool\n'
        '    var biometricUnlock: Bool\n'
        '    var emailUpdates: Bool\n'
        '    var analytics: Bool\n'
        '\n'
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
        '\n'
        '    /// Memberwise init used for the initial @State value before onAppear fires.\n'
        '    init(displayName: String, requireAuth: Bool, biometricUnlock: Bool,\n'
        '         emailUpdates: Bool, analytics: Bool) {\n'
        '        self.displayName     = displayName\n'
        '        self.requireAuth     = requireAuth\n'
        '        self.biometricUnlock = biometricUnlock\n'
        '        self.emailUpdates    = emailUpdates\n'
        '        self.analytics       = analytics\n'
        '    }\n'
        '\n'
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
    print("Fix 3 applied: Draft struct updated (removed showNameInMenu, added memberwise init)")
else:
    print("Fix 3 FAILED: anchor not found")
    # Show lines around the struct for debugging
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if 'struct Draft' in line:
            start = max(0, i-1)
            end = min(len(lines), i+22)
            for j, l in enumerate(lines[start:end], start=start+1):
                print(f"  {j}: {repr(l)}")
            break

with open(path, "w") as f:
    f.write(content)
print("Done")
