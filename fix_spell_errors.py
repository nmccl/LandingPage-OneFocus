"""
1. Remove all .spellCheckingEnabled() lines from all view files
2. Write ViewExtensions.swift to the correct Helpers path on disk
"""
import os, re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"
VIEWS = BASE + "/Views"

# ── Step 1: Strip .spellCheckingEnabled() from every Swift file in Views ──────
stripped_files = []
for root, dirs, files in os.walk(VIEWS):
    # skip hidden dirs
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for fname in files:
        if not fname.endswith(".swift"):
            continue
        path = os.path.join(root, fname)
        with open(path) as f:
            content = f.read()
        if ".spellCheckingEnabled()" not in content:
            continue
        # Remove any line that is solely ".spellCheckingEnabled()" (with leading whitespace)
        new_content = re.sub(r'[ \t]*\.spellCheckingEnabled\(\)\n', '', content)
        if new_content != content:
            with open(path, "w") as f:
                f.write(new_content)
            stripped_files.append(path.replace(BASE + "/", ""))

if stripped_files:
    print("Removed .spellCheckingEnabled() from:")
    for f in stripped_files:
        print(f"  {f}")
else:
    print("No .spellCheckingEnabled() calls found.")

# ── Step 2: Write ViewExtensions.swift to the correct Helpers path ─────────────
helpers_path = BASE + "/Helpers/ViewExtensions.swift"
view_ext_content = '''import SwiftUI

// MARK: - Content Text Field Modifiers

extension View {
    /// Re-enables spell checking and autocorrection on iOS content text fields.
    /// On macOS this is a no-op — spell checking is enabled by default.
    /// Do NOT apply to auth fields (email, password, name).
    @ViewBuilder
    func contentFieldStyle() -> some View {
#if os(iOS)
        self
            .autocorrectionDisabled(false)
            .keyboardType(.default)
#else
        self
#endif
    }
}
'''

with open(helpers_path, "w") as f:
    f.write(view_ext_content)
print(f"\nWrote ViewExtensions.swift to {helpers_path}")
print("\nDone. Add ViewExtensions.swift to your Xcode target to use .contentFieldStyle().")
