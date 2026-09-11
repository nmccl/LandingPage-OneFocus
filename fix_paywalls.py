#!/usr/bin/env python3
"""
Update all paywall/feature list surfaces with the canonical Pro feature list.

Canonical Pro features (shared, both platforms):
1. Unlimited focus sessions & custom durations
2. Unlimited tasks, notes & clipboard
3. Notes with rich text & folders
4. Clipboard favorites
5. Full statistics & streak tracking
6. Custom themes
7. Account sync across devices

macOS-only addition:
- Menu bar mode & global keyboard shortcuts

Changes:
1. UpgradePromptView.swift  — canonical feature list + context-aware headline
2. iOSOnboardingView.swift  — canonical feature list (iOS, no menu bar)
3. OnboardingView.swift     — canonical comparison table (macOS, includes menu bar)
4. HomePage.tsx             — website pricing section
"""

import re

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"
WEB  = "/Users/noahmcclung/Development/Web-Development/OneFocus-LandingPage/src/components/HomePage.tsx"

# ─────────────────────────────────────────────────────────────────────────────
# 1. UpgradePromptView.swift
# ─────────────────────────────────────────────────────────────────────────────
upgrade_path = f"{BASE}/Views/Components/UpgradePromptView.swift"

new_upgrade = '''// UpgradePromptView.swift
// OneFocus — cross-platform upgrade prompt sheet (iOS + macOS)
import SwiftUI

// MARK: - Upgrade Context
enum UpgradeContext {
    case generic
    case sessionLimit
    case taskLimit
    case noteLimit
    case clipboardLimit
    case statsLocked
    case themeLocked

    var headline: String {
        switch self {
        case .generic:        return "Upgrade to Pro"
        case .sessionLimit:   return "You\'ve hit today\'s session limit"
        case .taskLimit:      return "You\'ve reached your task limit"
        case .noteLimit:      return "You\'ve reached your note limit"
        case .clipboardLimit: return "Your clipboard history is full"
        case .statsLocked:    return "Stats are a Pro feature"
        case .themeLocked:    return "Custom themes are a Pro feature"
        }
    }

    var subheadline: String {
        switch self {
        case .generic:        return "Unlock everything OneFocus has to offer."
        case .sessionLimit:   return "Upgrade to keep going — no daily cap."
        case .taskLimit:      return "Upgrade for unlimited tasks."
        case .noteLimit:      return "Upgrade for unlimited notes."
        case .clipboardLimit: return "Upgrade for unlimited clipboard history."
        case .statsLocked:    return "See your full stats, streaks, and trends."
        case .themeLocked:    return "Make OneFocus feel like yours."
        }
    }
}

// MARK: - UpgradePromptView
struct UpgradePromptView: View {
    var context: UpgradeContext = .generic

    @EnvironmentObject private var proAccess: ProAccessManager
    @EnvironmentObject private var storeKit:  StoreKitManager
    @Environment(\\.dismiss) private var dismiss
#if os(macOS)
    @Environment(\\.isGlassPanel)  private var isGlassPanel
    @Environment(\\.panelDismiss)  private var panelDismiss
#endif
    @State private var isPurchasing        = false
    @State private var purchaseErrorMessage: String?
    @State private var isEligibleForTrial:  Bool = true

    private func closeSheet() {
#if os(macOS)
        panelDismiss?() ?? dismiss()
#else
        dismiss()
#endif
    }

    var body: some View {
        VStack(spacing: 0) {
            // ── Header ────────────────────────────────────────────────────
            VStack(spacing: 8) {
                Image(systemName: "crown.fill")
                    .font(.system(size: 32, weight: .medium))
                    .foregroundColor(AppConstants.Colors.primaryAccent)
                    .padding(.bottom, 4)
                Text(context.headline)
                    .font(.system(size: 22, weight: .semibold))
                    .foregroundColor(AppConstants.Colors.textPrimary)
                    .multilineTextAlignment(.center)
                Text(context.subheadline)
                    .font(.system(size: 14))
                    .foregroundColor(AppConstants.Colors.textSecondary)
                    .multilineTextAlignment(.center)
            }
            .padding(.top, 36)
            .padding(.horizontal, 32)
            .padding(.bottom, 28)
            Divider()
            // ── Feature list ──────────────────────────────────────────────
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    UpgradeFeatureRow(icon: "timer",               text: "Unlimited focus sessions & custom durations")
                    UpgradeFeatureRow(icon: "checklist",           text: "Unlimited tasks, notes & clipboard")
                    UpgradeFeatureRow(icon: "note.text",           text: "Notes with rich text & folders")
                    UpgradeFeatureRow(icon: "star.fill",           text: "Clipboard favorites")
                    UpgradeFeatureRow(icon: "chart.bar.fill",      text: "Full statistics & streak tracking")
                    UpgradeFeatureRow(icon: "paintbrush.fill",     text: "Custom themes")
                    UpgradeFeatureRow(icon: "arrow.triangle.2.circlepath", text: "Account sync across devices")
#if os(macOS)
                    UpgradeFeatureRow(icon: "menubar.rectangle",   text: "Menu bar mode & global keyboard shortcuts")
#endif
                }
                .padding(.horizontal, 32)
                .padding(.vertical, 20)
            }
            Divider()
            // ── CTA ───────────────────────────────────────────────────────
            VStack(spacing: 10) {
                if let errMsg = purchaseErrorMessage {
                    Text(errMsg)
                        .font(.system(size: 12))
                        .foregroundColor(.red)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 16)
                }
                Button(action: {
                    isPurchasing = true
                    purchaseErrorMessage = nil
                    _Concurrency.Task {
                        do {
                            try await storeKit.purchase()
                            await proAccess.evaluateProStatus()
                            closeSheet()
                        } catch {
                            purchaseErrorMessage = error.localizedDescription
                        }
                        isPurchasing = false
                    }
                }) {
                    HStack(spacing: 8) {
                        if isPurchasing || storeKit.proProduct == nil {
                            ProgressView()
                                .progressViewStyle(.circular)
                                .scaleEffect(0.7)
                        } else {
                            Image(systemName: "crown.fill")
                                .font(.system(size: 13, weight: .medium))
                        }
                        if storeKit.proProduct != nil && !isPurchasing {
                            Text(
                                isEligibleForTrial
                                ? "Start Free Trial — then \\(storeKit.formattedPrice)"
                                : "Start Pro — \\(storeKit.formattedPrice)"
                            )
                            .font(.system(size: 15, weight: .semibold))
                        } else if isPurchasing {
                            Text("Processing…")
                                .font(.system(size: 15, weight: .semibold))
                        }
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 46)
                    .background(AppConstants.Colors.primaryAccent)
                    .cornerRadius(AppConstants.CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(isPurchasing || storeKit.proProduct == nil)
                Button("Maybe Later") { closeSheet() }
                    .buttonStyle(.plain)
                    .font(.system(size: 13))
                    .foregroundColor(AppConstants.Colors.textTertiary)
                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {
                    Text("After your \\(trialLabel) free trial, you\'ll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                } else {
                    Text("Billed annually · Cancel anytime · Secure payment via Apple")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                }
            }
            .padding(.horizontal, 32)
            .padding(.top, 16)
            .padding(.bottom, 24)
        }
        .background(sheetBackground.ignoresSafeArea())
        .task {
            isEligibleForTrial = await storeKit.checkTrialEligibility()
        }
#if os(macOS)
        .frame(width: 420)
#endif
    }

    @ViewBuilder
    private var sheetBackground: some View {
#if os(macOS)
        if isGlassPanel {
            Color.clear
        } else {
            Color(nsColor: .windowBackgroundColor)
        }
#else
        AppConstants.Colors.backgroundPrimary
#endif
    }
}

// MARK: - UpgradeFeatureRow (shared)
struct UpgradeFeatureRow: View {
    let icon: String
    let text: String
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "checkmark")
                .font(.system(size: 11, weight: .bold))
                .foregroundColor(AppConstants.Colors.primaryAccent)
                .frame(width: 16)
            Image(systemName: icon)
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(AppConstants.Colors.textSecondary)
                .frame(width: 18)
            Text(text)
                .font(.system(size: 13))
                .foregroundColor(AppConstants.Colors.textPrimary)
        }
    }
}
'''

