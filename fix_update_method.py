"""
Targeted fix for update() in NotesStore.swift.
Uses line numbers to do a precise replacement since the string matching
failed due to line-wrapping in the terminal output.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/NotesStore.swift"
with open(path) as f:
    lines = f.readlines()

# Find the update() function
start = None
for i, line in enumerate(lines):
    if "    func update(_ note: Note) {" in line:
        start = i
        break

if start is None:
    print("FAIL: could not find update() function")
    exit(1)

# Find the closing brace of update()
depth = 0
end = None
for i in range(start, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if depth == 0 and i > start:
        end = i
        break

if end is None:
    print("FAIL: could not find end of update() function")
    exit(1)

print(f"Found update() at lines {start+1}-{end+1}")
print("Current content:")
for i in range(start, end+1):
    print(f"  {i+1}: {lines[i]}", end="")

# Replace with fixed version
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
    }
"""

lines[start:end+1] = [new_update]
with open(path, "w") as f:
    f.writelines(lines)

# Verify
with open(path) as f:
    result = f.read()

ok = "pendingWriteNoteIDs.insert(note.id)" in result and "defer { pendingWriteNoteIDs.remove(note.id) }" in result
print("\n" + ("OK" if ok else "FAIL") + ": update() now tracks pendingWriteNoteIDs")
