path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSTasksView.swift"
with open(path, 'r') as f:
    content = f.read()

# ── Fix 1: wrong API calls in iOSManageCategories ──────────────────────────────
# deleteCategory -> delete
content = content.replace(
    'taskCategoryManager.deleteCategory($0)',
    'taskCategoryManager.delete($0)'
)
# updateCategory -> update
content = content.replace(
    'taskCategoryManager.updateCategory(category)',
    'taskCategoryManager.update(category)'
)

# ── Fix 2: AddFolderSheet uses NoteFolderManager — replace with iOSAddCategorySheet ──
# The sheet call at line ~114 passes NoteFolderManager() which is wrong
content = content.replace(
    '                    AddFolderSheet(folderManager: NoteFolderManager())\n'
    '                        .preferredColorScheme(themeManager.current.colorScheme)\n'
    '                        .tint(AppConstants.Colors.primaryAccent)',
    '                    iOSAddCategorySheet(taskCategoryManager: taskCategoryManager)\n'
    '                        .preferredColorScheme(themeManager.current.colorScheme)\n'
    '                        .tint(AppConstants.Colors.primaryAccent)'
)

# ── Fix 3: Replace the entire AddFolderSheet struct with iOSAddCategorySheet ──
old_add = '''struct AddFolderSheet: View {
    @Environment(\\.dismiss) var dismiss
    @ObservedObject var folderManager: NoteFolderManager
    @State private var name: String = ""
    @State private var selectedIcon: String = "folder"
    private let icons: [String] = [
        // Core
        "folder.fill",
        "star.fill",
        "heart.fill",
        "bookmark.fill",
        "tag.fill",
        // Tasks / Productivity
        "checkmark.circle.fill",
        "checklist",
        "list.bullet",
        "square.and.pencil",
        // Time / Focus
        "clock.fill",
        "timer",
        // Work / School
        "briefcase.fill",
        "doc.fill",
        "book.fill",
        "graduationcap.fill",
        // Tech / Dev
        "desktopcomputer",
        "laptopcomputer",
        "terminal.fill",
        // Finance / Goals
        "dollarsign.circle.fill",
        "chart.bar.fill",
        "target",
        // Personal / Life
        "person.fill",
        "flame.fill",
        "bolt.fill",
        "car.fill",
        // Misc clean
        "flag.fill",
        "pin.fill",
        "sparkles"
    ]
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: AppConstants.Spacing.lg) {
                    // Preview chip
                    HStack(spacing: 6) {
                        Image(systemName: selectedIcon)
                            .font(.system(size: 12))
                            .foregroundColor(AppConstants.Colors.primaryAccent)
                        Text(name.isEmpty ? "Folder Name" : name)
                            .font(.system(size: AppConstants.FontSize.caption))
                            .foregroundColor(name.isEmpty
                                             ? AppConstants.Colors.textTertiary
                                             : AppConstants.Colors.primaryAccent)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(AppConstants.Colors.primaryAccent.opacity(0.10))
                    .cornerRadius(AppConstants.CornerRadius.pill)
                    // Name field
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Folder name", systemImage: "pencil")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        TextField("Folder name", text: $name)
                            .textFieldStyle(.plain)
                            .font(.system(size: AppConstants.FontSize.body))
                            .padding(AppConstants.Spacing.sm)
                            .background(AppConstants.Colors.backgroundSecondary)
                            .cornerRadius(AppConstants.CornerRadius.small)
                    }
                    // Icon grid (adaptive for iPhone/iPad)
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Icon", systemImage: "square.grid.2x2")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        LazyVGrid(
                            columns: [GridItem(.adaptive(minimum: 44), spacing: AppConstants.Spacing.sm)],
                            spacing: AppConstants.Spacing.sm
                        ) {
                            ForEach(icons, id: \\.self) { icon in
                                Button {
                                    selectedIcon = icon
                                } label: {
                                    Image(systemName: icon)
                                        .font(.system(size: 18))
                                        .foregroundColor(selectedIcon == icon
                                                         ? AppConstants.Colors.primaryAccent
                                                         : AppConstants.Colors.textSecondary)
                                        .frame(width: 44, height: 44)
                                        .background(selectedIcon == icon
                                                    ? AppConstants.Colors.primaryAccent.opacity(0.12)
                                                    : Color.clear)
                                        .cornerRadius(AppConstants.CornerRadius.small)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                    // Create button
                    Button("Create") {
                        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
                        guard !trimmed.isEmpty else { return }
                        folderManager.addFolder(name: trimmed, icon: selectedIcon)
                        dismiss()
                    }
                    .buttonStyle(.plain)
                    .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                    .foregroundColor(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                                     ? AppConstants.Colors.textTertiary
                                     : AppConstants.Colors.primaryAccent)
                    .disabled(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(AppConstants.Spacing.xl)
            }
            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())
            .navigationTitle("New Folder")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }
            }
        }
    }
}'''

