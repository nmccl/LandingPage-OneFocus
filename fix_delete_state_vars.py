#!/usr/bin/env python3
path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"
with open(path, "r") as f:
    src = f.read()

if "@State private var showingDeleteAlert" not in src:
    src = src.replace(
        "    @State private var isSaving = false",
        "    @State private var isSaving = false\n    @State private var showingDeleteAlert = false\n    @State private var deleteError: String?"
    )
    with open(path, "w") as f:
        f.write(src)
    print("added state vars")
else:
    print("already present")
