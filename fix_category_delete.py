"""
Add a trash delete button (with confirmation alert) to ManageCategoriesSheet
in TasksView.swift (macOS).

Changes:
1. Add @State private var categoryToDelete: TaskCategory? = nil
   after the existing @State private var editingCategory line.
2. After the pencil Button block, add a trash Button that sets categoryToDelete.
3. Add .alert(...) on the List to confirm deletion.

All changes are pure Swift/SwiftUI — no new imports, no new methods.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/TasksView.swift"
with open(path) as f:
    content = f.read()

# ── Change 1: add categoryToDelete state variable ──────────────────────────
old_state = "    @State private var editingCategory: TaskCategory? = nil"
new_state = (
    "    @State private var editingCategory: TaskCategory? = nil\n"
    "    @State private var categoryToDelete: TaskCategory? = nil"
)
if old_state not in content:
    print("FAIL: could not find editingCategory @State line")
    exit(1)
content = content.replace(old_state, new_state, 1)

# ── Change 2: add trash button after the pencil button block ───────────────
# The pencil button block ends with:
#                                 }
#                                 .buttonStyle(.plain)
#                             }
#                             .padding(.vertical, AppConstants.Spacing.xs)
# We insert the trash button between .buttonStyle(.plain) and the closing }
# of the HStack.

old_pencil_end = (
    "                                .buttonStyle(.plain)\n"
    "                            }\n"
    "                            .padding(.vertical, AppConstants.Spacing.xs)"
)
new_pencil_end = (
    "                                .buttonStyle(.plain)\n"
    "                                Button {\n"
    "                                    categoryToDelete = category\n"
    "                                } label: {\n"
    "                                    Image(systemName: \"trash\")\n"
    "                                        .font(.system(size: 13))\n"
    "                                        .foregroundColor(AppConstants.Colors.error)\n"
    "                                }\n"
    "                                .buttonStyle(.plain)\n"
    "                            }\n"
    "                            .padding(.vertical, AppConstants.Spacing.xs)"
)
if old_pencil_end not in content:
    print("FAIL: could not find pencil button end block")
    exit(1)
content = content.replace(old_pencil_end, new_pencil_end, 1)

# ── Change 3: add .alert confirmation on the List ─────────────────────────
# The List block ends with:
#                     .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)
# We append .alert(...) right after that line (before the closing `}`).
old_list_end = (
    "                    .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "                }"
)
new_list_end = (
    "                    .background(isGlassPanel ? Color.clear : AppConstants.Colors.backgroundPrimary)\n"
    "                    .alert(\"Delete Category?\", isPresented: Binding(\n"
    "                        get: { categoryToDelete != nil },\n"
    "                        set: { if !$0 { categoryToDelete = nil } }\n"
    "                    )) {\n"
    "                        Button(\"Delete\", role: .destructive) {\n"
    "                            if let cat = categoryToDelete {\n"
    "                                taskCategoryManager.delete(cat)\n"
    "                            }\n"
    "                            categoryToDelete = nil\n"
    "                        }\n"
    "                        Button(\"Cancel\", role: .cancel) {\n"
    "                            categoryToDelete = nil\n"
    "                        }\n"
    "                    } message: {\n"
    "                        if let cat = categoryToDelete {\n"
    "                            Text(\"\\\"\\(cat.name)\\\" will be permanently deleted. Tasks using this category will become uncategorized.\")\n"
    "                        }\n"
    "                    }\n"
    "                }"
)
if old_list_end not in content:
    print("FAIL: could not find list background line for alert attachment")
    exit(1)
content = content.replace(old_list_end, new_list_end, 1)

with open(path, "w") as f:
    f.write(content)

# Verify
with open(path) as f:
    result = f.read()

ok1 = "categoryToDelete: TaskCategory? = nil" in result
ok2 = 'Image(systemName: "trash")' in result
ok3 = 'foregroundColor(AppConstants.Colors.error)' in result
ok4 = '"Delete Category?"' in result
ok5 = 'taskCategoryManager.delete(cat)' in result
ok6 = '"Cancel", role: .cancel' in result

print(("OK" if ok1 else "FAIL") + ": categoryToDelete @State added")
print(("OK" if ok2 else "FAIL") + ": trash button added")
print(("OK" if ok3 else "FAIL") + ": trash button uses error color")
print(("OK" if ok4 else "FAIL") + ": delete confirmation alert added")
print(("OK" if ok5 else "FAIL") + ": alert calls taskCategoryManager.delete(cat)")
print(("OK" if ok6 else "FAIL") + ": cancel button in alert")
