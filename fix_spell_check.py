"""
Add .spellCheckingEnabled() to content TextFields and TextEditors.
Targets:
  - Task title fields (iOSHomeView, iOSTasksView, TasksView)
  - Notes fields (iOSHomeView, iOSTasksView, TasksView)
  - Quick Notes title and body fields (iOSQuickNotesView, QuickNotesView)
  - MenuBar task/note fields (MenuBarPopoverView)
  - Category name field (iOSTasksView, TasksView)

Skips:
  - Auth fields (email, password, name) — already have .autocorrectionDisabled()
  - Search fields — not appropriate for spell check
  - AccountSettings fields — email/password, not appropriate
"""
import re, sys

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views"

# Each entry: (file_path, list of (old_snippet, new_snippet))
# Strategy: find the TextField/TextEditor line and add .spellCheckingEnabled() after its closing modifier chain.
# We'll use a regex approach: after a content TextField/TextEditor, insert the modifier before the next unrelated modifier.

def add_spell_check(content, pattern, label):
    """
    For each match of `pattern` (a TextField or TextEditor line),
    insert .spellCheckingEnabled() after the matched line if not already present.
    """
    if ".spellCheckingEnabled()" in content:
        # Already has at least one — check if this specific pattern already has it
        pass
    
    count = 0
    lines = content.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.search(pattern, line):
            # Check if next non-empty line already has spellCheckingEnabled
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and "spellCheckingEnabled" in lines[j]:
                result.append(line)
                i += 1
                continue
            # Get indentation of the TextField line
            indent = len(line) - len(line.lstrip())
            spell_line = " " * indent + ".spellCheckingEnabled()"
            result.append(line)
            result.append(spell_line)
            count += 1
        else:
            result.append(line)
        i += 1
    
    if count > 0:
        print(f"  {label}: added {count} instance(s)")
    else:
        print(f"  {label}: no matches found")
    return "\n".join(result)


# ─────────────────────────────────────────────────────────────────────────────
# Files and patterns
# ─────────────────────────────────────────────────────────────────────────────

files_and_patterns = [
    # iOS New Task Sheet — task title
    (
        BASE + "/iOS/Tabs/iOSHomeView.swift",
        [
            (r'TextField\("Enter task title"', "iOSHomeView task title"),
            (r'TextEditor\(text: \$newTaskNotes\)', "iOSHomeView task notes"),
        ]
    ),
    # iOS Tasks — edit task title + notes, category name
    (
        BASE + "/iOS/Tabs/iOSTasksView.swift",
        [
            (r'TextField\("Task title"', "iOSTasksView task title"),
            (r'TextEditor\(text: \$editNotes\)', "iOSTasksView edit notes"),
            (r'TextField\("Category name"', "iOSTasksView category name"),
            (r'TextField\("New category name"', "iOSTasksView new category name"),
        ]
    ),
    # macOS Tasks — task title + notes + category
    (
        BASE + "/Tabs/TasksView.swift",
        [
            (r'TextField\("Enter task title"', "TasksView task title"),
            (r'TextField\("Task title"', "TasksView edit task title"),
            (r'TextEditor\(text: \$newTaskNotes\)', "TasksView new task notes"),
            (r'TextEditor\(text: \$editNotes\)', "TasksView edit notes"),
            (r'TextField\("Category name"', "TasksView category name"),
        ]
    ),
    # iOS Quick Notes — note title + body
    (
        BASE + "/iOS/Tabs/iOSQuickNotesView.swift",
        [
            (r'TextField\("Note title"', "iOSQuickNotesView note title"),
            (r'TextField\("Untitled"', "iOSQuickNotesView untitled note"),
            (r'TextEditor\(text: \$note\.content\)', "iOSQuickNotesView note content"),
            (r'TextEditor\(text: \$editingContent\)', "iOSQuickNotesView editing content"),
            (r'TextEditor\(text: \$noteContent\)', "iOSQuickNotesView noteContent"),
        ]
    ),
    # macOS Quick Notes
    (
        BASE + "/Tabs/QuickNotesView.swift",
        [
            (r'TextField\("Note title"', "QuickNotesView note title"),
            (r'TextField\("Untitled"', "QuickNotesView untitled note"),
            (r'TextEditor\(text: \$note\.content\)', "QuickNotesView note content"),
            (r'TextEditor\(text: \$editingContent\)', "QuickNotesView editing content"),
            (r'TextEditor\(text: \$noteContent\)', "QuickNotesView noteContent"),
        ]
    ),
    # MenuBar — task title + note fields
    (
        BASE + "/MenuBar/MenuBarPopoverView.swift",
        [
            (r'TextField\("Task title"', "MenuBarPopoverView task title"),
            (r'TextField\("Note title"', "MenuBarPopoverView note title"),
            (r'TextEditor\(text:', "MenuBarPopoverView text editor"),
        ]
    ),
]

for file_path, patterns in files_and_patterns:
    try:
        with open(file_path) as f:
            content = f.read()
    except FileNotFoundError:
        print(f"SKIP (not found): {file_path}")
        continue
    
    print(f"\n=== {file_path.split('/')[-1]} ===")
    original = content
    for pattern, label in patterns:
        content = add_spell_check(content, pattern, label)
    
    if content != original:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  Saved.")
    else:
        print(f"  No changes needed.")

print("\nDone.")
