"""
Fix: Add free trial awareness to the paywall UI.
Steps:
  1. StoreKitManager — add trialPeriodLabel + checkTrialEligibility (idempotent)
  2. OnboardingView (macOS) — add isEligibleForTrial state, update CTA + disclosure + .task
  3. iOSOnboardingView — add isEligibleForTrial state, update CTA + disclosure + .task
  4. UpgradePromptView — add isEligibleForTrial state, update CTA + disclosure + .task
"""
import sys

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"


def replace_once(content, old, new, label):
    if old in content:
        result = content.replace(old, new, 1)
        print(f"  {label}: OK")
        return result
    else:
        print(f"  {label} ERROR: anchor not found")
        # Find nearest context
        first_line = old.strip().split("\n")[0][:60]
        idx = content.find(first_line)
        if idx != -1:
            print(f"  Context: {repr(content[idx:idx+200])}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 1. StoreKitManager
# ─────────────────────────────────────────────────────────────────────────────
print("=== Step 1: StoreKitManager ===")
sk_path = BASE + "/Manager/StoreKitManager.swift"
with open(sk_path) as f:
    sk = f.read()

if "trialPeriodLabel" in sk:
    print("  Already applied, skipping")
else:
    old = (
        "    // MARK: - Formatted Price\n"
        "    /// Returns the formatted price string for the pro product (e.g. \"$12.99/year\").\n"
        "    var formattedPrice: String {\n"
        "        guard let product = proProduct else { return AppConstants.Pro.subscriptionPrice }\n"
        "        return \"\\(product.displayPrice)/year\"\n"
        "    }"
    )
    new = (
        "    // MARK: - Formatted Price\n"
        "    /// Returns the formatted price string for the pro product (e.g. \"$12.99/year\").\n"
        "    var formattedPrice: String {\n"
        "        guard let product = proProduct else { return AppConstants.Pro.subscriptionPrice }\n"
        "        return \"\\(product.displayPrice)/year\"\n"
        "    }\n"
        "\n"
        "    // MARK: - Trial Helpers\n"
        "    /// Human-readable label for the introductory offer period, e.g. \"7 days\".\n"
        "    /// Returns nil when no introductory offer is configured on the product.\n"
        "    var trialPeriodLabel: String? {\n"
        "        guard let offer = proProduct?.subscription?.introductoryOffer else { return nil }\n"
        "        guard offer.paymentMode == .freeTrial else { return nil }\n"
        "        let period = offer.period\n"
        "        switch period.unit {\n"
        "        case .day:   return period.value == 1 ? \"1 day\"   : \"\\(period.value) days\"\n"
        "        case .week:  return period.value == 1 ? \"1 week\"  : \"\\(period.value) weeks\"\n"
        "        case .month: return period.value == 1 ? \"1 month\" : \"\\(period.value) months\"\n"
        "        case .year:  return period.value == 1 ? \"1 year\"  : \"\\(period.value) years\"\n"
        "        @unknown default: return \"\\(period.value) \\(period.unit)\"\n"
        "        }\n"
        "    }\n"
        "\n"
        "    /// Async check — true when the current user has never redeemed the introductory offer.\n"
        "    /// Falls back to `true` when the product or subscription info is unavailable.\n"
        "    func checkTrialEligibility() async -> Bool {\n"
        "        guard let product = proProduct,\n"
        "              let subscription = product.subscription else { return true }\n"
        "        return await (subscription.isEligibleForIntroOffer)\n"
        "    }"
    )
    # The file may have a blank line after the MARK comment
    if old not in sk:
        old = old.replace(
            "    // MARK: - Formatted Price\n    ///",
            "    // MARK: - Formatted Price\n\n    ///"
        )
        new = new.replace(
            "    // MARK: - Formatted Price\n    ///",
            "    // MARK: - Formatted Price\n\n    ///"
        )
    sk = replace_once(sk, old, new, "formattedPrice → add trial helpers")
    if sk is None:
        sys.exit(1)
    with open(sk_path, "w") as f:
        f.write(sk)

# ─────────────────────────────────────────────────────────────────────────────
# 2. OnboardingView.swift (macOS PaywallPage)
# ─────────────────────────────────────────────────────────────────────────────
print("=== Step 2: macOS OnboardingView ===")
mac_path = BASE + "/Views/Auth/OnboardingView.swift"
with open(mac_path) as f:
    mac = f.read()

# 2a — add isEligibleForTrial state (idempotent)
if "isEligibleForTrial" not in mac:
    old = (
        "    @State private var isPurchasing = false\n"
        "    @State private var purchaseErrorMessage: String?"
    )
    new = (
        "    @State private var isPurchasing = false\n"
        "    @State private var purchaseErrorMessage: String?\n"
        "    /// True when this user has never redeemed the introductory offer.\n"
        "    @State private var isEligibleForTrial: Bool = true"
    )
    mac = replace_once(mac, old, new, "add isEligibleForTrial state")
    if mac is None:
        sys.exit(1)
else:
    print("  isEligibleForTrial already present, skipping state")

# 2b — update CTA button label
if "Start Free Trial" not in mac:
    old = (
        "                        Text(isPurchasing ? \"Processing\u2026\" : \"Start Pro \u2014 \\(storeKit.formattedPrice)\")\n"
        "                            .font(.system(size: 15, weight: .semibold))"
    )
    new = (
        "                        Text(isPurchasing ? \"Processing\u2026\" : (\n"
        "                            isEligibleForTrial\n"
        "                            ? \"Start Free Trial \u2014 then \\(storeKit.formattedPrice)\"\n"
        "                            : \"Start Pro \u2014 \\(storeKit.formattedPrice)\"\n"
        "                        ))\n"
        "                            .font(.system(size: 15, weight: .semibold))"
    )
    mac = replace_once(mac, old, new, "update CTA label")
    if mac is None:
        sys.exit(1)
else:
    print("  CTA label already updated, skipping")

# 2c — replace disclosure text
if "Cancel before the trial ends" not in mac:
    old = (
        "                Text(\"Billed annually \u00b7 Cancel anytime \u00b7 Secure payment via Apple\")\n"
        "                    .font(.system(size: 11))\n"
        "                    .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                    .multilineTextAlignment(.center)"
    )
    new = (
        "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {\n"
        "                    Text(\"After your \\(trialLabel) free trial, you'll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.\")\n"
        "                        .font(.system(size: 11))\n"
        "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                        .multilineTextAlignment(.center)\n"
        "                } else {\n"
        "                    Text(\"Billed annually \u00b7 Cancel anytime \u00b7 Secure payment via Apple\")\n"
        "                        .font(.system(size: 11))\n"
        "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                        .multilineTextAlignment(.center)\n"
        "                }"
    )
    mac = replace_once(mac, old, new, "update disclosure text")
    if mac is None:
        sys.exit(1)
else:
    print("  Disclosure already updated, skipping")

# 2d — add .task for trial eligibility check
if "checkTrialEligibility" not in mac:
    # Find the onAppear in PaywallPage (it's the last onAppear before "// MARK: - Plan Column")
    mark_idx = mac.find("    // MARK: - Plan Column")
    onappear_idx = mac.rfind(".onAppear {", 0, mark_idx)
    close_idx = mac.find("        }\n    }\n    // MARK: - Plan Column", onappear_idx)
    if close_idx != -1:
        insert_at = close_idx + len("        }\n")
        task_code = (
            "        .task {\n"
            "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
            "        }\n"
        )
        mac = mac[:insert_at] + task_code + mac[insert_at:]
        print("  add .task for trial eligibility: OK")
    else:
        print("  WARNING: Could not find PaywallPage onAppear close — skipping .task")
else:
    print("  .task already present, skipping")

with open(mac_path, "w") as f:
    f.write(mac)

# ─────────────────────────────────────────────────────────────────────────────
# 3. iOSOnboardingView.swift
# ─────────────────────────────────────────────────────────────────────────────
print("=== Step 3: iOS iOSOnboardingView ===")
ios_path = BASE + "/Views/Auth/iOSOnboardingView.swift"
with open(ios_path) as f:
    ios = f.read()

# 3a — add isEligibleForTrial state
if "isEligibleForTrial" not in ios:
    old = (
        "    @State private var isPurchasing = false\n\n"
        "    private let proFeatures"
    )
    new = (
        "    @State private var isPurchasing = false\n"
        "    @State private var isEligibleForTrial: Bool = true\n\n"
        "    private let proFeatures"
    )
    ios = replace_once(ios, old, new, "add isEligibleForTrial state")
    if ios is None:
        sys.exit(1)
else:
    print("  isEligibleForTrial already present, skipping state")

# 3b — update CTA button label
if "Start Free Trial" not in ios:
    old = (
        "                            Text(\"Upgrade to Pro\")\n"
        "                                .font(.system(size: 17, weight: .semibold))"
    )
    new = (
        "                            Text(isEligibleForTrial ? \"Start Free Trial\" : \"Upgrade to Pro\")\n"
        "                                .font(.system(size: 17, weight: .semibold))"
    )
    ios = replace_once(ios, old, new, "update CTA label")
    if ios is None:
        sys.exit(1)
else:
    print("  CTA label already updated, skipping")

# 3c — add disclosure after the primary button block, before "Continue with Free"
if "Cancel before the trial ends" not in ios:
    old = (
        "                Button(\"Continue with Free\") {\n"
        "                    onComplete()\n"
        "                }\n"
        "                .font(.system(size: 15))\n"
        "                .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                .buttonStyle(.plain)"
    )
    new = (
        "                // Auto-charge disclosure\n"
        "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {\n"
        "                    Text(\"After your \\(trialLabel) free trial, you'll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.\")\n"
        "                        .font(.system(size: 12))\n"
        "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                        .multilineTextAlignment(.center)\n"
        "                        .padding(.horizontal, 8)\n"
        "                }\n"
        "                Button(\"Continue with Free\") {\n"
        "                    onComplete()\n"
        "                }\n"
        "                .font(.system(size: 15))\n"
        "                .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                .buttonStyle(.plain)"
    )
    ios = replace_once(ios, old, new, "add disclosure text")
    if ios is None:
        sys.exit(1)
else:
    print("  Disclosure already present, skipping")

# 3d — add .task
if "checkTrialEligibility" not in ios:
    old = (
        "        .onAppear {\n"
        "            withAnimation(.easeOut(duration: 0.5)) { appeared = true }\n"
        "        }"
    )
    new = (
        "        .onAppear {\n"
        "            withAnimation(.easeOut(duration: 0.5)) { appeared = true }\n"
        "        }\n"
        "        .task {\n"
        "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
        "        }"
    )
    ios = replace_once(ios, old, new, "add .task")
    if ios is None:
        print("  WARNING: .task not added — onAppear anchor not found")
else:
    print("  .task already present, skipping")

with open(ios_path, "w") as f:
    f.write(ios)

# ─────────────────────────────────────────────────────────────────────────────
# 4. UpgradePromptView.swift
# ─────────────────────────────────────────────────────────────────────────────
print("=== Step 4: UpgradePromptView ===")
up_path = BASE + "/Views/Components/UpgradePromptView.swift"
with open(up_path) as f:
    up = f.read()

# 4a — add isEligibleForTrial state
if "isEligibleForTrial" not in up:
    old = (
        "    @State private var isPurchasing        = false\n"
        "    @State private var purchaseErrorMessage: String?"
    )
    new = (
        "    @State private var isPurchasing        = false\n"
        "    @State private var purchaseErrorMessage: String?\n"
        "    @State private var isEligibleForTrial:  Bool = true"
    )
    up = replace_once(up, old, new, "add isEligibleForTrial state")
    if up is None:
        sys.exit(1)
else:
    print("  isEligibleForTrial already present, skipping state")

# 4b — update CTA label
if "Start Free Trial" not in up:
    old = (
        "                        Text(isPurchasing ? \"Processing\u2026\" : \"Start Pro \u2014 \\(storeKit.formattedPrice)\")\n"
        "                            .font(.system(size: 15, weight: .semibold))"
    )
    new = (
        "                        Text(isPurchasing ? \"Processing\u2026\" : (\n"
        "                            isEligibleForTrial\n"
        "                            ? \"Start Free Trial \u2014 then \\(storeKit.formattedPrice)\"\n"
        "                            : \"Start Pro \u2014 \\(storeKit.formattedPrice)\"\n"
        "                        ))\n"
        "                            .font(.system(size: 15, weight: .semibold))"
    )
    up = replace_once(up, old, new, "update CTA label")
    if up is None:
        sys.exit(1)
else:
    print("  CTA label already updated, skipping")

# 4c — replace disclosure text
if "Cancel before the trial ends" not in up:
    old = (
        "                Text(\"Billed annually \u00b7 Cancel anytime \u00b7 Secure payment via Apple\")\n"
        "                    .font(.system(size: 11))\n"
        "                    .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                    .multilineTextAlignment(.center)"
    )
    new = (
        "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {\n"
        "                    Text(\"After your \\(trialLabel) free trial, you'll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.\")\n"
        "                        .font(.system(size: 11))\n"
        "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                        .multilineTextAlignment(.center)\n"
        "                } else {\n"
        "                    Text(\"Billed annually \u00b7 Cancel anytime \u00b7 Secure payment via Apple\")\n"
        "                        .font(.system(size: 11))\n"
        "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
        "                        .multilineTextAlignment(.center)\n"
        "                }"
    )
    up = replace_once(up, old, new, "update disclosure text")
    if up is None:
        sys.exit(1)
else:
    print("  Disclosure already updated, skipping")

# 4d — add .task
if "checkTrialEligibility" not in up:
    old = ".onAppear {\n            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n        }"
    new = (
        ".onAppear {\n"
        "            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n"
        "        }\n"
        "        .task {\n"
        "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
        "        }"
    )
    up = replace_once(up, old, new, "add .task")
    if up is None:
        print("  WARNING: .task not added")
else:
    print("  .task already present, skipping")

with open(up_path, "w") as f:
    f.write(up)

print("\nAll steps complete.")
