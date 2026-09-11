path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSTasksView.swift"
with open(path, 'r') as f:
    content = f.read()

# 1. Add taskToEdit state var
old_state = "    @State private var showingCategorySheet       = false"
new_state = """    @State private var showingCategorySheet       = false
    @State private var taskToEdit:            Task?  = nil"""
assert old_state in content, "state not found"
content = content.replace(old_state, new_state, 1)

# 2. Add tap + leading swipe edit action to the task row
old_row_end = """                .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                    Button(role: .destructive) {
                        tasksViewModel.deleteTask(task)
                        if userSettings.hapticEnabled { HapticManager.impact(.medium) }
                    } label: {
                        Label("Delete", systemImage: "trash")
                    }
                }"""
new_row_end = """                .onTapGesture {
                    taskToEdit = task
                    if userSettings.hapticEnabled { HapticManager.impact(.light) }
                }
                .swipeActions(edge: .leading, allowsFullSwipe: false) {
                    Button {
                        taskToEdit = task
                        if userSettings.hapticEnabled { HapticManager.impact(.light) }
                    } label: {
                        Label("Edit", systemImage: "pencil")
                    }
                    .tint(AppConstants.Colors.primaryAccent)
                }
                .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                    Button(role: .destructive) {
                        tasksViewModel.deleteTask(task)
                        if userSettings.hapticEnabled { HapticManager.impact(.medium) }
                    } label: {
                        Label("Delete", systemImage: "trash")
                    }
                }"""
assert old_row_end in content, "row end not found"
content = content.replace(old_row_end, new_row_end, 1)

# 3. Add edit sheet after category sheet
old_cat_end = """            .sheet(isPresented: $showingCategorySheet) {
                iOSCategoryPickerSheet(
                    selectedCategoryID: $selectedCategoryID,
                    manager: taskCategoryManager
                )
                .preferredColorScheme(themeManager.current.colorScheme)
                .tint(AppConstants.Colors.primaryAccent)
            }
        }
    }"""
new_cat_end = """            .sheet(isPresented: $showingCategorySheet) {
                iOSCategoryPickerSheet(
                    selectedCategoryID: $selectedCategoryID,
                    manager: taskCategoryManager
                )
                .preferredColorScheme(themeManager.current.colorScheme)
                .tint(AppConstants.Colors.primaryAccent)
            }
            .sheet(item: $taskToEdit) { task in
                iOSEditTaskSheet(task: task, viewModel: tasksViewModel)
                    .environmentObject(userSettings)
                    .environmentObject(proAccess)
                    .environmentObject(taskCategoryManager)
                    .preferredColorScheme(themeManager.current.colorScheme)
                    .tint(AppConstants.Colors.primaryAccent)
            }
        }
    }"""
assert old_cat_end in content, "category sheet end not found"
content = content.replace(old_cat_end, new_cat_end, 1)

