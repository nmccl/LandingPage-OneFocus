#!/usr/bin/env python3
"""
Fix script for Apple review TODO items:
1.  Notes sync iOS — pass isPro to configure() calls in iOSQuickNotesView
4.  Trial eligibility loading state — show spinner until product loads
7.  Onboarding skip — add "Sign In" option on paywall page
10. Print statements — wrap all print() in #if DEBUG across Manager + Services + Models
11. macOS task sheet TextEditor scrollbar — already has .scrollIndicators(.hidden) ✓
12. iOS Form section headers — already use .textCase(nil) + .font(.subheadline) ✓
13. Category chip trailing padding — already has .padding(.trailing, 16) ✓
15. Quick Notes empty state iOS — already has iOSNotesEmptyState ✓ (check if wired)
17. App icon — manual task, skip
18. Launch screen — manual task, skip
19. Info.plist NS*UsageDescription — check and add if missing
20. Deployment target — manual Xcode task, skip
"""

import os
import re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

def read(path):
    with open(path) as f:
        return f.read()

def write(path, content):
    with open(path, "w") as f:
        f.write(content)

results = []

# ─────────────────────────────────────────────────────────────────────────────
# FIX 1: Notes sync iOS — pass isPro to configure() in iOSQuickNotesView
# ─────────────────────────────────────────────────────────────────────────────
path = f"{BASE}/Views/iOS/Tabs/iOSQuickNotesView.swift"
c = read(path)

# Fix onAppear configure calls
old1 = """                .onAppear {
                    store.configure(userID: authManager.currentUser?.id.uuidString)
                    folderManager.configure(userID: authManager.currentUser?.id.uuidString)
                    // Refresh notes from Supabase each time the Notes tab appears.
                    _Concurrency.Task { await store.fetchFromSupabase() }
                }
                .onReceive(authManager.$currentUser) { user in
                    let uid = user?.id.uuidString
                    store.configure(userID: uid)
                    folderManager.configure(userID: uid)
                }"""

new1 = """                .onAppear {
                    let uid = authManager.currentUser?.id.uuidString
                    let pro = proAccess.isProUser
                    store.configure(userID: uid, isPro: pro)
                    folderManager.configure(userID: uid, isPro: pro)
                    // Refresh notes from Supabase each time the Notes tab appears.
                    if pro { _Concurrency.Task { await store.fetchFromSupabase() } }
                }
                .onReceive(authManager.$currentUser) { user in
                    let uid = user?.id.uuidString
                    let pro = proAccess.isProUser
                    store.configure(userID: uid, isPro: pro)
                    folderManager.configure(userID: uid, isPro: pro)
                }"""

if old1 in c:
    c = c.replace(old1, new1, 1)
    results.append("✓ Fix 1: iOSQuickNotesView configure() now passes isPro")
else:
    results.append("✗ Fix 1: iOSQuickNotesView onAppear block not found exactly")

write(path, c)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4: Trial eligibility loading state in iOSOnboardingView paywall
# Show spinner on purchase button until proProduct is loaded AND trial check done
# The existing code already shows ProgressView when proProduct == nil, but
# isEligibleForTrial defaults to true (not nil), so the CTA text flips after load.
# Fix: use optional Bool so we can show a spinner while the check is in-flight.
# ─────────────────────────────────────────────────────────────────────────────
path = f"{BASE}/Views/Auth/iOSOnboardingView.swift"
c = read(path)

# Change state from Bool to Bool? and show spinner while nil
old4a = "    @State private var isEligibleForTrial: Bool = true"
new4a = "    @State private var isEligibleForTrial: Bool? = nil  // nil = loading"

old4b = """                if isPurchasing || storeKit.proProduct == nil {
                            ProgressView()
                                .tint(AppConstants.Colors.backgroundPrimary)
                        } else {
                            Text(isEligibleForTrial ? "Start Free Trial" : "Upgrade to Pro")
                                .font(.system(size: 17, weight: .semibold))
                        }"""

new4b = """                if isPurchasing || storeKit.proProduct == nil || isEligibleForTrial == nil {
                            ProgressView()
                                .tint(AppConstants.Colors.backgroundPrimary)
                        } else {
                            Text(isEligibleForTrial == true ? "Start Free Trial" : "Upgrade to Pro")
                                .font(.system(size: 17, weight: .semibold))
                        }"""

old4c = "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {"
new4c = "                if isEligibleForTrial == true, let trialLabel = storeKit.trialPeriodLabel {"

old4d = "            isEligibleForTrial = await storeKit.checkTrialEligibility()"
new4d = "            isEligibleForTrial = await storeKit.checkTrialEligibility()"  # same, already correct

if old4a in c:
    c = c.replace(old4a, new4a, 1)
    results.append("✓ Fix 4a: isEligibleForTrial changed to optional Bool")
else:
    results.append("✗ Fix 4a: isEligibleForTrial state not found")

