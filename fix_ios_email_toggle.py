#!/usr/bin/env python3
path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSAccountSettingsView.swift'
with open(path) as f:
    src = f.read()

# Step 1: Replace the broken Binding-with-_Concurrency.Task email toggle
# Find it by searching for the key marker lines
import re

# Replace the entire iOSSettingsToggleRow for Email Updates (which has the bad Binding)
# Use a regex to find it regardless of exact whitespace
pattern = r'iOSSettingsToggleRow\(\s*title:\s*"Email Updates".*?isOn:.*?\)\s*\)'
replacement = '''iOSSettingsToggleRow(
                    title: "Email Updates",
                    subtitle: "Get notified when new releases launch.",
                    isOn: $userSettings.emailUpdates
                )'''
new_src, count = re.subn(pattern, replacement, src, count=1, flags=re.DOTALL)
if count:
    src = new_src
    print("Step 1: Replaced email updates toggle")
else:
    print("Step 1: Regex pattern not found")
    idx = src.find('Email Updates')
    print(repr(src[max(0,idx-50):idx+300]))

# Step 2: Add .onChange on the NavigationStack after .onAppear
old_appear = '            .onAppear { draftName = userSettings.userName }'
new_appear = '''            .onAppear { draftName = userSettings.userName }
            .onChange(of: userSettings.emailUpdates) { newValue in
                guard let email = authManager.currentUser?.email else { return }
                let name: String? = userSettings.userName.isEmpty ? nil : userSettings.userName
                Task {
                    if newValue {
                        await EmailUpdateService.subscribe(email: email, name: name)
                    } else {
                        await EmailUpdateService.unsubscribe(email: email)
                    }
                }
            }'''

if old_appear in src:
    src = src.replace(old_appear, new_appear, 1)
    print("Step 2: Added onChange on NavigationStack")
else:
    print("Step 2: onAppear pattern not found")
    idx = src.find('.onAppear')
    print(repr(src[idx:idx+80]))

with open(path, 'w') as f:
    f.write(src)
print("Done")