# 4. Insert iOSEditTaskSheet struct before #endif
edit_sheet = r'''
// MARK: - Edit Task Sheet
struct iOSEditTaskSheet: View {
    let task: Task
    let viewModel: TasksViewModel
    @EnvironmentObject var proAccess: ProAccessManager
    @EnvironmentObject var taskCategoryManager: TaskCategoryManager
    @Environment(\.dismiss) private var dismiss

    @State private var taskTitle:          String
    @State private var selectedPriority:   Task.Priority
    @State private var notes:              String
    @State private var dueDate:            Date
    @State private var hasDueDate:         Bool
    @State private var selectedCategoryID: UUID?

    init(task: Task, viewModel: TasksViewModel) {
        self.task      = task
        self.viewModel = viewModel
        _taskTitle          = State(initialValue: task.title)
        _selectedPriority   = State(initialValue: task.priority)
        _notes              = State(initialValue: task.notes ?? "")
        _dueDate            = State(initialValue: task.dueDate ?? Date())
        _hasDueDate         = State(initialValue: task.dueDate != nil)
        _selectedCategoryID = State(initialValue: task.categoryID)
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: AppConstants.Spacing.xl) {
                    // Title
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Task Title", systemImage: "pencil")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        TextField("Enter task title", text: $taskTitle)
                            .font(.system(size: AppConstants.FontSize.body))
                            .padding(AppConstants.Spacing.md)
                            .background(AppConstants.Colors.inputBackground)
                            .cornerRadius(AppConstants.CornerRadius.medium)
                    }
                    // Category (Pro only)
                    if proAccess.isProUser {
                        VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                            Label("Category", systemImage: "folder")
                                .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                                .foregroundColor(AppConstants.Colors.textSecondary)
                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: AppConstants.Spacing.sm) {
                                    iOSCategoryChip(
                                        icon: "tray.fill",
                                        name: "None",
                                        color: AppConstants.Colors.textSecondary,
                                        isSelected: selectedCategoryID == nil
                                    ) { selectedCategoryID = nil }
                                    ForEach(taskCategoryManager.categories) { cat in
                                        iOSCategoryChip(
                                            icon: cat.icon,
                                            name: cat.name,
                                            color: cat.color,
                                            isSelected: selectedCategoryID == cat.id
                                        ) { selectedCategoryID = cat.id }
                                    }
                                }
                                .padding(.vertical, 2)
                            }
                        }
                    }
                    // Priority
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Priority", systemImage: "flag")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        Picker("Priority", selection: $selectedPriority) {
                            ForEach(Task.Priority.allCases, id: \.self) { p in
                                Text(p.rawValue).tag(p)
                            }
                        }
                        .pickerStyle(.segmented)
                    }
                    // Due Date
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Toggle(isOn: $hasDueDate) {
                            Label("Due Date", systemImage: "calendar")
                                .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                                .foregroundColor(AppConstants.Colors.textSecondary)
                        }
                        .tint(AppConstants.Colors.primaryAccent)
                        if hasDueDate {
                            DatePicker("", selection: $dueDate, displayedComponents: [.date])
                                .datePickerStyle(.graphical)
                                .labelsHidden()
                        }
                    }
                    // Notes
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Notes (Optional)", systemImage: "note.text")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        TextEditor(text: $notes)
                            .font(.system(size: AppConstants.FontSize.body))
                            .frame(minHeight: 90)
                            .padding(AppConstants.Spacing.sm)
                            .background(AppConstants.Colors.inputBackground)
                            .cornerRadius(AppConstants.CornerRadius.medium)
                            .scrollContentBackground(.hidden)
                    }
                    // Save button
                    Button {
                        let trimmedTitle = taskTitle.trimmingCharacters(in: .whitespaces)
                        let trimmedNotes = notes.trimmingCharacters(in: .whitespaces)
                        var updated = task
                        updated.title      = trimmedTitle
                        updated.priority   = selectedPriority
                        updated.dueDate    = hasDueDate ? dueDate : nil
                        updated.notes      = trimmedNotes.isEmpty ? nil : trimmedNotes
                        updated.categoryID = selectedCategoryID
                        viewModel.updateTask(updated)
                        dismiss()
                    } label: {
                        Text("Save Changes")
                            .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 15)
                            .background(taskTitle.trimmingCharacters(in: .whitespaces).isEmpty
                                        ? AppConstants.Colors.textTertiary
                                        : AppConstants.Colors.primaryAccent)
                            .cornerRadius(AppConstants.CornerRadius.medium)
                    }
                    .disabled(taskTitle.trimmingCharacters(in: .whitespaces).isEmpty)
                }
                .padding(AppConstants.Spacing.xl)
            }
            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())
            .navigationTitle("Edit Task")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }
            }
        }
    }
}
'''

assert '\n#endif\n' in content, "#endif not found"
content = content.replace('\n#endif\n', edit_sheet + '\n#endif\n', 1)

with open(path, 'w') as f:
    f.write(content)
print("done")
