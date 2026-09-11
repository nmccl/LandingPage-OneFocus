import re

checks = []

def check(label, path, pattern, should_exist=True):
    try:
        with open(path) as f:
            content = f.read()
        found = bool(re.search(pattern, content))
        result = found == should_exist
        checks.append((result, label))
        status = "OK" if result else "FAIL"
        print(status + ": " + label)
    except Exception as e:
        checks.append((False, label))
        print("FAIL: " + label + " -- " + str(e))

base = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# NotesStore: HTML encoding
check("NotesStore uses content_html column", base + "/Services/NotesStore.swift", r"content_html")
check("NotesStore NOT using content_rtf", base + "/Services/NotesStore.swift", r"content_rtf", should_exist=False)
check("NotesStore has activelyEditingNoteID", base + "/Services/NotesStore.swift", r"activelyEditingNoteID")
check("NotesStore HTML encode in toRow", base + "/Services/NotesStore.swift", r"documentType.*html|html.*documentType|NSAttributedString\.DocumentType\.html")
check("NotesStore HTML decode in Note(row:)", base + "/Services/NotesStore.swift", r"NSAttributedString\.DocumentType\.html|documentType.*html")

# macOS editor
check("macOS editor sets activelyEditingNoteID on appear", base + "/Views/Tabs/QuickNotesView.swift", r"activelyEditingNoteID\s*=\s*note\.id")
check("macOS editor clears activelyEditingNoteID on disappear", base + "/Views/Tabs/QuickNotesView.swift", r"activelyEditingNoteID\s*=\s*nil")

# iOS editor
check("iOS editor sets activelyEditingNoteID on appear", base + "/Views/iOS/Tabs/iOSQuickNotesView.swift", r"activelyEditingNoteID\s*=\s*noteID")
check("iOS editor clears activelyEditingNoteID on disappear", base + "/Views/iOS/Tabs/iOSQuickNotesView.swift", r"activelyEditingNoteID\s*=\s*nil")

# No bare Task {} in key files
for fname in ["Services/NotesStore.swift", "Models/TasksViewModel.swift", "Manager/TaskCategoryManager.swift",
              "Manager/NoteFolderManager.swift", "Manager/HistoryManager.swift", "Manager/ClipboardHistoryViewModel.swift"]:
    path = base + "/" + fname
    short = fname.split("/")[-1]
    check("No bare Task{} in " + short, path, r"(?<!_Concurrency\.)Task\s*\{", should_exist=False)

total = len(checks)
passed = sum(1 for ok, _ in checks if ok)
print("\n" + str(passed) + "/" + str(total) + " checks passed")
