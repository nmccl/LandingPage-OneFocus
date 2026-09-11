#!/usr/bin/env python3
"""
Replace the ClipboardHistoryViewModel with a version that uses a nonisolated
TimerBox wrapper so deinit can safely invalidate the timer without touching
@MainActor-isolated state (fixes the Swift 5.9 'No exact call to initializer'
/ actor-isolation error on deinit).
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/ClipboardHistoryViewModel.swift"

new_content = '''\
// ClipboardHistoryViewModel.swift
// OneFocus — cross-platform clipboard history view model (iOS + macOS)
import SwiftUI
import Combine

// MARK: - TimerBox
// A nonisolated reference-type wrapper that holds the polling Timer.
// Because deinit on a @MainActor class is itself nonisolated, we cannot
// access actor-isolated stored properties there.  Storing the timer inside
// this plain NSObject subclass lets deinit reach it safely without any
// actor hop or { @MainActor in } closure (which is rejected in Swift 5.9+).
private final class TimerBox: NSObject {
    var timer: Timer?

    func invalidate() {
        timer?.invalidate()
        timer = nil
    }
}

// MARK: - ClipboardHistoryViewModel
@MainActor
class ClipboardHistoryViewModel: ObservableObject {
    @Published var items: [ClipboardItem] = []
    @Published var isMonitoring: Bool = true

    // The box is nonisolated (plain reference type), so deinit can touch it.
    private let timerBox = TimerBox()
    private var lastClipboardContent: String = ""
    private var storageKey: String = "clipboardHistory"
    private var isPro: Bool = false

    init() {
        if isMonitoring { startMonitoring() }
        NotificationCenter.default.addObserver(
            forName: .userWillSignOut, object: nil, queue: .main
        ) { [weak self] _ in
            DispatchQueue.main.async { self?.clearForSignOut() }
        }
    }

    deinit {
        // timerBox is a plain reference type — safe to access from nonisolated deinit.
        timerBox.invalidate()
    }

    /// Call this on `.onAppear` and whenever the signed-in user or Pro status changes.
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
    }

    func clearForSignOut() {
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
    }

    // MARK: - Public Methods
    func toggleMonitoring() {
        isMonitoring.toggle()
        isMonitoring ? startMonitoring() : stopMonitoring()
    }

    func copyToClipboard(_ item: ClipboardItem) {
        #if canImport(AppKit)
        let pb = NSPasteboard.general
        pb.clearContents()
        pb.setString(item.content, forType: .string)
        #elseif canImport(UIKit)
        UIPasteboard.general.string = item.content
        #endif
    }

    func toggleFavorite(_ item: ClipboardItem) {
        guard let idx = items.firstIndex(where: { $0.id == item.id }) else { return }
        items[idx].isFavorite.toggle()
        saveItemsIfPro()
    }

    func deleteItem(_ item: ClipboardItem) {
        items.removeAll { $0.id == item.id }
        saveItemsIfPro()
    }

    func clearHistory() {
        items.removeAll()
        // Always wipe persisted data regardless of Pro status so that
        // a user who downgraded from Pro does not see stale saved history
        // reappear after signing out and back in.
        clearPersistedData()
    }

    func enforceLimit(_ limit: Int) {
        guard items.count > limit else { return }
        items = Array(items.prefix(limit))
        saveItemsIfPro()
    }

    // MARK: - Private Methods
    private func startMonitoring() {
        #if canImport(AppKit)
        if let content = NSPasteboard.general.string(forType: .string) {
            lastClipboardContent = content
        }
        #elseif canImport(UIKit)
        if let content = UIPasteboard.general.string { lastClipboardContent = content }
        #endif
        let t = Timer.scheduledTimer(
            timeInterval: 1.0,
            target: self,
            selector: #selector(timerFired(_:)),
            userInfo: nil,
            repeats: true
        )
        timerBox.timer = t
    }

    private func stopMonitoring() {
        timerBox.invalidate()
    }

    @objc private func timerFired(_ timer: Timer) {
        checkClipboard()
    }

    private func checkClipboard() {
        #if canImport(AppKit)
        guard let content = NSPasteboard.general.string(forType: .string) else { return }
        #elseif canImport(UIKit)
        guard let content = UIPasteboard.general.string else { return }
        #endif
        guard content != lastClipboardContent,
              !content.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              items.first?.content != content
        else { return }
        lastClipboardContent = content
        let newItem = ClipboardItem(content: content)
        items.insert(newItem, at: 0)
        saveItemsIfPro()
    }

    private func loadItems() {
        if let data    = UserDefaults.standard.data(forKey: storageKey),
           let decoded = try? JSONDecoder().decode([ClipboardItem].self, from: data) {
            items = decoded
        }
    }

    private func saveItemsIfPro() {
        guard isPro else { return }
        if let encoded = try? JSONEncoder().encode(items) {
            UserDefaults.standard.set(encoded, forKey: storageKey)
            UserDefaults.standard.synchronize()
        }
    }

    private func clearPersistedData() {
        UserDefaults.standard.removeObject(forKey: storageKey)
        UserDefaults.standard.synchronize()
    }
}
'''

with open(path, 'w') as f:
    f.write(new_content)

print(f"✅ Written {len(new_content)} bytes to {path}")

# Quick sanity check
with open(path) as f:
    src = f.read()

checks = [
    ("TimerBox class", "private final class TimerBox"),
    ("timerBox property", "private let timerBox = TimerBox()"),
    ("clean deinit", "timerBox.invalidate()"),
    ("no old timer? property", "private var timer:" not in src),
    ("startMonitoring uses timerBox", "timerBox.timer = t"),
    ("stopMonitoring uses timerBox", "timerBox.invalidate()"),
]

all_ok = True
for label, check in checks:
    if isinstance(check, bool):
        ok = check
    else:
        ok = check in src
    status = "✅" if ok else "❌"
    print(f"  {status} {label}")
    if not ok:
        all_ok = False

print()
print("All checks passed." if all_ok else "Some checks FAILED — review the file.")
