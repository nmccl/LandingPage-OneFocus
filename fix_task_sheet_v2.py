"""
Fix: Remove ScrollView from iOSNewTaskSheet and iOSEditTaskSheet.
Uses brace-counting to locate the exact NavigationStack block, then replaces it.
"""
import sys

home_path  = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSHomeView.swift"
tasks_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSTasksView.swift"


def find_block(content, start_marker, from_pos=0):
    """Find a block starting at start_marker and return (start, end) indices."""
    idx = content.find(start_marker, from_pos)
    if idx == -1:
        return None, None
    depth = 0
    i = idx
    while i < len(content):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return idx, i + 1
        i += 1
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# iOSNewTaskSheet  (iOSHomeView.swift)
# ─────────────────────────────────────────────────────────────────────────────
with open(home_path) as f:
    home = f.read()

struct_pos = home.find("struct iOSNewTaskSheet")
nav_start, nav_end = find_block(home, "        NavigationStack {", struct_pos)

if nav_start is None:
    print("ERROR: Could not find NavigationStack in iOSNewTaskSheet")
    sys.exit(1)

NEW_NAV_BLOCK = (
    "        NavigationStack {\n"
    "            Form {\n"
    "                // Title\n"
    "                Section {\n"
    "                    TextField(\"Task title\", text: $taskTitle)\n"
    "                        .font(.system(size: AppConstants.FontSize.body))\n"
    "                } header: {\n"
    "                    Text(\"Title\")\n"
    "                }\n"
    "\n"
    "                // Category (Pro only)\n"
    "                if proAccess.isProUser {\n"
    "                    Section {\n"
    "                        ScrollView(.horizontal, showsIndicators: false) {\n"
    "                            HStack(spacing: AppConstants.Spacing.sm) {\n"
    "                                iOSCategoryChip(\n"
    "                                    icon: \"tray.fill\",\n"
    "                                    name: \"None\",\n"
    "                                    color: AppConstants.Colors.textSecondary,\n"
    "                                    isSelected: selectedCategoryID == nil\n"
    "                                ) { selectedCategoryID = nil }\n"
    "                                ForEach(taskCategoryManager.categories) { cat in\n"
    "                                    iOSCategoryChip(\n"
    "                                        icon: cat.icon,\n"
    "                                        name: cat.name,\n"
    "                                        color: cat.color,\n"
    "                                        isSelected: selectedCategoryID == cat.id\n"
    "                                    ) { selectedCategoryID = cat.id }\n"
    "                                }\n"
    "                            }\n"
    "                            .padding(.vertical, 4)\n"
    "                        }\n"
    "                    } header: {\n"
    "                        Text(\"Category\")\n"
    "                    }\n"
    "                }\n"
    "\n"
    "                // Priority\n"
    "                Section {\n"
    "                    Picker(\"Priority\", selection: $selectedPriority) {\n"
    "                        ForEach(Task.Priority.allCases, id: \\.self) { p in\n"
    "                            Text(p.rawValue).tag(p)\n"
    "                        }\n"
    "                    }\n"
    "                    .pickerStyle(.segmented)\n"
    "                } header: {\n"
    "                    Text(\"Priority\")\n"
    "                }\n"
    "\n"
    "                // Due Date\n"
    "                Section {\n"
    "                    Toggle(\"Set Due Date\", isOn: $hasDueDate)\n"
    "                        .tint(AppConstants.Colors.primaryAccent)\n"
    "                    if hasDueDate {\n"
    "                        DatePicker(\"Date\", selection: $dueDate, displayedComponents: [.date])\n"
    "                            .datePickerStyle(.compact)\n"
    "                    }\n"
    "                } header: {\n"
    "                    Text(\"Due Date\")\n"
    "                }\n"
    "\n"
    "                // Notes\n"
    "                Section {\n"
    "                    TextEditor(text: $notes)\n"
    "                        .font(.system(size: AppConstants.FontSize.body))\n"
    "                        .frame(minHeight: 80)\n"
    "                        .scrollContentBackground(.hidden)\n"
    "                } header: {\n"
    "                    Text(\"Notes (Optional)\")\n"
    "                }\n"
    "            }\n"
    "            .navigationTitle(\"New Task\")\n"
    "            .navigationBarTitleDisplayMode(.inline)\n"
    "            .toolbar {\n"
    "                ToolbarItem(placement: .cancellationAction) {\n"
    "                    Button(\"Cancel\") { dismiss() }\n"
    "                        .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                }\n"
    "                ToolbarItem(placement: .confirmationAction) {\n"
    "                    Button(\"Create\") {\n"
    "                        let trimmedTitle = taskTitle.trimmingCharacters(in: .whitespaces)\n"
    "                        let trimmedNotes = notes.trimmingCharacters(in: .whitespaces)\n"
    "                        let newTask = Task(\n"
    "                            title:      trimmedTitle,\n"
    "                            dueDate:    hasDueDate ? dueDate : nil,\n"
    "                            priority:   selectedPriority,\n"
    "                            notes:      trimmedNotes.isEmpty ? nil : trimmedNotes,\n"
    "                            categoryID: selectedCategoryID\n"
    "                        )\n"
    "                        viewModel.addTask(newTask)\n"
    "                        dismiss()\n"
    "                    }\n"
    "                    .fontWeight(.semibold)\n"
    "                    .foregroundColor(AppConstants.Colors.primaryAccent)\n"
    "                    .disabled(taskTitle.trimmingCharacters(in: .whitespaces).isEmpty)\n"
    "                }\n"
    "            }\n"
    "        }"
)