with open(upgrade_path, "w") as f:
    f.write(new_upgrade)
print("✓ UpgradePromptView.swift updated")

# ─────────────────────────────────────────────────────────────────────────────
# 2. iOSOnboardingView.swift — proFeatures array
# ─────────────────────────────────────────────────────────────────────────────
ios_onboard_path = f"{BASE}/Views/Auth/iOSOnboardingView.swift"
with open(ios_onboard_path, "r") as f:
    ios_content = f.read()

old_features = '''    private let proFeatures: [(icon: String, text: String)] = [
        ("infinity",                    "Unlimited focus sessions"),
        ("chart.line.uptrend.xyaxis",   "Full stats & trends"),
        ("flame.fill",                  "Streak tracking"),
        ("bell.badge.fill",             "Custom themes"),
        ("slider.horizontal.3",         "Advanced timer settings"),
        ("icloud.fill",                 "iCloud sync across devices")
    ]'''

new_features = '''    private let proFeatures: [(icon: String, text: String)] = [
        ("timer",                           "Unlimited focus sessions & custom durations"),
        ("checklist",                       "Unlimited tasks, notes & clipboard"),
        ("note.text",                       "Notes with rich text & folders"),
        ("star.fill",                       "Clipboard favorites"),
        ("chart.bar.fill",                  "Full statistics & streak tracking"),
        ("paintbrush.fill",                 "Custom themes"),
        ("arrow.triangle.2.circlepath",     "Account sync across devices")
    ]'''

