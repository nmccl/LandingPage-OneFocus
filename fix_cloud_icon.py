#!/usr/bin/env python3
"""
Fix cloud icon toolbar:
1. Change placement from .automatic to .primaryAction (far right on macOS)
2. Split Pro vs free into two separate branches:
   - Pro: ZStack with .onTapGesture + .popover (existing working pattern)
   - Free: Button { showingUpgradeFromSync = true } to avoid re-render loop with .sheet
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/MainView.swift"
with open(path) as f:
    c = f.read()

# Step 1: Change placement
c = c.replace(
    "ToolbarItem(placement: .automatic) {",
    "ToolbarItem(placement: .primaryAction) {",
    1
)

# Step 2: Replace the entire inner content of the ToolbarItem
# Find the current onTapGesture block and replace with split Pro/free branches
old_tap_section = """.onTapGesture {
                    if proAccess.isProUser {
                        showingCloudPopover.toggle()
                    } else {
                        showingUpgradeFromSync = true
                    }
                }
                .help(proAccess.isProUser ? "Account Sync" : "Upgrade to Pro for sync")
                .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {
                    CloudSyncPopover(cloudSync: cloudSync)
                        .environmentObject(themeManager)
                }
                .sheet(isPresented: $showingUpgradeFromSync) {
                    UpgradePromptView(context: .generic)
                        .environmentObject(proAccess)
                        .environmentObject(storeKit)
                }
            }"""

new_tap_section = """.onTapGesture { showingCloudPopover.toggle() }
                .help("Account Sync")
                .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {
                    CloudSyncPopover(cloudSync: cloudSync)
                        .environmentObject(themeManager)
                }
            }"""

if old_tap_section in c:
    c = c.replace(old_tap_section, new_tap_section, 1)
    print("✓ Tap section replaced (Pro-only popover path)")
else:
    print("✗ Tap section not found — checking for partial match")
    if "showingUpgradeFromSync = true" in c:
        print("  showingUpgradeFromSync found")
    if "onTapGesture" in c:
        idx = c.find("onTapGesture")
        print(f"  onTapGesture at char {idx}:")
        print(repr(c[idx:idx+300]))

# Step 3: Now wrap the entire ZStack in an if/else for Pro vs free
# Find the ZStack opening and wrap it
old_zstack_open = """                ZStack {
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

new_zstack_wrapped = """                if proAccess.isProUser {
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

if old_zstack_open in c:
    c = c.replace(old_zstack_open, new_zstack_wrapped, 1)
    print("✓ ZStack wrapped in Pro/free if-else")
else:
    print("✗ ZStack block not found")
    if "onTapGesture { showingCloudPopover.toggle() }" in c:
        idx = c.find("onTapGesture { showingCloudPopover.toggle() }")
        print(f"  Found onTapGesture at {idx}:")
        print(repr(c[max(0,idx-300):idx+100]))

with open(path, "w") as f:
    f.write(c)

# Verify
with open(path) as f:
    final = f.read()

checks = [
    ("placement: .primaryAction", "placement changed to primaryAction"),
    ("if proAccess.isProUser {", "Pro/free branch exists"),
    ("Button {", "Button used for free path"),
    ("showingUpgradeFromSync = true", "upgrade sheet trigger exists"),
    (".sheet(isPresented: $showingUpgradeFromSync)", "sheet attached to Button"),
    ("onTapGesture { showingCloudPopover.toggle() }", "Pro path uses onTapGesture"),
]
for check, label in checks:
    status = "✓" if check in final else "✗"
    print(f"  {status} {label}")

print("\nDone.")
