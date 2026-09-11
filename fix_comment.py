path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSQuickNotesView.swift'
with open(path, 'r') as f:
    lines = f.readlines()
lines[458] = '            // Must set an explicit frame so iOS reserves space above the keyboard.\n'
with open(path, 'w') as f:
    f.writelines(lines)
print('fixed')