if old_features in ios_content:
    ios_content = ios_content.replace(old_features, new_features, 1)
    with open(ios_onboard_path, "w") as f:
        f.write(ios_content)
    print("✓ iOSOnboardingView.swift proFeatures updated")
else:
    print("✗ iOSOnboardingView.swift — old features block not found exactly, checking...")
    if "bell.badge.fill" in ios_content:
        print("  (bell.badge.fill still present)")
    if "proFeatures" in ios_content:
        # Show what's there
        start = ios_content.find("private let proFeatures")
        print(f"  Found proFeatures at char {start}:")
        print(repr(ios_content[start:start+400]))

# ─────────────────────────────────────────────────────────────────────────────
# 3. OnboardingView.swift (macOS) — featureGroups comparison table
# ─────────────────────────────────────────────────────────────────────────────
mac_onboard_path = f"{BASE}/Views/Auth/OnboardingView.swift"
with open(mac_onboard_path, "r") as f:
    mac_content = f.read()

# Find and replace the featureGroups array
old_groups_start = "    private let featureGroups: [FeatureGroup] = ["
old_groups_end = "    ]"  # last ] of the array

# Locate the block
start_idx = mac_content.find(old_groups_start)
if start_idx == -1:
    print("✗ OnboardingView.swift — featureGroups not found")
