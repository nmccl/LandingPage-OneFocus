#!/usr/bin/env python3
import re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# ─── 1. CloudSyncService.swift ───────────────────────────────
css_path = f"{BASE}/Services/CloudSyncService.swift"
with open(css_path, "r") as f:
    css = f.read()

css = css.replace(
    "    // MARK: - Pull (cross-platform)",
    """    func push(clipboardItem: ClipboardItem) {
        #if !targetEnvironment(simulator)
        guard isSyncEnabled, isAvailable else { return }
        AsyncTask { await self._save(clipboardItem.ckRecord(zoneID: self.zoneID)) }
        #endif
    }
    func delete(clipboardItem: ClipboardItem) {
        #if !targetEnvironment(simulator)
        guard isSyncEnabled, isAvailable else { return }
        AsyncTask { await self._delete(id: clipboardItem.id) }
        #endif
    }
    // MARK: - Pull (cross-platform)""",
    1
)

css = css.replace(
    '        let categories = changed.filter { $0.recordType == TaskCategory.ckRecordType }.compactMap { TaskCategory(record: $0) }',
    '        let categories = changed.filter { $0.recordType == TaskCategory.ckRecordType }.compactMap { TaskCategory(record: $0) }\n        let clipboardItems = changed.filter { $0.recordType == ClipboardItem.ckRecordType }.compactMap { ClipboardItem(record: $0) }',
    1
)

css = css.replace(
    '        if !categories.isEmpty { NotificationCenter.default.post(name: .cloudDidPullCategories, object: categories) }',
    '        if !categories.isEmpty { NotificationCenter.default.post(name: .cloudDidPullCategories, object: categories) }\n        if !clipboardItems.isEmpty { NotificationCenter.default.post(name: .cloudDidPullClipboard, object: clipboardItems) }',
    1
)

css = css.replace(
    '    static let cloudDidPullCategories = Notification.Name("cloudDidPullCategories")',
    '    static let cloudDidPullCategories = Notification.Name("cloudDidPullCategories")\n    static let cloudDidPullClipboard  = Notification.Name("cloudDidPullClipboard")',
    1
)

ck_ext = """
// MARK: - ClipboardItem ↔ CKRecord
extension ClipboardItem {
    static let ckRecordType = "ClipboardItem"
    func ckRecord(zoneID: CKRecordZone.ID) -> CKRecord {
        let r = CKRecord(recordType: Self.ckRecordType,
                         recordID: CKRecord.ID(recordName: id.uuidString, zoneID: zoneID))
        r["content"]    = content as CKRecordValue
        r["timestamp"]  = timestamp as CKRecordValue
        r["isFavorite"] = (isFavorite ? 1 : 0) as CKRecordValue
        return r
    }
    init?(record: CKRecord) {
        guard let content   = record["content"]   as? String,
              let timestamp = record["timestamp"] as? Date else { return nil }
        let id = UUID(uuidString: record.recordID.recordName) ?? UUID()
        self.init(
            id:         id,
            content:    content,
            timestamp:  timestamp,
            isFavorite: (record["isFavorite"] as? Int ?? 0) == 1
        )
    }
}
"""
css = css.rstrip() + "\n" + ck_ext

with open(css_path, "w") as f:
    f.write(css)
print("CloudSyncService.swift patched")

# ─── 2. ClipboardHistoryViewModel.swift ─────────────────────
vm_path = f"{BASE}/Manager/ClipboardHistoryViewModel.swift"
with open(vm_path, "r") as f:
    vm = f.read()

vm = vm.replace(
    """        NotificationCenter.default.addObserver(
            forName: .userWillSignOut, object: nil, queue: .main
        ) { [weak self] _ in
            DispatchQueue.main.async { self?.clearForSignOut() }
        }
    }""",
    """        NotificationCenter.default.addObserver(
            forName: .userWillSignOut, object: nil, queue: .main
        ) { [weak self] _ in
            DispatchQueue.main.async { self?.clearForSignOut() }
        }
        NotificationCenter.default.addObserver(
            forName: .cloudDidPullClipboard, object: nil, queue: .main
        ) { [weak self] notification in
            guard let self,
                  let pulled = notification.object as? [ClipboardItem] else { return }
            DispatchQueue.main.async { self.mergePulledItems(pulled) }
        }
    }""",
    1
)

vm = vm.replace(
    """        let newItem = ClipboardItem(content: content)
        items.insert(newItem, at: 0)
        saveItemsIfPro()
        #elseif canImport(UIKit)""",
    """        let newItem = ClipboardItem(content: content)
        items.insert(newItem, at: 0)
        saveItemsIfPro()
        if isPro { CloudSyncService.shared.push(clipboardItem: newItem) }
        #elseif canImport(UIKit)""",
    1
)

vm = vm.replace(
    """    func deleteItem(_ item: ClipboardItem) {
        items.removeAll { $0.id == item.id }
        saveItemsIfPro()
    }""",
    """    func deleteItem(_ item: ClipboardItem) {
        items.removeAll { $0.id == item.id }
        saveItemsIfPro()
        if isPro { CloudSyncService.shared.delete(clipboardItem: item) }
    }""",
    1
)

vm = vm.replace(
    "    private func loadItems() {",
    """    private func mergePulledItems(_ pulled: [ClipboardItem]) {
        guard isPro else { return }
        var merged = items
        for remote in pulled {
            if !merged.contains(where: { $0.id == remote.id }) {
                merged.append(remote)
            }
        }
        items = merged.sorted { $0.timestamp > $1.timestamp }
        saveItemsIfPro()
    }
    private func loadItems() {""",
    1
)

with open(vm_path, "w") as f:
    f.write(vm)
print("ClipboardHistoryViewModel.swift patched")
