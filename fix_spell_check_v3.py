"""
Add .contentFieldStyle() to content TextFields and TextEditors.
Uses correct placeholder strings found in the actual files.
Skips auth, search, and password fields.
"""
import re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views"


def add_modifier(content, pattern, label):
    count = 0
    lines = content.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.search(pattern, line):
            # Check if next non-empty line already has contentFieldStyle
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and "contentFieldStyle" in lines[j]:
                result.append(line)
                i += 1
                continue
            indent = len(line) - len(line.lstrip())
            result.append(line)
            result.append(" " * indent + ".contentFieldStyle()")
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
    # iOS New Task Sheet — task title + notes
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
            (r'TextField\("Task title"', "task title"),
            (r'TextEditor\(text: \$notes\)', "edit task notes"),
            (r'TextField\("Name"', "category name"),
        ]
    ),
    # macOS Tasks — title + notes + category
    (
        BASE + "/Tabs/TasksView.swift",
        [
            (r'TextField\("Enter task title"', "new task title"),
            (r'TextField\("Task title"', "edit task title"),
            (r'TextEditor\(text: \$notes\)', "new task notes"),
            (r'TextEditor\(text: \$editedNotes\)', "edit task notes"),
            (r'TextField\("Category name"', "category name"),
        ]
    ),
    # iOS Quick Notes — title + folder/tag names
    (
        BASE + "/iOS/Tabs/iOSQuickNotesView.swift",
        [
            (r'TextField\("Title"', "note title"),
            (r'TextField\("Name"', "folder/tag name"),
        ]
    ),
    # macOS Quick Notes — title + folder name
    (
        BASE + "/Tabs/QuickNotesView.swift",
        [
            (r'TextField\("Note Title"', "note title"),
            (r'TextField\("Folder name"', "folder name"),
        ]
    ),
    # MenuBar — text editor
    (
        BASE + "/MenuBar/MenuBarPopoverView.swift",
        [
            (r'TextEditor\(text:', "text editor"),
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
        content = add_modifier(content, pattern, label)

    if content != original:
        with open(file_path, "w") as f:
            f.write(content)
        print("  Saved.")
    else:
        print("  No changes needed.")

print("\nDone.")
