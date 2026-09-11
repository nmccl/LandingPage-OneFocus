"""
Fix the note save race condition on macOS.

ROOT CAUSE:
1. QuickNotesView.onAppear calls store.configure(userID:) every time the view appears.
   configure() always calls fetchFromSupabase().
2. When the user clicks to a different note:
   a. onDisappear fires -> flushSave() -> commitSave() -> store.update(note) dispatches async Supabase upsert
   b. activelyEditingNoteID is set to nil
   c. The new editor appears -> QuickNotesView.onAppear -> configure() -> fetchFromSupabase()
   d. Supabase hasn't finished writing yet -> old data returns -> notes array overwritten

FIX STRATEGY:
1. NotesStore: Add a `pendingWriteNoteIDs: Set<UUID>` that tracks notes with in-flight Supabase writes.
   fetchFromSupabase() skips overwriting any note in this set.
   update() adds the note ID before the write, removes it after.

2. QuickNotesView.onAppear: Don't call configure() on every appear — only call it if userID
   hasn't been set yet (configure is already called from AuthManager on sign-in).
   This eliminates the spurious fetch entirely.
"""

import re

# ── Fix 1: NotesStore.swift ──────────────────────────────────────────────────
notes_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/NotesStore.swift"
with open(notes_path) as f:
    src = f.read()

# 1a. Add pendingWriteNoteIDs property after activelyEditingNoteID
old_prop = "    var activelyEditingNoteID: UUID? = nil"
new_prop = """    var activelyEditingNoteID: UUID? = nil
    /// Note IDs that have an in-flight Supabase write. fetchFromSupabase()
    /// skips overwriting these so a background fetch can't clobber a save
    /// that hasn't landed yet.
    private var pendingWriteNoteIDs: Set<UUID> = []"""
src = src.replace(old_prop, new_prop, 1)

# 1b. Update fetchFromSupabase() to also protect pendingWriteNoteIDs
old_fetch_guard = """            // Preserve any note currently open in the editor so
            // in-flight keystrokes are not overwritten by the fetch.
            if let editingID = activelyEditingNoteID,
               let localNote = notes.first(where: { $0.id == editingID }) {
                var merged = fetched
                if let idx = merged.firstIndex(where: { $0.id == editingID }) {
                    merged[idx] = localNote
                }
                notes = merged
            } else {
                notes = fetched
            }"""
new_fetch_guard = """            // Preserve notes that are either open in the editor OR have
            // an in-flight Supabase write. This prevents a concurrent fetch
            // from overwriting content that hasn't been persisted yet.
            let protectedIDs = pendingWriteNoteIDs.union(
                activelyEditingNoteID.map { [$0] } ?? []
            )
            if protectedIDs.isEmpty {
                notes = fetched
            } else {
                var merged = fetched
                for pid in protectedIDs {
                    if let localNote = notes.first(where: { $0.id == pid }),
                       let idx = merged.firstIndex(where: { $0.id == pid }) {
                        merged[idx] = localNote
                    }
                }
                notes = merged
            }"""
src = src.replace(old_fetch_guard, new_fetch_guard, 1)

# 1c. Update update() to track pendingWriteNoteIDs
old_update = """    func update(_ note: Note) {
        guard let idx = notes.firstIndex(where: { $0.id == note.id }) else { return }
        notes[idx] = note
        saveCache()
        guard let uid = userID else { return }
        _Concurrency.Task {
            do {
                try await supabase
                    .from("notes")
                    .upsert(note.toRow(userID: uid), onConflict: "id")
                    .execute()
                #if DEBUG
                print("[NotesStore] Updated note \\(note.id) in Supabase")
                #endif
            } catch {
                #if DEBUG
                print("[NotesStore] update failed: \\(error)")
                #endif
            }
        }
    }"""
new_update = """    func update(_ note: Note) {
        guard let idx = notes.firstIndex(where: { $0.id == note.id }) else { return }
        notes[idx] = note
        saveCache()
        guard let uid = userID else { return }
        // Mark this note as having a pending write so fetchFromSupabase()
        // won't overwrite it with stale data while the upsert is in flight.
        pendingWriteNoteIDs.insert(note.id)
        _Concurrency.Task {
            defer { pendingWriteNoteIDs.remove(note.id) }
            do {
                try await supabase
                    .from("notes")
                    .upsert(note.toRow(userID: uid), onConflict: "id")
                    .execute()
                #if DEBUG
                print("[NotesStore] Updated note \\(note.id) in Supabase")
                #endif
            } catch {
                #if DEBUG
                print("[NotesStore] update failed: \\(error)")
                #endif
            }
        }
    }"""
src = src.replace(old_update, new_update, 1)

with open(notes_path, "w") as f:
    f.write(src)

ok1a = "pendingWriteNoteIDs: Set<UUID>" in src
ok1b = "protectedIDs" in src
ok1c = "pendingWriteNoteIDs.insert(note.id)" in src
print(("OK" if ok1a else "FAIL") + ": NotesStore pendingWriteNoteIDs property added")
print(("OK" if ok1b else "FAIL") + ": NotesStore fetchFromSupabase protectedIDs guard")
print(("OK" if ok1c else "FAIL") + ": NotesStore update() tracks pendingWriteNoteIDs")

# ── Fix 2: QuickNotesView.onAppear — don't re-configure on every appear ──────
mac_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/QuickNotesView.swift"
with open(mac_path) as f:
    mac = f.read()

# Replace the onAppear that calls configure() unconditionally
# with one that only calls configure if userID is not yet set
old_onappear = """        .onAppear {
            store.configure(userID: authManager.currentUser?.id.uuidString)
            if selectedNoteID == nil {
                selectedNoteID = filteredNotes.first?.id
            }
        }"""
new_onappear = """        .onAppear {
            // configure() is already called from AuthManager on sign-in.
            // Only call it here if the store has no userID yet (cold launch
            // where the view appears before the auth callback fires).
            // Calling configure() on every appear triggers fetchFromSupabase()
            // which can overwrite in-flight saves when the user navigates
            // between notes quickly.
            if authManager.currentUser != nil && NotesStore.shared.isConfigured == false {
                store.configure(userID: authManager.currentUser?.id.uuidString)
            }
            if selectedNoteID == nil {
                selectedNoteID = filteredNotes.first?.id
            }
        }"""
if old_onappear in mac:
    mac = mac.replace(old_onappear, new_onappear, 1)
    with open(mac_path, "w") as f:
        f.write(mac)
    print("OK: QuickNotesView.onAppear no longer calls configure() on every appear")
else:
    print("FAIL: QuickNotesView.onAppear pattern not found — printing nearby lines:")
    lines = mac.split("\n")
    for i, line in enumerate(lines):
        if "store.configure" in line or "onAppear" in line:
            print(f"  {i+1}: {line}")

# ── Fix 3: Add isConfigured property to NotesStore ───────────────────────────
with open(notes_path) as f:
    src2 = f.read()

old_userid_prop = "    private var userID: String?"
new_userid_prop = """    private var userID: String?
    /// True once configure(userID:) has been called with a non-nil user.
    /// Used by views to avoid redundant configure() calls on every appear.
    var isConfigured: Bool { userID != nil }"""
if old_userid_prop in src2:
    src2 = src2.replace(old_userid_prop, new_userid_prop, 1)
    with open(notes_path, "w") as f:
        f.write(src2)
    print("OK: NotesStore.isConfigured property added")
else:
    print("FAIL: could not find 'private var userID: String?' in NotesStore")