else:
    # Find the closing bracket of the array (count brackets)
    depth = 0
    end_idx = start_idx
    for i, ch in enumerate(mac_content[start_idx:], start_idx):
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end_idx = i + 1
                break

    new_groups = '''    private let featureGroups: [FeatureGroup] = [
        FeatureGroup(
            category: "Focus Timer",
            freeItems: [
                "5 sessions per day",
                "Default 25 / 5 / 15 preset"
            ],
            proItems: [
                "Unlimited sessions",
                "Custom focus & break durations"
            ]
        ),
        FeatureGroup(
            category: "Tasks",
            freeItems: [
                "Up to 20 active tasks"
            ],
            proItems: [
                "Unlimited tasks",
                "Categories & folders"
            ]
        ),
        FeatureGroup(
            category: "Quick Notes",
            freeItems: [
                "Up to 15 notes",
                "Plain text"
            ],
            proItems: [
                "Unlimited notes",
                "Rich text & folders"
            ]
        ),
        FeatureGroup(
            category: "Clipboard History",
            freeItems: [
                "Last 20 items"
            ],
            proItems: [
                "Unlimited history",
                "Favorites"
            ]
        ),
        FeatureGroup(
            category: "Statistics & Themes",
            freeItems: [
                "Light & dark mode"
            ],
            proItems: [
                "Full daily, weekly & monthly stats",
                "Streak & trend tracking",
                "Custom themes"
            ]
        ),
        FeatureGroup(
            category: "Sync & Power Features",
            freeItems: [],
            proItems: [
                "Account sync across devices",
                "Menu bar mode",
                "Global keyboard shortcuts"
            ]
        )
    ]'''

    mac_content = mac_content[:start_idx] + new_groups + mac_content[end_idx:]
    with open(mac_onboard_path, "w") as f:
        f.write(mac_content)
    print("✓ OnboardingView.swift featureGroups updated")

# ─────────────────────────────────────────────────────────────────────────────
# 4. HomePage.tsx — website Pro feature list
# ─────────────────────────────────────────────────────────────────────────────
with open(WEB, "r") as f:
    web_content = f.read()

old_pro_list = '''                "Everything in Free",
                "Unlimited tasks, notes & clipboard",
                "Unlimited focus sessions",
                "iCloud sync across Mac & iPhone",
                "Menu bar widget",
                "Custom themes & Liquid Glass",
                "Advanced statistics & streaks",
                "Keyboard shortcuts",
                "Data export",
                "Priority support",'''

new_pro_list = '''                "Everything in Free",
                "Unlimited focus sessions & custom durations",
                "Unlimited tasks, notes & clipboard",
                "Notes with rich text & folders",
                "Clipboard favorites",
                "Full statistics & streak tracking",
                "Custom themes",
                "Account sync across devices",
                "Menu bar mode & global keyboard shortcuts",'''

if old_pro_list in web_content:
    web_content = web_content.replace(old_pro_list, new_pro_list, 1)
    with open(WEB, "w") as f:
        f.write(web_content)
    print("✓ HomePage.tsx Pro feature list updated")
else:
    print("✗ HomePage.tsx — old Pro list not found exactly")
    if "iCloud sync" in web_content:
        print("  (iCloud sync still present)")
    if "Priority support" in web_content:
        print("  (Priority support still present)")

# Also fix the FAQ answer that mentions iCloud
old_faq = '"Pro gives you unlimited focus sessions, tasks, notes, and clipboard history, plus custom themes, iCloud sync across all your devices, the menu bar widget, keyboard shortcuts, advanced statistics, and more."'
new_faq = '"Pro gives you unlimited focus sessions with custom durations, unlimited tasks, notes, and clipboard history, rich text notes with folders, clipboard favorites, full statistics and streak tracking, custom themes, account sync across devices, menu bar mode, and global keyboard shortcuts."'

if old_faq in web_content:
    web_content = web_content.replace(old_faq, new_faq, 1)
    with open(WEB, "w") as f:
        f.write(web_content)
    print("✓ HomePage.tsx FAQ Pro answer updated")
else:
    # Try to update it from the already-modified content
    with open(WEB, "r") as f:
        web_content2 = f.read()
    if old_faq in web_content2:
        web_content2 = web_content2.replace(old_faq, new_faq, 1)
        with open(WEB, "w") as f:
            f.write(web_content2)
        print("✓ HomePage.tsx FAQ Pro answer updated (second pass)")
    else:
        print("  (FAQ answer already updated or not found — skipping)")

print("\nDone.")
