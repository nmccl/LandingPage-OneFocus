"""
Fix: Stack Create Task and Cancel buttons vertically in macOS NewTaskDetailSheet.
- Remove the separate footer VStack with Divider + Cancel
- Add Cancel as a full-width light button directly below Create Task in the content VStack
"""
import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/TasksView.swift"

with open(path) as f:
    content = f.read()

# ── Replace the Create button + separate Cancel footer with stacked buttons ──
# Old: Create button ends the content VStack, then a separate VStack(spacing:0) holds Cancel
OLD_BUTTONS = (
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
    "                .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "                .scrollContentBackground(.hidden)\n\n"
    "                VStack(spacing: 0) {\n"
    "                    Divider()\n"
    "                    HStack {\n"
    "                        Spacer()\n"
    "                        Button(\"Cancel\") { closePanel() }\n"
    "                            .buttonStyle(.bordered)\n"
    "                            .foregroundColor(AppConstants.Colors.textPrimary)\n"
    "                    }\n"
    "                    .padding()\n"
    "                    .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "                }"
)

NEW_BUTTONS = (
    "                    // Action buttons — stacked vertically\n"
    "                    VStack(spacing: AppConstants.Spacing.sm) {\n"
    "                        // Create Task (primary)\n"
    "                        Button {\n"
    "                            let newTask = Task(\n"
    "                                title:      taskTitle,\n"
    "                                dueDate:    hasDueDate ? dueDate : nil,\n"
    "                                priority:   selectedPriority,\n"
    "                                notes:      notes.isEmpty ? nil : notes,\n"
    "                                categoryID: selectedCategoryID\n"
    "                            )\n"
    "                            viewModel.addTask(newTask)\n"
    "                            closePanel()\n"
    "                        } label: {\n"
    "                            Text(\"Create Task\")\n"
    "                                .font(.system(size: AppConstants.FontSize.body, weight: .semibold))\n"
    "                                .foregroundColor(.white)\n"
    "                                .frame(maxWidth: .infinity)\n"
    "                                .padding(.vertical, 14)\n"
    "                                .background(taskTitle.isEmpty\n"
    "                                            ? AppConstants.Colors.textTertiary\n"
    "                                            : AppConstants.Colors.primaryAccent)\n"
    "                                .cornerRadius(AppConstants.CornerRadius.medium)\n"
    "                        }\n"
    "                        .buttonStyle(.plain)\n"
    "                        .disabled(taskTitle.isEmpty)\n"
    "                        // Cancel (secondary)\n"
    "                        Button {\n"
    "                            closePanel()\n"
    "                        } label: {\n"
    "                            Text(\"Cancel\")\n"
    "                                .font(.system(size: AppConstants.FontSize.body, weight: .medium))\n"
    "                                .foregroundColor(AppConstants.Colors.textPrimary)\n"
    "                                .frame(maxWidth: .infinity)\n"
    "                                .padding(.vertical, 14)\n"
    "                                .background(AppConstants.Colors.inputBackground)\n"
    "                                .cornerRadius(AppConstants.CornerRadius.medium)\n"
    "                        }\n"
    "                        .buttonStyle(.plain)\n"
    "                    }\n"
    "                }\n"
    "                .padding(AppConstants.Spacing.xl)\n"
    "                .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)"
)

if OLD_BUTTONS not in content:
    print("ERROR: Could not find the Create+Cancel button block")
    # Debug: show what's around the Create button
    idx = content.find("// Create button")
    print(repr(content[idx:idx+1200]))
    sys.exit(1)

content = content.replace(OLD_BUTTONS, NEW_BUTTONS, 1)
print("Step 1 (stack Create Task + Cancel buttons): OK")

with open(path, "w") as f:
    f.write(content)

print("Done. TasksView.swift updated.")
