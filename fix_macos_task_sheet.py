"""
Fix: Remove ScrollView from macOS NewTaskDetailSheet and TaskDetailSheet.
- Replace ScrollView { VStack { } } with plain VStack
- Replace .datePickerStyle(.graphical) with .compact + Toggle for due date
- Add @State hasDueDate to NewTaskDetailSheet
- Shrink window frame to fit without scrolling
"""
import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/TasksView.swift"

with open(path) as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────────────────────
# 1. NewTaskDetailSheet
#    a) Add @State hasDueDate = false after the existing @State vars
#    b) Replace the ScrollView body with a plain VStack
#    c) Replace the graphical DatePicker with Toggle + compact picker
#    d) Shrink the frame
# ─────────────────────────────────────────────────────────────────────────────

# a) Add hasDueDate state var
OLD_STATE = (
    "    @State private var taskTitle        = \"\"\n"
    "    @State private var selectedPriority: Task.Priority = .medium\n"
    "    @State private var notes            = \"\"\n"
    "    @State private var dueDate          = Date()\n"
    "    @State private var selectedCategoryID: UUID?"
)
NEW_STATE = (
    "    @State private var taskTitle        = \"\"\n"
    "    @State private var selectedPriority: Task.Priority = .medium\n"
    "    @State private var notes            = \"\"\n"
    "    @State private var dueDate          = Date()\n"
    "    @State private var hasDueDate       = false\n"
    "    @State private var selectedCategoryID: UUID?"
)
if OLD_STATE not in content:
    print("ERROR: Could not find NewTaskDetailSheet @State vars")
    sys.exit(1)
content = content.replace(OLD_STATE, NEW_STATE, 1)
print("Step 1a (add hasDueDate state): OK")

# b+c+d) Replace the ScrollView body block in NewTaskDetailSheet
# The block starts at "                ScrollView {" (inside the outer VStack)
# and ends just before the Cancel footer VStack.
# We'll use brace-counting from the struct body.

def find_block(text, marker, from_pos=0):
    idx = text.find(marker, from_pos)
    if idx == -1:
        return None, None
    depth = 0
    i = idx
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return idx, i + 1
        i += 1
    return None, None

# Find NewTaskDetailSheet struct
new_task_pos = content.find("struct NewTaskDetailSheet")
# Find the ScrollView inside it (the vertical one, not horizontal)
# It appears as "                ScrollView {" inside the outer VStack
scroll_marker = "                ScrollView {\n                    VStack(spacing: AppConstants.Spacing.xl) {\n\n                        // Title\n                        VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n                            Text(\"Task Title\")"
scroll_start = content.find(scroll_marker, new_task_pos)
if scroll_start == -1:
    print("ERROR: Could not find NewTaskDetailSheet ScrollView block")
    # Debug
    idx = content.find("struct NewTaskDetailSheet")
    sv = content.find("ScrollView {", idx)
    print(repr(content[sv:sv+200]))
    sys.exit(1)

# Find the end of this ScrollView block
sv_start, sv_end = find_block(content, "                ScrollView {", new_task_pos)
if sv_start is None:
    print("ERROR: Could not find end of NewTaskDetailSheet ScrollView")
    sys.exit(1)

# Also grab the trailing modifiers on the ScrollView (.scrollContentBackground, .background, .navigationTitle)
# They appear right after the closing brace of ScrollView
after_sv = content[sv_end:sv_end+300]
print("After ScrollView block:", repr(after_sv[:200]))

