path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/MainView.swift"
with open(path, 'r') as f:
    content = f.read()

# 1. Remove the two .frame lines from sidebarContent and add .navigationSplitViewColumnWidth there instead
old = '        .frame(maxWidth: 260, alignment: .leading)\n        .frame(minWidth: 220, idealWidth: 240, maxWidth: 260)\n        .background(AppConstants.Colors.backgroundSecondary)'
new = '        .background(AppConstants.Colors.backgroundSecondary)\n        .navigationSplitViewColumnWidth(min: 220, ideal: 240, max: 260)'
if old in content:
    content = content.replace(old, new, 1)
    print("Moved column width to sidebarContent")
else:
    print("Could not find sidebarContent .frame block")

# 2. Remove the duplicate .navigationSplitViewColumnWidth from the outer NavigationSplitView
old2 = '        .navigationSplitViewColumnWidth(min: 220, ideal: 240, max: 260)\n        .navigationSplitViewStyle(.balanced)'
new2 = '        .navigationSplitViewStyle(.balanced)'
if old2 in content:
    content = content.replace(old2, new2, 1)
    print("Removed duplicate from NavigationSplitView")
else:
    print("Could not find duplicate on NavigationSplitView (may already be removed)")

with open(path, 'w') as f:
    f.write(content)
print("Done")
