"""
Apply the two remaining fixes to TasksView.swift:
1. Shrink NewTaskDetailSheet frame (ScrollView already removed)
2. Replace .graphical DatePicker in TaskDetailSheet edit mode with .compact
"""
import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/TasksView.swift"

with open(path) as f:
    content = f.read()

# ── 1. Shrink NewTaskDetailSheet frame ───────────────────────────────────────
OLD_FRAME = (
    "        .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "        .frame(idealWidth: 500, idealHeight: 600)\n"
    "        .frame(minWidth: 400, maxWidth: 600, minHeight: 520, maxHeight: 850)\n"
    "    }\n"
    "}\n\n"
    "// MARK: - Category Chip"
)
NEW_FRAME = (
    "        .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "        .frame(idealWidth: 500, idealHeight: 520)\n"
    "        .frame(minWidth: 420, maxWidth: 600, minHeight: 480, maxHeight: 600)\n"
    "    }\n"
    "}\n\n"
    "// MARK: - Category Chip"
)
if OLD_FRAME in content:
    content = content.replace(OLD_FRAME, NEW_FRAME, 1)
    print("Step 1 (shrink NewTask frame): OK")
else:
    # Already shrunk or different — check
    idx = content.find("// MARK: - Category Chip")
    print("Step 1 WARNING: Frame not found, current area:")
    print(repr(content[idx-200:idx+10]))

# ── 2. Replace .graphical DatePicker in TaskDetailSheet edit mode ─────────────
# The exact content has a blank line between the label and the DatePicker
OLD_EDIT_DATE = (
    "                                DatePicker(\"\", selection: $editedDueDate, displayedComponents: [.date])\n"
    "                                    .datePickerStyle(.graphical)\n"
    "                                    .labelsHidden()"
)
NEW_EDIT_DATE = (
    "                                DatePicker(\"\", selection: $editedDueDate, displayedComponents: [.date])\n"
    "                                    .datePickerStyle(.compact)\n"
    "                                    .labelsHidden()"
)
if OLD_EDIT_DATE in content:
    content = content.replace(OLD_EDIT_DATE, NEW_EDIT_DATE, 1)
    print("Step 2 (TaskDetailSheet edit date .compact): OK")
else:
    print("Step 2 WARNING: Could not find edit date picker")
    idx2 = content.find("struct TaskDetailSheet")
    gidx = content.find(".graphical", idx2)
    if gidx != -1:
        print(repr(content[gidx-100:gidx+100]))
    else:
        print("No .graphical found in TaskDetailSheet — may already be fixed")

with open(path, "w") as f:
    f.write(content)

print("\nDone.")