NEW_TASK_CONTENT = (
    "                VStack(spacing: AppConstants.Spacing.lg) {\n"
    "                    // Title\n"
    "                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                        Text(\"Task Title\")\n"
    "                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                            .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                        TextField(\"Enter task title\", text: $taskTitle)\n"
    "                            .textFieldStyle(.plain)\n"
    "                            .font(.system(size: AppConstants.FontSize.body))\n"
    "                            .padding(AppConstants.Spacing.md)\n"
    "                            .background(AppConstants.Colors.inputBackground)\n"
    "                            .cornerRadius(AppConstants.CornerRadius.medium)\n"
    "                    }\n"
    "                    // Category picker — Pro only\n"
    "                    if proAccess.isProUser {\n"
    "                        VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                            Text(\"Category\")\n"
    "                                .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                                .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                            ScrollView(.horizontal, showsIndicators: false) {\n"
    "                                HStack(spacing: AppConstants.Spacing.sm) {\n"
    "                                    CategoryChip(\n"
    "                                        icon: \"tray.fill\",\n"
    "                                        name: \"None\",\n"
    "                                        color: AppConstants.Colors.textSecondary,\n"
    "                                        isSelected: selectedCategoryID == nil\n"
    "                                    ) {\n"
    "                                        selectedCategoryID = nil\n"
    "                                    }\n"
    "                                    ForEach(taskCategoryManager.categories) { cat in\n"
    "                                        CategoryChip(\n"
    "                                            icon: cat.icon,\n"
    "                                            name: cat.name,\n"
    "                                            color: cat.color,\n"
    "                                            isSelected: selectedCategoryID == cat.id\n"
    "                                        ) {\n"
    "                                            selectedCategoryID = cat.id\n"
    "                                        }\n"
    "                                    }\n"
    "                                }\n"
    "                                .padding(.vertical, 2)\n"
    "                            }\n"
    "                        }\n"
    "                    }\n"
    "                    // Priority\n"
    "                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                        Text(\"Priority\")\n"
    "                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                            .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                        Picker(\"\", selection: $selectedPriority) {\n"
    "                            ForEach(Task.Priority.allCases, id: \\.self) { priority in\n"
    "                                Text(priority.rawValue).tag(priority)\n"
    "                            }\n"
    "                        }\n"
    "                        .pickerStyle(.segmented)\n"
    "                        .tint(Color.gray)\n"
    "                    }\n"
    "                    // Due Date\n"
    "                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                        Toggle(\"Due Date\", isOn: $hasDueDate)\n"
    "                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                            .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                            .tint(AppConstants.Colors.primaryAccent)\n"
    "                        if hasDueDate {\n"
    "                            DatePicker(\"\", selection: $dueDate, displayedComponents: [.date])\n"
    "                                .datePickerStyle(.compact)\n"
    "                                .labelsHidden()\n"
    "                        }\n"
    "                    }\n"
    "                    // Notes\n"
    "                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                        Text(\"Notes (Optional)\")\n"
    "                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                            .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                        TextEditor(text: $notes)\n"
    "                            .font(.system(size: AppConstants.FontSize.body))\n"
    "                            .frame(height: 80)\n"
    "                            .padding(AppConstants.Spacing.sm)\n"
    "                            .background(AppConstants.Colors.inputBackground)\n"
    "                            .cornerRadius(AppConstants.CornerRadius.medium)\n"
    "                            .scrollContentBackground(.hidden)\n"
    "                    }\n"
    "                    // Create button\n"
    "                    Button {\n"
    "                        let newTask = Task(\n"
    "                            title:      taskTitle,\n"
    "                            dueDate:    hasDueDate ? dueDate : nil,\n"
    "                            priority:   selectedPriority,\n"
    "                            notes:      notes.isEmpty ? nil : notes,\n"
    "                            categoryID: selectedCategoryID\n"
    "                        )\n"
    "                        viewModel.addTask(newTask)\n"
    "                        closePanel()\n"
    "                    } label: {\n"
    "                        Text(\"Create Task\")\n"
    "                            .font(.system(size: AppConstants.FontSize.body, weight: .medium))\n"
    "                            .foregroundColor(.white)\n"
    "                            .frame(maxWidth: .infinity)\n"
    "                            .padding(.vertical, 14)\n"
    "                            .background(taskTitle.isEmpty\n"
    "                                        ? AppConstants.Colors.textTertiary\n"
    "                                        : AppConstants.Colors.primaryAccent)\n"
    "                            .cornerRadius(AppConstants.CornerRadius.medium)\n"
    "                    }\n"
    "                    .buttonStyle(.plain)\n"
    "                    .disabled(taskTitle.isEmpty)\n"
    "                }\n"
    "                .padding(AppConstants.Spacing.xl)\n"
    "                .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)"
)

