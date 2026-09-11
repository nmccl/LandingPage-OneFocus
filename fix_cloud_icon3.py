#!/usr/bin/env python3
path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/MainView.swift"
with open(path) as f:
    lines = f.readlines()

# Find the ToolbarItem line
start = None
for i, line in enumerate(lines):
    if "ToolbarItem(placement: .primaryAction)" in line:
        start = i
        break

if start is None:
    print("ERROR: ToolbarItem not found")
    exit(1)

print(f"ToolbarItem starts at line {start+1}: {lines[start].rstrip()}")

# Find closing brace by counting braces
depth = 0
end = None
for i in range(start, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if depth == 0:
        end = i
        break

print(f"ToolbarItem ends at line {end+1}: {lines[end].rstrip()}")

new_block = (
    "            ToolbarItem(placement: .primaryAction) {\n"
    "                // Pro users: ZStack with .onTapGesture + .popover (popover must\n"
    "                // be on the label view, not a Button, to avoid immediate dismiss).\n"
    "                // Free users: plain Button to avoid the re-render loop that\n"
    "                // .onTapGesture + .sheet causes.\n"
    "                if proAccess.isProUser {\n"
    "                    ZStack {\n"
    "                        Circle()\n"
    "                            .fill(AppConstants.Colors.backgroundSecondary)\n"
    "                            .frame(width: 45, height: 28)\n"
    "                        if cloudSync.isSyncing {\n"
    "                            ProgressView()\n"
    "                                .controlSize(.mini)\n"
    "                                .scaleEffect(0.8)\n"
    "                        } else {\n"
    "                            Image(systemName: cloudSyncIcon)\n"
    "                                .font(.system(size: 13, weight: .medium))\n"
    "                                .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                        }\n"
    "                        if cloudSync.isSyncEnabled && !cloudSync.isSyncing {\n"
    "                            Circle()\n"
    "                                .fill(cloudSyncDotColor)\n"
    "                                .frame(width: 7, height: 7)\n"
    "                                .offset(x: 7, y: -7)\n"
    "                        }\n"
    "                    }\n"
    "                    .frame(width: 35, height: 28)\n"
    "                    .contentShape(Rectangle())\n"
    "                    .onTapGesture { showingCloudPopover.toggle() }\n"
    '                    .help("Account Sync")\n'
    "                    .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {\n"
    "                        CloudSyncPopover(cloudSync: cloudSync)\n"
    "                            .environmentObject(themeManager)\n"
    "                    }\n"
    "                } else {\n"
    "                    Button {\n"
    "                        showingUpgradeFromSync = true\n"
    "                    } label: {\n"
    "                        ZStack {\n"
    "                            Circle()\n"
    "                                .fill(AppConstants.Colors.backgroundSecondary)\n"
    "                                .frame(width: 45, height: 28)\n"
    '                            Image(systemName: "icloud.slash")\n'
    "                                .font(.system(size: 13, weight: .medium))\n"
    "                                .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                        }\n"
    "                        .frame(width: 35, height: 28)\n"
    "                    }\n"
    "                    .buttonStyle(.plain)\n"
    '                    .help("Upgrade to Pro for sync")\n'
    "                    .sheet(isPresented: $showingUpgradeFromSync) {\n"
    "                        UpgradePromptView(context: .generic)\n"
    "                            .environmentObject(proAccess)\n"
    "                            .environmentObject(storeKit)\n"
    "                    }\n"
    "                }\n"
    "            }\n"
)

new_lines = lines[:start] + [new_block] + lines[end+1:]
with open(path, "w") as f:
    f.writelines(new_lines)

print("Written. Verifying...")
with open(path) as f:
    final = f.read()

checks = [
    "if proAccess.isProUser {",
    "showingUpgradeFromSync = true",
    ".sheet(isPresented: $showingUpgradeFromSync)",
    "Button {",
    "onTapGesture { showingCloudPopover",
    "placement: .primaryAction",
]
for check in checks:
    print(f"  {'OK' if check in final else 'MISSING'}: {check}")

print("Done.")
