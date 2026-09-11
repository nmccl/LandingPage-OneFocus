#!/usr/bin/env python3
"""
Gate Supabase sync behind Pro across all stores.

Strategy per store:
1. Add `private var isPro: Bool = false` property
2. Update `configure(userID:)` to `configure(userID:, isPro: Bool = false)`
   and store the value
3. Add `guard isPro else { return }` as first line of `fetchFromSupabase()`
4. Add `guard isPro else { return }` after `saveCache()` in each write function
   (before the existing `guard let uid = userID else { return }`)

Also:
5. Update MainView.swift cloud icon — free users see upgrade sheet
6. Update OneFocusApp.swift — pass isPro to all store configure() calls
   and update on proAccess.$isProUser changes
"""

import re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# ─────────────────────────────────────────────────────────────────────────────
# Helper: add isPro guard to fetchFromSupabase
# ─────────────────────────────────────────────────────────────────────────────
def gate_fetch(content, store_name):
    """Add guard isPro else { return } as first line of fetchFromSupabase()"""
    # Pattern: "func fetchFromSupabase() async {\n        guard let uid"
    old = "    func fetchFromSupabase() async {\n        guard let uid = userID else { return }"
    new = "    func fetchFromSupabase() async {\n        guard isPro else { return }\n        guard let uid = userID else { return }"
    if old in content:
        content = content.replace(old, new, 1)
        print(f"  ✓ {store_name}: fetchFromSupabase() gated")
    else:
        print(f"  ✗ {store_name}: fetchFromSupabase pattern not found")
    return content

def add_isPro_property(content, store_name, after_marker):
    """Add `private var isPro: Bool = false` after a marker line"""
    if "private var isPro: Bool" in content:
        print(f"  ✓ {store_name}: isPro already present")
        return content
    if after_marker in content:
        content = content.replace(after_marker, after_marker + "\n    private var isPro: Bool = false", 1)
        print(f"  ✓ {store_name}: isPro property added")
    else:
        print(f"  ✗ {store_name}: marker for isPro not found: {repr(after_marker)}")
    return content

def update_configure(content, store_name, old_sig, new_sig, old_body_marker, new_body_marker):
    """Update configure() signature and add isPro storage"""
    if old_sig in content:
        content = content.replace(old_sig, new_sig, 1)
        print(f"  ✓ {store_name}: configure() signature updated")
    else:
        print(f"  ✗ {store_name}: configure() signature not found")
    if old_body_marker in content:
        content = content.replace(old_body_marker, new_body_marker, 1)
        print(f"  ✓ {store_name}: configure() isPro stored")
    else:
        print(f"  ✗ {store_name}: configure() body marker not found")
    return content

def gate_writes(content, store_name):
    """Add guard isPro after saveCache() calls in write functions"""
    # Replace all occurrences of:
    #   saveCache()\n        guard let uid = userID else { return }
    # with:
    #   saveCache()\n        guard isPro else { return }\n        guard let uid = userID else { return }
    old = "        saveCache()\n        guard let uid = userID else { return }"
    new = "        saveCache()\n        guard isPro else { return }\n        guard let uid = userID else { return }"
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  ✓ {store_name}: {count} write site(s) gated")
    else:
        print(f"  ✗ {store_name}: no saveCache()+guard pattern found")
    return content

# ─────────────────────────────────────────────────────────────────────────────
# 1. NotesStore.swift
# ─────────────────────────────────────────────────────────────────────────────
print("NotesStore.swift")
path = f"{BASE}/Services/NotesStore.swift"
with open(path) as f:
    c = f.read()

c = add_isPro_property(c, "NotesStore", "    private var userID: String?")
c = update_configure(c,
    "NotesStore",
    "    func configure(userID: String?) {",
    "    func configure(userID: String?, isPro: Bool = false) {",
    "        self.userID = userID\n        if userID == nil {\n            notes = []\n            return\n        }",
    "        self.isPro = isPro\n        self.userID = userID\n        if userID == nil {\n            notes = []\n            return\n        }"
)
c = gate_fetch(c, "NotesStore")
c = gate_writes(c, "NotesStore")
with open(path, "w") as f:
    f.write(c)

# ─────────────────────────────────────────────────────────────────────────────
# 2. TasksViewModel.swift
# ─────────────────────────────────────────────────────────────────────────────
print("\nTasksViewModel.swift")
path = f"{BASE}/Models/TasksViewModel.swift"
with open(path) as f:
    c = f.read()

c = add_isPro_property(c, "TasksViewModel", "    private var userID: String?")
c = update_configure(c,
    "TasksViewModel",
    "    func configure(userID: String?) {",
    "    func configure(userID: String?, isPro: Bool = false) {",
    "        let changed = userID != self.userID\n        self.userID = userID",
    "        let changed = userID != self.userID\n        self.isPro = isPro\n        self.userID = userID"
)
c = gate_fetch(c, "TasksViewModel")
c = gate_writes(c, "TasksViewModel")
with open(path, "w") as f:
    f.write(c)

