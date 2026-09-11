#!/usr/bin/env python3
"""Fix ClipboardHistoryViewModel cross-account persistence bug."""

path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/ClipboardHistoryViewModel.swift'
with open(path) as f:
    content = f.read()

# Fix 1: configure() should ALWAYS clear items when account context changes.
old_configure = '''    /// Call this on `.onAppear` and whenever the signed-in user or Pro status changes.
    func configure(userID: String?, isPro: Bool) {
        let newKey = userID.map { "u_\\($0)_clipboardHistory" } ?? "clipboardHistory"
        let keyChanged = newKey != storageKey
        storageKey = newKey
        self.isPro = isPro
        if keyChanged { items = [] }
        if isPro { loadItems() } else { clearPersistedData() }
    }'''

new_configure = '''    /// Call this on `.onAppear` and whenever the signed-in user or Pro status changes.
    func configure(userID: String?, isPro: Bool) {
        let newKey = userID.map { "u_\\($0)_clipboardHistory" } ?? "clipboardHistory"
        let keyChanged = newKey != storageKey
        storageKey = newKey
        self.isPro = isPro
        // Always clear in-memory items when the account context changes,
        // and also when signing out (userID == nil) to prevent stale items
        // from the previous session re-appearing after sign-in.
        if keyChanged || userID == nil { items = [] }
        if isPro { loadItems() } else { clearPersistedData() }
    }'''

if old_configure in content:
    content = content.replace(old_configure, new_configure, 1)
    print('configure() fixed')
else:
    print('configure() not found')
    idx = content.find('func configure(userID:')
    if idx >= 0:
        print(repr(content[idx:idx+300]))

# Fix 2: clearHistory() should always remove persisted data.
old_clear = '''    func clearHistory() {
        items.removeAll()
        saveItemsIfPro()
    }'''

new_clear = '''    func clearHistory() {
        items.removeAll()
        // Always wipe persisted data regardless of Pro status so that
        // a user who downgraded from Pro does not see stale saved history
        // reappear after signing out and back in.
        clearPersistedData()
    }'''

if old_clear in content:
    content = content.replace(old_clear, new_clear, 1)
    print('clearHistory() fixed')
else:
    print('clearHistory() not found')

# Fix 3: clearForSignOut should reset lastClipboardContent.
old_signout = '''    func clearForSignOut() {
        items = []
        clearPersistedData()
    }'''

new_signout = '''    func clearForSignOut() {
        items = []
        clearPersistedData()
        // Reset the last-seen clipboard content so the monitoring timer does
        // not immediately re-insert the current clipboard value into the now-
        // empty list before the account context has been fully torn down.
        #if canImport(AppKit)
        lastClipboardContent = NSPasteboard.general.string(forType: .string) ?? ""
        #elseif canImport(UIKit)
        lastClipboardContent = UIPasteboard.general.string ?? ""
        #endif
    }'''

if old_signout in content:
    content = content.replace(old_signout, new_signout, 1)
    print('clearForSignOut() fixed')
else:
    print('clearForSignOut() not found')

with open(path, 'w') as f:
    f.write(content)
print(f'Saved. Lines: {content.count(chr(10))}')
