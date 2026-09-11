#!/usr/bin/env python3
"""
Fix remaining items:
- Fix 7b: Add Sign In link to iOSOnboardingView paywall (line-based)
- Fix 10: Wrap print() statements in #if DEBUG across Manager/Services/Models
"""

import os
import glob

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

def read(path):
    with open(path) as f:
        return f.read()

def write(path, content):
    with open(path, "w") as f:
        f.write(content)

results = []

# ─────────────────────────────────────────────────────────────────────────────
# FIX 7b: Add Sign In link after Restore Purchases in iOSOnboardingView
# ─────────────────────────────────────────────────────────────────────────────
path = f"{BASE}/Views/Auth/iOSOnboardingView.swift"
with open(path) as f:
    lines = f.readlines()

# Find the line with .buttonStyle(.plain) after "Restore Purchases"
restore_idx = None
for i, line in enumerate(lines):
    if 'Button("Restore Purchases")' in line:
        restore_idx = i
        break

if restore_idx is None:
    results.append("✗ Fix 7b: Restore Purchases button not found")
else:
    # Find the closing .buttonStyle(.plain) after restore_idx
    plain_idx = None
    for i in range(restore_idx, min(restore_idx + 15, len(lines))):
        if ".buttonStyle(.plain)" in lines[i]:
            plain_idx = i
            break

    if plain_idx is None:
        results.append("✗ Fix 7b: .buttonStyle(.plain) after Restore Purchases not found")
    else:
        # Check if sign-in link already added
        if "Already have an account" in "".join(lines[plain_idx:plain_idx+5]):
            results.append("~ Fix 7b: Sign In link already present")
        else:
            # Insert after the .buttonStyle(.plain) line
            sign_in_lines = [
                "                Button(\"Already have an account? Sign In\") {\n",
                "                    showingSignIn = true\n",
                "                }\n",
                "                .font(.system(size: 13))\n",
                "                .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))\n",
                "                .buttonStyle(.plain)\n",
            ]
            lines = lines[:plain_idx+1] + sign_in_lines + lines[plain_idx+1:]
            with open(path, "w") as f:
                f.writelines(lines)
            results.append("✓ Fix 7b: Sign In link added after Restore Purchases")

# Now add the .sheet for showingSignIn — find the .task { block and add .sheet before it
with open(path) as f:
    lines = f.readlines()

if "showingSignIn = true" in "".join(lines) and ".sheet(isPresented: $showingSignIn)" not in "".join(lines):
    # Find ".task {" near the end of the paywall page body
    task_idx = None
    for i, line in enumerate(lines):
        if ".task {" in line and "isEligibleForTrial" in "".join(lines[i:i+3]):
            task_idx = i
            break
    if task_idx:
        sheet_lines = [
            "        .sheet(isPresented: $showingSignIn) {\n",
            "            iOSSignInView()\n",
            "                .environmentObject(authManager)\n",
            "        }\n",
        ]
        lines = lines[:task_idx] + sheet_lines + lines[task_idx:]
        with open(path, "w") as f:
            f.writelines(lines)
        results.append("✓ Fix 7c: .sheet(isPresented: $showingSignIn) added")
    else:
        results.append("✗ Fix 7c: .task { block not found for sheet insertion")
else:
    if ".sheet(isPresented: $showingSignIn)" in "".join(lines):
        results.append("~ Fix 7c: sheet already present")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 10: Wrap print() / debugPrint() in #if DEBUG
# ─────────────────────────────────────────────────────────────────────────────
dirs_to_fix = [
    f"{BASE}/Manager",
    f"{BASE}/Services",
    f"{BASE}/Models",
]

total_wrapped = 0
files_changed = []

for d in dirs_to_fix:
    for fpath in glob.glob(f"{d}/**/*.swift", recursive=True):
        with open(fpath) as f:
            lines = f.readlines()
        new_lines = []
        i = 0
        changed = False
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            is_print = stripped.startswith("print(") or stripped.startswith("debugPrint(")
            # Check if already inside #if DEBUG block
            already_guarded = False
            for j in range(max(0, i-5), i):
                if "#if DEBUG" in lines[j]:
                    already_guarded = True
                    break
            if is_print and not already_guarded:
                # Collect full statement (handle multi-line)
                stmt_lines = [line]
                open_p = stripped.count("(") - stripped.count(")")
                j = i + 1
                while open_p > 0 and j < len(lines):
                    stmt_lines.append(lines[j])
                    open_p += lines[j].count("(") - lines[j].count(")")
                    j += 1
                new_lines.append(f"{indent}#if DEBUG\n")
                new_lines.extend(stmt_lines)
                new_lines.append(f"{indent}#endif\n")
                total_wrapped += 1
                changed = True
                i = j
            else:
                new_lines.append(line)
                i += 1
        if changed:
            with open(fpath, "w") as f:
                f.writelines(new_lines)
            files_changed.append(os.path.basename(fpath))

results.append(f"✓ Fix 10: Wrapped {total_wrapped} print statements in #if DEBUG across: {', '.join(files_changed) if files_changed else 'none found'}")

# Print results
print("\n".join(results))
print("\nDone.")