# ─────────────────────────────────────────────────────────────────────────────
# 3. HistoryManager.swift
# ─────────────────────────────────────────────────────────────────────────────
print("\nHistoryManager.swift")
path = f"{BASE}/Manager/HistoryManager.swift"
with open(path) as f:
    c = f.read()

c = add_isPro_property(c, "HistoryManager", "    private var userID: String?")

# Read configure body
old_cfg_sig = "    func configure(userID: String?) {"
new_cfg_sig = "    func configure(userID: String?, isPro: Bool = false) {"
c = c.replace(old_cfg_sig, new_cfg_sig, 1)

# Find where to store isPro in configure — after "self.userID = userID"
old_store = "        self.userID = userID\n        if userID == nil {"
new_store = "        self.isPro = isPro\n        self.userID = userID\n        if userID == nil {"
if old_store in c:
    c = c.replace(old_store, new_store, 1)
    print(f"  ✓ HistoryManager: configure() updated")
else:
    print(f"  ✗ HistoryManager: configure body marker not found")

c = gate_fetch(c, "HistoryManager")
c = gate_writes(c, "HistoryManager")
with open(path, "w") as f:
    f.write(c)

# ─────────────────────────────────────────────────────────────────────────────
# 4. NoteFolderManager.swift
# ─────────────────────────────────────────────────────────────────────────────
print("\nNoteFolderManager.swift")
path = f"{BASE}/Manager/NoteFolderManager.swift"
with open(path) as f:
    c = f.read()

c = add_isPro_property(c, "NoteFolderManager", "    private var userID: String?")
c = c.replace("    func configure(userID: String?) {", "    func configure(userID: String?, isPro: Bool = false) {", 1)

# Find configure body store point
old_store = "        self.userID = userID\n        if userID == nil {"
new_store = "        self.isPro = isPro\n        self.userID = userID\n        if userID == nil {"
if old_store in c:
    c = c.replace(old_store, new_store, 1)
    print(f"  ✓ NoteFolderManager: configure() updated")
else:
    print(f"  ✗ NoteFolderManager: configure body marker not found")

c = gate_fetch(c, "NoteFolderManager")
c = gate_writes(c, "NoteFolderManager")
with open(path, "w") as f:
    f.write(c)

# ─────────────────────────────────────────────────────────────────────────────
# 5. TaskCategoryManager.swift
# ─────────────────────────────────────────────────────────────────────────────
print("\nTaskCategoryManager.swift")
path = f"{BASE}/Manager/TaskCategoryManager.swift"
with open(path) as f:
    c = f.read()

c = add_isPro_property(c, "TaskCategoryManager", "    private var userID: String?")
c = c.replace("    func configure(userID: String?) {", "    func configure(userID: String?, isPro: Bool = false) {", 1)

old_store = "        self.userID = userID\n        if userID == nil {"
new_store = "        self.isPro = isPro\n        self.userID = userID\n        if userID == nil {"
if old_store in c:
    c = c.replace(old_store, new_store, 1)
    print(f"  ✓ TaskCategoryManager: configure() updated")
else:
    print(f"  ✗ TaskCategoryManager: configure body marker not found")

c = gate_fetch(c, "TaskCategoryManager")
c = gate_writes(c, "TaskCategoryManager")
with open(path, "w") as f:
    f.write(c)

# ─────────────────────────────────────────────────────────────────────────────
# 6. OneFocusApp.swift — pass isPro to all configure() calls
# ─────────────────────────────────────────────────────────────────────────────
print("\nOneFocusApp.swift")
path = f"{BASE}/OneFocusApp.swift"
with open(path) as f:
    c = f.read()

replacements = [
    # tasksViewModel
    ("                tasksViewModel.configure(userID: uid)",
     "                tasksViewModel.configure(userID: uid, isPro: proAccessManager.isProUser)"),
    # historyManager
    ("                historyManager.configure(userID: uid)",
     "                historyManager.configure(userID: uid, isPro: proAccessManager.isProUser)"),
    # taskCategoryManager
    ("                taskCategoryManager.configure(userID: uid)",
     "                taskCategoryManager.configure(userID: uid, isPro: proAccessManager.isProUser)"),
    # NotesStore
    ("                NotesStore.shared.configure(userID: uid)",
     "                NotesStore.shared.configure(userID: uid, isPro: proAccessManager.isProUser)"),
    # noteFolderManager
    ("                noteFolderManager.configure(userID: uid)",
     "                noteFolderManager.configure(userID: uid, isPro: proAccessManager.isProUser)"),
]

for old, new in replacements:
    if old in c:
        c = c.replace(old, new, 1)
        print(f"  ✓ {old.strip()[:50]}...")
    else:
        print(f"  ✗ not found: {old.strip()[:50]}...")

