#!/usr/bin/env python3
"""Replace iOSNewTaskSheet stub using index-based slicing."""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSHomeView.swift"
with open(path, "r") as f:
    src = f.read()

mark_idx = src.find("// MARK: - Placeholder sheets")
endif_idx = src.rfind("#endif")

if mark_idx == -1 or endif_idx == -1:
    print("ERROR: Could not find markers")
    exit(1)

new_block = '''// MARK: - iOS New Task Sheet
struct iOSNewTaskSheet: View {
    let viewModel: TasksViewModel
    @EnvironmentObject var proAccess: ProAccessManager
    @EnvironmentObject var taskCategoryManager: TaskCategoryManager
    @Environment(\\.dismiss) private var dismiss

    @State private var taskTitle        = ""
    @State private var selectedPriority: Task.Priority = .medium
    @State private var notes            = ""
    @State private var dueDate          = Date()
    @State private var hasDueDate       = false
    @State private var selectedCategoryID: UUID? = nil

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
                            ForEach(Task.Priority.allCases, id: \\.self) { p in
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

                    // Create button
                    Button {
                        let trimmedTitle = taskTitle.trimmingCharacters(in: .whitespaces)
                        let trimmedNotes = notes.trimmingCharacters(in: .whitespaces)
                        let newTask = Task(
                            title:      trimmedTitle,
                            dueDate:    hasDueDate ? dueDate : nil,
                            priority:   selectedPriority,
                            notes:      trimmedNotes.isEmpty ? nil : trimmedNotes,
                            categoryID: selectedCategoryID
                        )
                        viewModel.addTask(newTask)
                        dismiss()
                    } label: {
                        Text("Create Task")
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
            .navigationTitle("New Task")
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

// MARK: - iOS Category Chip
private struct iOSCategoryChip: View {
    let icon: String
    let name: String
    let color: Color
    let isSelected: Bool
    let action: () -> Void
    var body: some View {
        Button(action: action) {
            HStack(spacing: 5) {
                Image(systemName: icon)
                    .font(.system(size: 11, weight: .medium))
                Text(name)
                    .font(.system(size: AppConstants.FontSize.caption,
                                  weight: isSelected ? .semibold : .regular))
            }
            .foregroundColor(isSelected ? .white : color)
            .padding(.horizontal, 12)
            .padding(.vertical, 7)
            .background(isSelected ? color : color.opacity(0.12))
            .cornerRadius(AppConstants.CornerRadius.pill)
            .overlay(
                RoundedRectangle(cornerRadius: AppConstants.CornerRadius.pill)
                    .stroke(isSelected ? Color.clear : color.opacity(0.3), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

'''

new_src = src[:mark_idx] + new_block + src[endif_idx:]
with open(path, "w") as f:
    f.write(new_src)
print("✅ iOSNewTaskSheet fully implemented and iOSCategoryChip added")
