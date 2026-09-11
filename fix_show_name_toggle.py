#!/usr/bin/env python3
"""Remove the dead showNameInMenu toggle from AccountSettingsView profileCard"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"

with open(path, "r") as f:
    content = f.read()

# There's a blank line before the Divider and before the ToggleRow
old_toggle = ('                Divider().background(AppConstants.Colors.divider)\n'
              '\n'
              '                ToggleRow(\n'
              '                    title: "Show in Profile Menu",\n'
              '                    subtitle: "Display your name in the bottom profile menu.",\n'
              '                    isOn: $draft.showNameInMenu\n'
              '                )\n')

if old_toggle in content:
    content = content.replace(old_toggle, '', 1)
    print("Removed dead showNameInMenu toggle row")
else:
    print("showNameInMenu toggle not found - checking for it...")
    idx = content.find('showNameInMenu')
    if idx >= 0:
        print(f"Found at char {idx}:")
        print(repr(content[max(0,idx-200):idx+200]))
    else:
        print("showNameInMenu not found at all in file")

with open(path, "w") as f:
    f.write(content)
print("Done")