home = home[:nav_start] + NEW_NAV_BLOCK + home[nav_end:]
with open(home_path, "w") as f:
    f.write(home)
print("iOSNewTaskSheet: OK")

# ─────────────────────────────────────────────────────────────────────────────
# iOSEditTaskSheet  (iOSTasksView.swift)
# ─────────────────────────────────────────────────────────────────────────────
with open(tasks_path) as f:
    tasks = f.read()

edit_struct_pos = tasks.find("struct iOSEditTaskSheet")
edit_nav_start, edit_nav_end = find_block(tasks, "        NavigationStack {", edit_struct_pos)

if edit_nav_start is None:
    print("ERROR: Could not find NavigationStack in iOSEditTaskSheet")
    sys.exit(1)

NEW_EDIT_NAV_BLOCK = (
    "        NavigationStack {\n"
    "            Form {\n"
    "                // Title\n"
    "                Section {\n"
    "                    TextField(\"Task title\", text: $taskTitle)\n"
    "                        .font(.system(size: AppConstants.FontSize.body))\n"
    "                } header: {\n"
    "                    Text(\"Title\")\n"
    "                }\n"
    "\n"
    "                // Category (Pro only)\n"
    "                if proAccess.isProUser {\n"
    "                    Section {\n"
    "                        ScrollView(.horizontal, showsIndicators: false) {\n"
    "                            HStack(spacing: AppConstants.Spacing.sm) {\n"
    "                                iOSCategoryChip(\n"
    "                                    icon: \"tray.fill\",\n"
    "                                    name: \"None\",\n"
    "                                    color: AppConstants.Colors.textSecondary,\n"
    "                                    isSelected: selectedCategoryID == nil\n"
    "                                ) { selectedCategoryID = nil }\n"
    "                                ForEach(taskCategoryManager.categories) { cat in\n"
    "                                    iOSCategoryChip(\n"
    "                                        icon: cat.icon,\n"
    "                                        name: cat.name,\n"
    "                                        color: cat.color,\n"
    "                                        isSelected: selectedCategoryID == cat.id\n"
    "                                    ) { selectedCategoryID = cat.id }\n"
    "                                }\n"
    "                            }\n"
    "                            .padding(.vertical, 4)\n"
    "                        }\n"
    "                    } header: {\n"
    "                        Text(\"Category\")\n"
    "                    }\n"
    "                }\n"
    "\n"
    "                // Priority\n"
    "                Section {\n"
    "                    Picker(\"Priority\", selection: $selectedPriority) {\n"
    "                        ForEach(Task.Priority.allCases, id: \\.self) { p in\n"
    "                            Text(p.rawValue).tag(p)\n"
    "                        }\n"
    "                    }\n"
    "                    .pickerStyle(.segmented)\n"
    "                } header: {\n"
    "                    Text(\"Priority\")\n"
    "                }\n"
    "\n"
    "                // Due Date\n"
    "                Section {\n"
    "                    Toggle(\"Set Due Date\", isOn: $hasDueDate)\n"
    "                        .tint(AppConstants.Colors.primaryAccent)\n"
    "                    if hasDueDate {\n"
    "                        DatePicker(\"Date\", selection: $dueDate, displayedComponents: [.date])\n"
    "                            .datePickerStyle(.compact)\n"
    "                    }\n"
    "                } header: {\n"
    "                    Text(\"Due Date\")\n"
    "                }\n"
    "\n"
    "                // Notes\n"
    "                Section {\n"
    "                    TextEditor(text: $notes)\n"
    "                        .font(.system(size: AppConstants.FontSize.body))\n"
    "                        .frame(minHeight: 80)\n"
    "                        .scrollContentBackground(.hidden)\n"
    "                } header: {\n"
    "                    Text(\"Notes (Optional)\")\n"
    "                }\n"
    "            }\n"
    "            .navigationTitle(\"Edit Task\")\n"
    "            .navigationBarTitleDisplayMode(.inline)\n"
    "            .toolbar {\n"
    "                ToolbarItem(placement: .cancellationAction) {\n"
    "                    Button(\"Cancel\") { dismiss() }\n"
    "                        .foregroundColor(AppConstants.Colors.textSecondary)\n"
    "                }\n"
    "                ToolbarItem(placement: .confirmationAction) {\n"
    "                    Button(\"Save\") {\n"
    "                        let trimmedTitle = taskTitle.trimmingCharacters(in: .whitespaces)\n"
    "                        let trimmedNotes = notes.trimmingCharacters(in: .whitespaces)\n"
    "                        var updated = task\n"
    "                        updated.title      = trimmedTitle\n"
    "                        updated.priority   = selectedPriority\n"
    "                        updated.dueDate    = hasDueDate ? dueDate : nil\n"
    "                        updated.notes      = trimmedNotes.isEmpty ? nil : trimmedNotes\n"
    "                        updated.categoryID = selectedCategoryID\n"
    "                        viewModel.updateTask(updated)\n"
    "                        dismiss()\n"
    "                    }\n"
    "                    .fontWeight(.semibold)\n"
    "                    .foregroundColor(AppConstants.Colors.primaryAccent)\n"
    "                    .disabled(taskTitle.trimmingCharacters(in: .whitespaces).isEmpty)\n"
    "                }\n"
    "            }\n"
    "        }"
)

tasks = tasks[:edit_nav_start] + NEW_EDIT_NAV_BLOCK + tasks[edit_nav_end:]
with open(tasks_path, "w") as f:
    f.write(tasks)
print("iOSEditTaskSheet: OK")
