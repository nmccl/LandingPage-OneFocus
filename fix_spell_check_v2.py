"""
Add .spellCheckingEnabled() to content TextFields and TextEditors.
Uses correct placeholder strings found in the actual files.
Skips auth, search, and password fields.
"""
import re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views"


def add_spell_check(content, pattern, label):
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
        print(f"  {label}: no new matches")
    return "\n".join(result)


files_and_patterns = [
    # iOS New Task Sheet
    (
        BASE + "/iOS/Tabs/iOSHomeView.swift",
        [
            (r'TextField\("Task title"', "task title"),
            (r'TextEditor\(text: \$notes\)', "task notes"),
        ]
    ),
    # iOS Edit Task + Category
    (
        BASE + "/iOS/Tabs/iOSTasksView.swift",
        [
            (r'TextEditor\(text: \$notes\)', "edit task notes"),
            (r'TextField\("Name"', "category name"),
        ]
    ),
    # macOS Tasks
    (
        BASE + "/Tabs/TasksView.swift",
        [
            (r'TextEditor\(text: \$newTaskNotes\)', "new task notes"),
            (r'TextEditor\(text: \$editNotes\)', "edit task notes"),
        ]
    ),
    # iOS Quick Notes — title field + folder name
    (
        BASE + "/iOS/Tabs/iOSQuickNotesView.swift",
        [
            (r'TextField\("Title"', "note title"),
            (r'TextField\("Name"', "folder/tag name"),
        ]
    ),
    # macOS Quick Notes — title field + folder name
    (
        BASE + "/Tabs/QuickNotesView.swift",
        [
            (r'TextField\("Note Title"', "note title"),
            (r'TextField\("Folder name"', "folder name"),
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
        print("  Saved.")
    else:
        print("  No changes needed.")

print("\nDone.")