content = content[:sv_start] + NEW_TASK_CONTENT + content[sv_end:]
print("Step 1b+c (replace NewTask ScrollView with VStack + compact picker): OK")

# Now remove the trailing .scrollContentBackground and .background and .navigationTitle
# that were modifiers on the old ScrollView — they're now baked into the VStack above.
# Find and remove them.
OLD_TRAILING = (
    "                .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "                .navigationTitle(\"New Task\")\n"
)
if OLD_TRAILING in content:
    content = content.replace(OLD_TRAILING, "", 1)
    print("Step 1d (remove old ScrollView trailing modifiers): OK")
else:
    # Check what's there
    idx = content.find("struct NewTaskDetailSheet")
    nav = content.find(".navigationTitle", idx)
    print("WARNING: Could not find .navigationTitle trailing modifier, checking:", repr(content[nav-100:nav+100]))

# Fix the frame to be smaller since no scrolling needed
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
    print("Step 1e (shrink NewTask frame): OK")
else:
    print("WARNING: Could not find NewTask frame to shrink")

# ─────────────────────────────────────────────────────────────────────────────
# 2. TaskDetailSheet — edit mode graphical calendar → compact
# ─────────────────────────────────────────────────────────────────────────────

OLD_EDIT_DATE = (
    "                            VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                                Text(\"Due Date\")\n"
    "                                    .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                                    .foregroundColor(AppConstants.Colors.textSecondary)\n\n"
    "                                DatePicker(\"\", selection: $editedDueDate, displayedComponents: [.date])\n"
    "                                    .datePickerStyle(.graphical)\n"
    "                                    .labelsHidden()\n"
    "                            }"
)
NEW_EDIT_DATE = (
    "                            VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {\n"
    "                                Toggle(\"Due Date\", isOn: Binding(\n"
    "                                    get: { true },\n"
    "                                    set: { _ in }\n"
    "                                ))\n"
    "                                .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))\n"
    "                                .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                                .tint(AppConstants.Colors.primaryAccent)\n"
    "                                .disabled(true)\n"
    "                                DatePicker(\"\", selection: $editedDueDate, displayedComponents: [.date])\n"
    "                                    .datePickerStyle(.compact)\n"
    "                                    .labelsHidden()\n"
    "                            }"
)
if OLD_EDIT_DATE in content:
    content = content.replace(OLD_EDIT_DATE, NEW_EDIT_DATE, 1)
    print("Step 2 (TaskDetailSheet edit date compact): OK")
else:
    print("WARNING: Could not find TaskDetailSheet edit date block")
    idx = content.find("struct TaskDetailSheet")
    gidx = content.find(".graphical", idx)
    print(repr(content[gidx-200:gidx+100]))

# Also fix the TaskDetailSheet frame
OLD_DETAIL_FRAME = (
    "        .frame(idealWidth: 500, idealHeight: 650)\n"
    "        .frame(minWidth: 400, maxWidth: 600, minHeight: 500, maxHeight: 800)"
)
NEW_DETAIL_FRAME = (
    "        .frame(idealWidth: 500, idealHeight: 600)\n"
    "        .frame(minWidth: 400, maxWidth: 600, minHeight: 480, maxHeight: 680)"
)
if OLD_DETAIL_FRAME in content:
    content = content.replace(OLD_DETAIL_FRAME, NEW_DETAIL_FRAME, 1)
    print("Step 2b (shrink TaskDetailSheet frame): OK")
else:
    print("WARNING: Could not find TaskDetailSheet frame")

with open(path, "w") as f:
    f.write(content)

print("\nAll steps complete. TasksView.swift updated.")
