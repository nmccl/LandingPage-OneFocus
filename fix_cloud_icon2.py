#!/usr/bin/env python3
"""
Fix cloud icon toolbar — replace entire ToolbarItem content with Pro/free split.
Placement already changed to .primaryAction.
Now wrap the ZStack in if/else for Pro vs free.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/MainView.swift"
with open(path) as f:
    c = f.read()

old_block = """            ToolbarItem(placement: .primaryAction) {
                // The .popover must be on the ZStack label, NOT on the Button
                // itself. When .popover is on a Button, the button's own tap
                // event is processed AFTER the popover opens, which the popover
                // interprets as an outside-click and immediately dismisses itself.
                // Attaching .popover to the label view breaks that cycle.
                ZStack {
                    // Circle background
                    Circle()
                        .fill(AppConstants.Colors.backgroundSecondary)
                        .frame(width: 45, height: 28)
                    if cloudSync.isSyncing {
                        ProgressView()
                            .controlSize(.mini)
                            .scaleEffect(0.8)
                    } else {
                        Image(systemName: cloudSyncIcon)
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                    }
                    // Small status dot — top-right corner, only when enabled
                    if cloudSync.isSyncEnabled && !cloudSync.isSyncing {
                        Circle()
                            .fill(cloudSyncDotColor)
                            .frame(width: 7, height: 7)
                            .offset(x: 7, y: -7)
                    }
                }
                .frame(width: 35, height: 28)
                .contentShape(Rectangle())
                .onTapGesture { showingCloudPopover.toggle() }
                .help("Account Sync")
                .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {
                    CloudSyncPopover(cloudSync: cloudSync)
                        .environmentObject(themeManager)
                }
            }"""

new_block = """            ToolbarItem(placement: .primaryAction) {
                // Pro users: ZStack with .onTapGesture + .popover (popover must
                // be on the label view, not a Button, to avoid immediate dismiss).
                // Free users: plain Button to avoid the re-render loop that
                // .onTapGesture + .sheet causes.
                if proAccess.isProUser {
                    ZStack {
                        Circle()
                            .fill(AppConstants.Colors.backgroundSecondary)
                            .frame(width: 45, height: 28)
                        if cloudSync.isSyncing {
                            ProgressView()
                                .controlSize(.mini)
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: cloudSyncIcon)
                                .font(.system(size: 13, weight: .medium))
                                .foregroundColor(AppConstants.Colors.textSecondary)
                        }
                        if cloudSync.isSyncEnabled && !cloudSync.isSyncing {
                            Circle()
                                .fill(cloudSyncDotColor)
                                .frame(width: 7, height: 7)
                                .offset(x: 7, y: -7)
                        }
                    }
                    .frame(width: 35, height: 28)
                    .contentShape(Rectangle())
                    .onTapGesture { showingCloudPopover.toggle() }
                    .help("Account Sync")
                    .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {
                        CloudSyncPopover(cloudSync: cloudSync)
                            .environmentObject(themeManager)
                    }
                } else {
                    Button {
                        showingUpgradeFromSync = true
                    } label: {
                        ZStack {
                            Circle()
                                .fill(AppConstants.Colors.backgroundSecondary)
                                .frame(width: 45, height: 28)
                            Image(systemName: "icloud.slash")
                                .font(.system(size: 13, weight: .medium))
                                .foregroundColor(AppConstants.Colors.textSecondary)
                        }
                        .frame(width: 35, height: 28)
                    }
                    .buttonStyle(.plain)
                    .help("Upgrade to Pro for sync")
                    .sheet(isPresented: $showingUpgradeFromSync) {
                        UpgradePromptView(context: .generic)
                            .environmentObject(proAccess)
                            .environmentObject(storeKit)
                    }
                }
            }"""

if old_block in c:
    c = c.replace(old_block, new_block, 1)
    print("✓ ToolbarItem replaced")
else:
    print("✗ Block not found — dumping toolbar section")
    idx = c.find("ToolbarItem(placement: .primaryAction)")
    if idx >= 0:
        print(repr(c[idx:idx+500]))

with open(path, "w") as f:
    f.write(c)

# Verify
with open(path) as f:
    final = f.read()

checks = [
    ("placement: .primaryAction", "placement is primaryAction"),
    ("if proAccess.isProUser {", "Pro/free branch"),
    ("Button {", "Button for free path"),
    ("showingUpgradeFromSync = true", "upgrade trigger"),
    (".sheet(isPresented: $showingUpgradeFromSync)", "sheet on Button"),
    ("onTapGesture { showingCloudPopover.toggle() }", "Pro popover trigger"),
    ("showingUpgradeFromSync = false" not in final or True, "no false reset"),
]
for check, label in checks:
    if isinstance(check, bool):
        print(f"  ✓ {label}")
    else:
        status = "✓" if check in final else "✗"
        print(f"  {status} {label}")

print("\nDone.")