new_add = r'''// MARK: - Add Category Sheet
struct iOSAddCategorySheet: View {
    @ObservedObject var taskCategoryManager: TaskCategoryManager
    @Environment(\.dismiss) private var dismiss
    @State private var name:         String = ""
    @State private var selectedIcon: String = "tag.fill"
    private let icons: [String] = [
        "tag.fill", "folder.fill", "star.fill", "heart.fill", "bookmark.fill",
        "checkmark.circle.fill", "checklist", "list.bullet", "square.and.pencil",
        "clock.fill", "timer", "briefcase.fill", "doc.fill", "book.fill",
        "graduationcap.fill", "desktopcomputer", "laptopcomputer", "terminal.fill",
        "dollarsign.circle.fill", "chart.bar.fill", "target",
        "person.fill", "flame.fill", "bolt.fill", "car.fill",
        "flag.fill", "pin.fill", "sparkles"
    ]
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: AppConstants.Spacing.lg) {
                    // Preview chip
                    HStack(spacing: 6) {
                        Image(systemName: selectedIcon)
                            .font(.system(size: 12))
                            .foregroundColor(AppConstants.Colors.primaryAccent)
                        Text(name.isEmpty ? "Category Name" : name)
                            .font(.system(size: AppConstants.FontSize.caption))
                            .foregroundColor(name.isEmpty
                                             ? AppConstants.Colors.textTertiary
                                             : AppConstants.Colors.primaryAccent)
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(AppConstants.Colors.primaryAccent.opacity(0.10))
                    .cornerRadius(AppConstants.CornerRadius.pill)
                    // Name field
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Category name", systemImage: "pencil")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        TextField("Category name", text: $name)
                            .textFieldStyle(.plain)
                            .font(.system(size: AppConstants.FontSize.body))
                            .padding(AppConstants.Spacing.sm)
                            .background(AppConstants.Colors.backgroundSecondary)
                            .cornerRadius(AppConstants.CornerRadius.small)
                    }
                    // Icon grid
                    VStack(alignment: .leading, spacing: AppConstants.Spacing.sm) {
                        Label("Icon", systemImage: "square.grid.2x2")
                            .font(.system(size: AppConstants.FontSize.subheadline, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textSecondary)
                        LazyVGrid(
                            columns: [GridItem(.adaptive(minimum: 44), spacing: AppConstants.Spacing.sm)],
                            spacing: AppConstants.Spacing.sm
                        ) {
                            ForEach(icons, id: \.self) { icon in
                                Button { selectedIcon = icon } label: {
                                    Image(systemName: icon)
                                        .font(.system(size: 18))
                                        .foregroundColor(selectedIcon == icon
                                                         ? AppConstants.Colors.primaryAccent
                                                         : AppConstants.Colors.textSecondary)
                                        .frame(width: 44, height: 44)
                                        .background(selectedIcon == icon
                                                    ? AppConstants.Colors.primaryAccent.opacity(0.12)
                                                    : Color.clear)
                                        .cornerRadius(AppConstants.CornerRadius.small)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                    // Create button
                    Button("Create") {
                        let trimmed = name.trimmingCharacters(in: .whitespacesAndNewlines)
                        guard !trimmed.isEmpty else { return }
                        taskCategoryManager.add(TaskCategory(name: trimmed, icon: selectedIcon))
                        dismiss()
                    }
                    .buttonStyle(.plain)
                    .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                    .foregroundColor(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                                     ? AppConstants.Colors.textTertiary
                                     : AppConstants.Colors.primaryAccent)
                    .disabled(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(AppConstants.Spacing.xl)
            }
            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())
            .navigationTitle("New Category")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }
            }
        }
    }
}'''

assert old_add in content, "AddFolderSheet block not found"
content = content.replace(old_add, new_add, 1)