if old4b in c:
    c = c.replace(old4b, new4b, 1)
    results.append("✓ Fix 4b: Purchase button shows spinner while trial check loading")
else:
    results.append("✗ Fix 4b: Purchase button block not found")

if old4c in c:
    c = c.replace(old4c, new4c, 1)
    results.append("✓ Fix 4c: Trial disclosure uses == true check")
else:
    results.append("✗ Fix 4c: Trial disclosure line not found")

write(path, c)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 7: Onboarding skip — add "Sign In" link on paywall page
# The paywall page has "Continue with Free" and "Restore Purchases".
# Add "Already have an account? Sign In" below Restore Purchases.
# ─────────────────────────────────────────────────────────────────────────────
path = f"{BASE}/Views/Auth/iOSOnboardingView.swift"
c = read(path)

# The iOSPaywallPage needs a showSignIn state and a navigation link
# First check if it already has a sign-in path
if "Already have an account" in c or "showSignIn" in c:
    results.append("~ Fix 7: Sign-in link already exists in paywall")
else:
    # Add showSignIn state to iOSPaywallPage
    old7a = "    @State private var isPurchasing = false\n    @State private var isEligibleForTrial: Bool? = nil  // nil = loading"
    new7a = "    @State private var isPurchasing = false\n    @State private var isEligibleForTrial: Bool? = nil  // nil = loading\n    @State private var showingSignIn = false"

    old7b = """                Button("Restore Purchases") {
                    _Concurrency.Task {
                        await storeKit.restorePurchases()
                        await proAccess.evaluateProStatus()
                        if proAccess.isProUser { onComplete() }
                    }
                }
                .font(.system(size: 13))
                .foregroundColor(AppConstants.Colors.textTertiary.opacity(0.7))
                .buttonStyle(.plain)
            }"""

    new7b = """                Button("Restore Purchases") {
                    _Concurrency.Task {
                        await storeKit.restorePurchases()
                        await proAccess.evaluateProStatus()
                        if proAccess.isProUser { onComplete() }
                    }
                }
                .font(.system(size: 13))
                .foregroundColor(AppConstants.Colors.textTertiary.opacity(0.7))
                .buttonStyle(.plain)
                Button("Already have an account? Sign In") {
                    showingSignIn = true
                }
                .font(.system(size: 13))
                .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
                .buttonStyle(.plain)
            }
            .sheet(isPresented: $showingSignIn) {
                iOSSignInView()
                    .environmentObject(authManager)
            }"""

    if old7a in c:
        c = c.replace(old7a, new7a, 1)
        results.append("✓ Fix 7a: showingSignIn state added")
    else:
        results.append("✗ Fix 7a: isPurchasing state block not found")

    if old7b in c:
        c = c.replace(old7b, new7b, 1)
        results.append("✓ Fix 7b: Sign In link added below Restore Purchases")
    else:
        results.append("✗ Fix 7b: Restore Purchases button block not found")

    write(path, c)

# ─────────────────────────────────────────────────────────────────────────────
# FIX 10: Wrap all print() / debugPrint() in #if DEBUG across Manager, Services, Models
# ─────────────────────────────────────────────────────────────────────────────
import glob

dirs_to_fix = [
    f"{BASE}/Manager",
    f"{BASE}/Services",
    f"{BASE}/Models",
]

total_wrapped = 0
for d in dirs_to_fix:
    for fpath in glob.glob(f"{d}/**/*.swift", recursive=True):
        c = read(fpath)
        lines = c.splitlines(keepends=True)
        new_lines = []
        i = 0
        changed = False
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            # Check if this is a print/debugPrint line not already in #if DEBUG
            if (stripped.startswith("print(") or stripped.startswith("debugPrint(")) and \
               not any("#if DEBUG" in lines[j] for j in range(max(0, i-3), i)):
                # Find the end of the print statement (may span multiple lines)
                stmt_lines = [line]
                # Count parens to handle multi-line print
                open_p = stripped.count("(") - stripped.count(")")
                j = i + 1
                while open_p > 0 and j < len(lines):
                    stmt_lines.append(lines[j])
                    open_p += lines[j].count("(") - lines[j].count(")")
                    j += 1
                # Wrap in #if DEBUG
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
            write(fpath, "".join(new_lines))

results.append(f"✓ Fix 10: Wrapped {total_wrapped} print/debugPrint statements in #if DEBUG")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 15: Verify iOSNotesEmptyState is actually shown in iOSQuickNotesView
# ─────────────────────────────────────────────────────────────────────────────
path = f"{BASE}/Views/iOS/Tabs/iOSQuickNotesView.swift"
c = read(path)
if "iOSNotesEmptyState" in c:
    results.append("✓ Fix 15: iOSNotesEmptyState already wired in iOSQuickNotesView")
else:
    results.append("✗ Fix 15: iOSNotesEmptyState NOT wired — needs manual check")

# Print results
print("\n".join(results))
print("\nDone.")