# Also update the proAccess.$isProUser onChange to reconfigure stores
# Find the existing onChange block that reconfigures clipboardViewModel
old_onchange = "            .onReceive(proAccessManager.$isProUser) { isPro in\n                clipboardViewModel.configure(userID: authManager.currentUser?.id.uuidString, isPro: isPro)"
new_onchange = """            .onReceive(proAccessManager.$isProUser) { isPro in
                let uid = authManager.currentUser?.id.uuidString
                clipboardViewModel.configure(userID: uid, isPro: isPro)
                tasksViewModel.configure(userID: uid, isPro: isPro)
                historyManager.configure(userID: uid, isPro: isPro)
                taskCategoryManager.configure(userID: uid, isPro: isPro)
                NotesStore.shared.configure(userID: uid, isPro: isPro)
                noteFolderManager.configure(userID: uid, isPro: isPro)"""

if old_onchange in c:
    c = c.replace(old_onchange, new_onchange, 1)
    print("  ✓ proAccess.$isProUser onChange updated to reconfigure all stores")
else:
    print("  ✗ proAccess.$isProUser onChange block not found exactly")
    # Try to find it
    if "onReceive(proAccessManager.$isProUser)" in c:
        idx = c.find("onReceive(proAccessManager.$isProUser)")
        print(f"  Found at char {idx}:")
        print(repr(c[idx:idx+200]))

with open(path, "w") as f:
    f.write(c)

# ─────────────────────────────────────────────────────────────────────────────
# 7. MainView.swift — cloud icon: free users see upgrade sheet
# ─────────────────────────────────────────────────────────────────────────────
print("\nMainView.swift")
path = f"{BASE}/Views/MainView.swift"
with open(path) as f:
    c = f.read()

# Add showingUpgradeSheet state
old_state = "    @State private var showingCloudPopover  = false"
new_state  = "    @State private var showingCloudPopover  = false\n    @State private var showingUpgradeFromSync = false"
if old_state in c:
    c = c.replace(old_state, new_state, 1)
    print("  ✓ showingUpgradeFromSync state added")
else:
    print("  ✗ showingCloudPopover state not found")

# Change onTapGesture to check isPro
old_tap = "                .onTapGesture { showingCloudPopover.toggle() }"
new_tap  = "                .onTapGesture {\n                    if proAccess.isProUser {\n                        showingCloudPopover.toggle()\n                    } else {\n                        showingUpgradeFromSync = true\n                    }\n                }"
if old_tap in c:
    c = c.replace(old_tap, new_tap, 1)
    print("  ✓ cloud icon tap gated behind isPro")
else:
    print("  ✗ onTapGesture not found")

# Update help text
c = c.replace('.help("iCloud Sync")', '.help(proAccess.isProUser ? "Account Sync" : "Upgrade to Pro for sync")', 1)

# Add upgrade sheet presentation — attach to the toolbar ZStack or nearby
old_popover = "                .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {\n                    CloudSyncPopover(cloudSync: cloudSync)\n                        .environmentObject(themeManager)\n                }"
new_popover = """                .popover(isPresented: $showingCloudPopover, arrowEdge: .bottom) {
                    CloudSyncPopover(cloudSync: cloudSync)
                        .environmentObject(themeManager)
                }
                .sheet(isPresented: $showingUpgradeFromSync) {
                    UpgradePromptView(context: .generic)
                        .environmentObject(proAccess)
                        .environmentObject(storeKit)
                }"""
if old_popover in c:
    c = c.replace(old_popover, new_popover, 1)
    print("  ✓ upgrade sheet added to cloud icon")
else:
    print("  ✗ popover block not found exactly")

# Update cloudSyncIcon to show icloud.slash for free users
old_icon_func = "    private var cloudSyncIcon: String {\n        guard cloudSync.isSyncEnabled else { return \"icloud.slash\" }\n        guard cloudSync.isSyncEnabled else { return \"icloud.slash\" }\n        return \"icloud\"\n    }"
new_icon_func = "    private var cloudSyncIcon: String {\n        guard proAccess.isProUser else { return \"icloud.slash\" }\n        guard cloudSync.isSyncEnabled else { return \"icloud.slash\" }\n        return \"icloud\"\n    }"
if old_icon_func in c:
    c = c.replace(old_icon_func, new_icon_func, 1)
    print("  ✓ cloudSyncIcon updated for free users")
else:
    # Try simpler replacement
    old2 = '    private var cloudSyncIcon: String {\n        guard cloudSync.isSyncEnabled else { return "icloud.slash" }\n        guard cloudSync.isSyncEnabled else { return "icloud.slash" }\n        return "icloud"\n    }'
    new2 = '    private var cloudSyncIcon: String {\n        guard proAccess.isProUser else { return "icloud.slash" }\n        guard cloudSync.isSyncEnabled else { return "icloud.slash" }\n        return "icloud"\n    }'
    if old2 in c:
        c = c.replace(old2, new2, 1)
        print("  ✓ cloudSyncIcon updated (pass 2)")
    else:
        print("  ✗ cloudSyncIcon function not found — showing current:")
        idx = c.find("cloudSyncIcon")
        if idx >= 0:
            print(repr(c[idx:idx+200]))

with open(path, "w") as f:
    f.write(c)

print("\nAll done.")