# ── Fix 4: Replace iOSManageCategories with correct API + notes-style UI ──────
old_manage = '''// MARK: - Manage Categories
struct iOSManageCategories: View {
    @ObservedObject var taskCategoryManager: TaskCategoryManager
    @ObservedObject var tasksViewModel:      TasksViewModel
    @Environment(\\.dismiss) private var dismiss
    @State private var editingCategory: TaskCategory?
    @State private var editName: String = ""
    var body: some View {
        NavigationStack {
            List {
                if taskCategoryManager.categories.isEmpty {
                    emptyState
                } else {
                    categoryList
                }
            }
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
            .background(AppConstants.Colors.backgroundPrimary)
            .navigationTitle("Manage Categories")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                        .fontWeight(.semibold)
                        .foregroundColor(AppConstants.Colors.primaryAccent)
                }
            }
            .alert("Rename Category", isPresented: isEditingBinding) {
                TextField("Name", text: $editName)
                Button("Cancel", role: .cancel) { editingCategory = nil }
                Button("Save") { saveEdit() }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
    // MARK: - Subviews
    private var emptyState: some View {
        Text("No categories yet.")
            .font(.system(size: AppConstants.FontSize.body))
            .foregroundColor(AppConstants.Colors.textSecondary)
            .listRowBackground(AppConstants.Colors.backgroundPrimary)
    }
    private var categoryList: some View {
        ForEach(taskCategoryManager.categories) { category in
            categoryRow(category)
        }
        .onDelete(perform: deleteCategories)
    }
    private func categoryRow(_ category: TaskCategory) -> some View {
        let count = tasksViewModel.tasks.filter { $0.categoryID == category.id }.count
        return HStack {
            Image(systemName: category.icon)
                .foregroundColor(category.color)
                .frame(width: 24)
            Text(category.name)
                .foregroundColor(AppConstants.Colors.textPrimary)
            Spacer()
            Text("\\(count) task\\(count == 1 ? "" : "s")")
                .font(.system(size: AppConstants.FontSize.caption))
                .foregroundColor(AppConstants.Colors.textTertiary)
            Button {
                editingCategory = category
                editName = category.name
            } label: {
                Image(systemName: "pencil")
                    .foregroundColor(AppConstants.Colors.primaryAccent)
            }
            .buttonStyle(.plain)
            .padding(.leading, 8)
        }
        .listRowBackground(AppConstants.Colors.backgroundPrimary)
    }
    // MARK: - Logic
    private func deleteCategories(at offsets: IndexSet) {
        let categoriesToDelete = offsets.map { taskCategoryManager.categories[$0] }
        categoriesToDelete.forEach { taskCategoryManager.delete($0) }
    }
    private var isEditingBinding: Binding<Bool> {
        Binding(
            get: { editingCategory != nil },
            set: { if !$0 { editingCategory = nil } }
        )
    }
    private func saveEdit() {
        guard var category = editingCategory else { return }
        let trimmed = editName.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty {
            category.name = trimmed
            taskCategoryManager.update(category)
        }
        editingCategory = nil
    }
}'''

new_manage = r'''// MARK: - Manage Categories Sheet
struct iOSManageCategories: View {
    @ObservedObject var taskCategoryManager: TaskCategoryManager
    @ObservedObject var tasksViewModel:      TasksViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var editingCategory: TaskCategory?
    @State private var editName:        String = ""
    var body: some View {
        NavigationStack {
            List {
                if taskCategoryManager.categories.isEmpty {
                    Text("No categories yet.")
                        .font(.system(size: AppConstants.FontSize.body))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                        .listRowBackground(AppConstants.Colors.backgroundPrimary)
                } else {
                    ForEach(taskCategoryManager.categories) { category in
                        let count = tasksViewModel.tasks.filter { $0.categoryID == category.id }.count
                        HStack {
                            Image(systemName: category.icon)
                                .foregroundColor(category.color)
                                .frame(width: 24)
                            Text(category.name)
                                .foregroundColor(AppConstants.Colors.textPrimary)
                            Spacer()
                            Text("\(count) task\(count == 1 ? "" : "s")")
                                .font(.system(size: AppConstants.FontSize.caption))
                                .foregroundColor(AppConstants.Colors.textTertiary)
                            Button {
                                editingCategory = category
                                editName        = category.name
                            } label: {
                                Image(systemName: "pencil")
                                    .foregroundColor(AppConstants.Colors.primaryAccent)
                            }
                            .buttonStyle(.plain)
                            .padding(.leading, 8)
                        }
                        .listRowBackground(AppConstants.Colors.backgroundPrimary)
                    }
                    .onDelete { offsets in
                        offsets.forEach { taskCategoryManager.delete(taskCategoryManager.categories[$0]) }
                    }
                }
            }
            .listStyle(.plain)
            .scrollContentBackground(.hidden)
            .background(AppConstants.Colors.backgroundPrimary)
            .navigationTitle("Manage Categories")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { dismiss() }
                        .fontWeight(.semibold)
                        .foregroundColor(AppConstants.Colors.primaryAccent)
                }
            }
            .alert("Rename Category", isPresented: Binding(
                get: { editingCategory != nil },
                set: { if !$0 { editingCategory = nil } }
            )) {
                TextField("Name", text: $editName)
                Button("Cancel", role: .cancel) { editingCategory = nil }
                Button("Save") {
                    if var c = editingCategory {
                        let trimmed = editName.trimmingCharacters(in: .whitespacesAndNewlines)
                        if !trimmed.isEmpty {
                            c.name = trimmed
                            taskCategoryManager.update(c)
                        }
                    }
                    editingCategory = nil
                }
            }
        }
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
    }
}'''

assert old_manage in content, "iOSManageCategories block not found"
content = content.replace(old_manage, new_manage, 1)

with open(path, 'w') as f:
    f.write(content)
print("done")
