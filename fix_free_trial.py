"""
Fix: Add free trial awareness to the paywall UI across all three files:
  1. StoreKitManager.swift   — add trialLabel + isEligibleForTrial
  2. OnboardingView.swift    — update macOS PaywallPage CTA + disclosure
  3. iOSOnboardingView.swift — update iOS paywall CTA + disclosure
  4. UpgradePromptView.swift — update in-app upgrade prompt CTA + disclosure
"""
import sys

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# ─────────────────────────────────────────────────────────────────────────────
# 1. StoreKitManager — add trialLabel and isEligibleForTrial
# ─────────────────────────────────────────────────────────────────────────────
sk_path = BASE + "/Manager/StoreKitManager.swift"
with open(sk_path) as f:
    sk = f.read()

OLD_FORMATTED_PRICE = (
    "    // MARK: - Formatted Price\n\n"
    "    /// Returns the formatted price string for the pro product (e.g. \"$12.99/year\").\n"
    "    var formattedPrice: String {\n"
    "        guard let product = proProduct else { return AppConstants.Pro.subscriptionPrice }\n"
    "        return \"\\(product.displayPrice)/year\"\n"
    "    }"
)

NEW_FORMATTED_PRICE = (
    "    // MARK: - Formatted Price\n"
    "    /// Returns the formatted price string for the pro product (e.g. \"$12.99/year\").\n"
    "    var formattedPrice: String {\n"
    "        guard let product = proProduct else { return AppConstants.Pro.subscriptionPrice }\n"
    "        return \"\\(product.displayPrice)/year\"\n"
    "    }\n"
    "\n"
    "    // MARK: - Trial Label\n"
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
    "    // MARK: - Trial Eligibility\n"
    "    /// Async check — true when the current user has never redeemed the introductory offer.\n"
    "    /// Falls back to `true` when the product or subscription info is unavailable.\n"
    "    func checkTrialEligibility() async -> Bool {\n"
    "        guard let product = proProduct,\n"
    "              let subscription = product.subscription else { return true }\n"
    "        return await (subscription.isEligibleForIntroOffer)\n"
    "    }"
)

if "trialPeriodLabel" in sk:
    print("Step 1 (StoreKitManager trial helpers): already applied, skipping")
elif OLD_FORMATTED_PRICE in sk:
    sk = sk.replace(OLD_FORMATTED_PRICE, NEW_FORMATTED_PRICE, 1)
    print("Step 1 (StoreKitManager trial helpers): OK")
else:
    print("Step 1 ERROR: Could not find formattedPrice anchor")
    idx = sk.find("// MARK: - Formatted Price")
    print(repr(sk[idx:idx+200]))
    sys.exit(1)

with open(sk_path, "w") as f:
    f.write(sk)

# ─────────────────────────────────────────────────────────────────────────────
# 2. OnboardingView.swift — macOS PaywallPage
# ─────────────────────────────────────────────────────────────────────────────
mac_path = BASE + "/Views/Auth/OnboardingView.swift"
with open(mac_path) as f:
    mac = f.read()

# Add isEligibleForTrial state to PaywallPage
OLD_PAYWALL_STATE = (
    "struct PaywallPage: View {\n\n"
    "    let onUpgrade: () -> Void\n"
    "    let onSkip: () -> Void\n"
    "\n"
    "    @EnvironmentObject private var storeKit: StoreKitManager\n"
    "    @EnvironmentObject private var proAccess: ProAccessManager\n"
    "\n"
    "    @State private var appeared = false\n"
    "    @State private var isPurchasing = false\n"
    "    @State private var purchaseErrorMessage: String?"
)

NEW_PAYWALL_STATE = (
    "struct PaywallPage: View {\n\n"
    "    let onUpgrade: () -> Void\n"
    "    let onSkip: () -> Void\n"
    "\n"
    "    @EnvironmentObject private var storeKit: StoreKitManager\n"
    "    @EnvironmentObject private var proAccess: ProAccessManager\n"
    "\n"
    "    @State private var appeared = false\n"
    "    @State private var isPurchasing = false\n"
    "    @State private var purchaseErrorMessage: String?\n"
    "    /// True when this user has never redeemed the introductory offer.\n"
    "    @State private var isEligibleForTrial: Bool = true"
)

if OLD_PAYWALL_STATE in mac:
    mac = mac.replace(OLD_PAYWALL_STATE, NEW_PAYWALL_STATE, 1)
    print("Step 2a (macOS PaywallPage state): OK")
else:
    print("Step 2a ERROR: Could not find PaywallPage state anchor")
    idx = mac.find("struct PaywallPage")
    print(repr(mac[idx:idx+400]))
    sys.exit(1)

# Replace the CTA button label and disclosure text
OLD_MAC_CTA = (
    "                        Text(isPurchasing ? \"Processing\\u2026\" : \"Start Pro \\u2014 \\(storeKit.formattedPrice)\")\n"
    "                            .font(.system(size: 15, weight: .semibold))\n"
    "                    }\n"
    "                    .foregroundColor(.white)\n"
    "                    .frame(maxWidth: .infinity)\n"
    "                    .frame(height: 46)\n"
    "                    .background(AppConstants.Colors.primaryAccent)\n"
    "                    .cornerRadius(AppConstants.CornerRadius.medi                "                }\n"
    "                .buttonStyle(.plain)\n"
    "                .disabled(isPurchasing)\n\n"
    "                Button(action: onSkip) {\n"                   Text(\"Continue with Free\")\n"
    "                        .font(.system(size: 13))\n"
    "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                }\n"
    "                .buttonStyle(.plain)\n"
    "                Text(\"Billed annually \\u00b7 Cancel anytime \\u00b7 Secure payment via Apple\")\n"
    "                    .font(.system(size: 11))\n"
    "                    .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                    .multilineTextAlignment(.center)"
)

NEW_MAC_CTA = (
    "                        Text(isPurchasing ? \"Processing\\u2026\" : (\n"
    "                            isEligibleForTrial\n"
    "                            ? \"Start Free Trial \\u2014 then \\(storeKit.formattedPrice)\"\n"
    "                            : \"Start Pro \\u2014 \\(storeKit.formattedPrice)\"\n"
    "                        ))\n"
    "                            .font(.system(size: 15, weight: .semibold))\n"
    "                    }\n"
    "                    .foregroundColor(.white)\n"
    "                    .frame(maxWidth: .infinity)\n"
    "                    .frame(height: 46)\n"
    "                    .background(AppConstants.Colors.primaryAccent)\n"
    "                    .cornerRadius(AppConstants.CornerRadius.medium)\n"
    "                }\n"
    "                .buttonStyle(.plain)\n"
    "                .disabled(isPurchasing)\n"
    "                Button(action: onSkip) {\n"
    "                    Text(\"Continue with Free\")\n"
    "                        .font(.system(size: 13))\n"
    "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                }\n"
    "                .buttonStyle(.plain)\n"
    "                // Auto-charge disclosure\n"
    "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {\n"
    "                    Text(\"After your \\(trialLabel) free trial, you\\'ll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.\")\n"
    "                        .font(.system(size: 11))\n"
    "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                        .multilineTextAlignment(.center)\n"
    "                } else {\n"
    "                    Text(\"Billed annually \\u00b7 Cancel anytime \\u00b7 Secure payment via Apple\")\n"
    "                        .font(.system(size: 11))\n"
    "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                        .multilineTextAlignment(.center)\n"
    "                }"
)

if OLD_MAC_CTA in mac:
    mac = mac.replace(OLD_MAC_CTA, NEW_MAC_CTA, 1)
    print("Step 2b (macOS PaywallPage CTA + disclosure): OK")
else:
    print("Step 2b ERROR: Could not find macOS CTA anchor")
    idx = mac.find("Start Pro")
    print(repr(mac[idx-50:idx+300]))
    sys.exit(1)

# Add .task to load trial eligibility in the PaywallPage onAppear
OLD_MAC_ONAPPEAR = (
    "        .onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n"
    "        }\n"
    "    }\n"
    "    // MARK: - Plan Column"
)

NEW_MAC_ONAPPEAR = (
    "        .onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n"
    "        }\n"
    "        .task {\n"
    "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
    "        }\n"
    "    }\n"
    "    // MARK: - Plan Column"
)

if OLD_MAC_ONAPPEAR in mac:
    mac = mac.replace(OLD_MAC_ONAPPEAR, NEW_MAC_ONAPPEAR, 1)
    print("Step 2c (macOS PaywallPage .task): OK")
else:
    print("Step 2c ERROR: Could not find macOS onAppear anchor")
    idx = mac.find(".onAppear")
    print(repr(mac[idx:idx+200]))
    sys.exit(1)

with open(mac_path, "w") as f:
    f.write(mac)

# ─────────────────────────────────────────────────────────────────────────────
# 3. iOSOnboardingView.swift — iOS paywall
# ─────────────────────────────────────────────────────────────────────────────
ios_path = BASE + "/Views/Auth/iOSOnboardingView.swift"
with open(ios_path) as f:
    ios = f.read()

# Find the iOS paywall struct — it has isPurchasing state
OLD_IOS_STATE = (
    "    @State private var isPurchasing = false\n"
    "    let onComplete: () -> Void"
)

NEW_IOS_STATE = (
    "    @State private var isPurchasing = false\n"
    "    @State private var isEligibleForTrial: Bool = true\n"
    "    let onComplete: () -> Void"
)

if OLD_IOS_STATE in ios:
    ios = ios.replace(OLD_IOS_STATE, NEW_IOS_STATE, 1)
    print("Step 3a (iOS paywall state): OK")
else:
    print("Step 3a ERROR: Could not find iOS paywall state anchor")
    idx = ios.find("isPurchasing = false")
    print(repr(ios[idx-50:idx+150]))
    sys.exit(1)

# Replace the iOS CTA button label
OLD_IOS_CTA = (
    "                        Text(\"Upgrade to Pro\")\n"
    "                            .font(.system(size: 17, weight: .semibold))\n"
    "                    }\n"
    "                    .foregroundColor(AppConstants.Colors.backgroundPrimary)\n"
    "                    .frame(maxWidth: .infinity)\n"
    "                    .padding(.vertical, 16)\n"
    "                    .background(AppConstants.Colors.primaryAccent)\n"
    "                    .cornerRadius(AppConstants.CornerRadius.large)\n"
    "                }\n"
    "                .buttonStyle(.plain)\n"
    "                .disabled(isPurchasing)\n"
    "                Button(\"Continue with Free\") {\n"
    "                    onComplete()\n"
    "                }\n"
    "                .font(.system(size: 15))\n"
    "                .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                .buttonStyle(.plain)\n"
    "                Button(\"Restore Purchases\") {\n"
    "                    _Concurrency.Task {\n"
    "                        await storeKit.restorePurchases()\n"
    "                        onComplete()\n"
    "                    }\n"
    "                }\n"
    "                .font(.system(size: 13))\n"
    "                .foregroundColor(AppConstants.Colors.textTertiary.opacity(0.7))\n"
    "                .buttonStyle(.plain)"
)

NEW_IOS_CTA = (
    "                        Text(isEligibleForTrial\n"
    "                             ? \"Start Free Trial\"\n"
    "                             : \"Upgrade to Pro\")\n"
    "                            .font(.system(size: 17, weight: .semibold))\n"
    "                    }\n"
    "                    .foregroundColor(AppConstants.Colors.backgroundPrimary)\n"
    "                    .frame(maxWidth: .infinity)\n"
    "                    .padding(.vertical, 16)\n"
    "                    .background(AppConstants.Colors.primaryAccent)\n"
    "                    .cornerRadius(AppConstants.CornerRadius.large)\n"
    "                }\n"
    "                .buttonStyle(.plain)\n"
    "                .disabled(isPurchasing)\n"
    "                // Auto-charge disclosure\n"
    "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {\n"
    "                    Text(\"After your \\(trialLabel) free trial, you\\'ll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.\")\n"
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
    "                .buttonStyle(.plain)\n"
    "                Button(\"Restore Purchases\") {\n"
    "                    _Concurrency.Task {\n"
    "                        await storeKit.restorePurchases()\n"
    "                        onComplete()\n"
    "                    }\n"
    "                }\n"
    "                .font(.system(size: 13))\n"
    "                .foregroundColor(AppConstants.Colors.textTertiary.opacity(0.7))\n"
    "                .buttonStyle(.plain)"
)

if OLD_IOS_CTA in ios:
    ios = ios.replace(OLD_IOS_CTA, NEW_IOS_CTA, 1)
    print("Step 3b (iOS paywall CTA + disclosure): OK")
else:
    print("Step 3b ERROR: Could not find iOS CTA anchor")
    idx = ios.find("Upgrade to Pro")
    print(repr(ios[idx-100:idx+400]))
    sys.exit(1)

# Add .task to iOS paywall to check trial eligibility
OLD_IOS_ONAPPEAR = (
    "        .onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.5)) { appeared = true }\n"
    "        }"
)

NEW_IOS_ONAPPEAR = (
    "        .onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.5)) { appeared = true }\n"
    "        }\n"
    "        .task {\n"
    "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
    "        }"
)

if OLD_IOS_ONAPPEAR in ios:
    ios = ios.replace(OLD_IOS_ONAPPEAR, NEW_IOS_ONAPPEAR, 1)
    print("Step 3c (iOS paywall .task): OK")
else:
    print("Step 3c WARNING: Could not find iOS onAppear anchor — skipping")

with open(ios_path, "w") as f:
    f.write(ios)

# ─────────────────────────────────────────────────────────────────────────────
# 4. UpgradePromptView.swift — in-app upgrade prompt
# ─────────────────────────────────────────────────────────────────────────────
up_path = BASE + "/Views/Components/UpgradePromptView.swift"
with open(up_path) as f:
    up = f.read()

# Add isEligibleForTrial state
OLD_UP_STATE = (
    "    @State private var isPurchasing = false\n"
    "    @State private var purchaseErrorMessage: String?"
)

NEW_UP_STATE = (
    "    @State private var isPurchasing = false\n"
    "    @State private var purchaseErrorMessage: String?\n"
    "    @State private var isEligibleForTrial: Bool = true"
)

if OLD_UP_STATE in up:
    up = up.replace(OLD_UP_STATE, NEW_UP_STATE, 1)
    print("Step 4a (UpgradePromptView state): OK")
else:
    print("Step 4a ERROR: Could not find UpgradePromptView state anchor")
    sys.exit(1)

# Replace button label
OLD_UP_LABEL = (
    "                        Text(isPurchasing ? \"Processing\\u2026\" : \"Start Pro \\u2014 \\(storeKit.formattedPrice)\")\n"
    "                            .font(.system(size: 15, weight: .semibold))"
)

NEW_UP_LABEL = (
    "                        Text(isPurchasing ? \"Processing\\u2026\" : (\n"
    "                            isEligibleForTrial\n"
    "                            ? \"Start Free Trial \\u2014 then \\(storeKit.formattedPrice)\"\n"
    "                            : \"Start Pro \\u2014 \\(storeKit.formattedPrice)\"\n"
    "                        ))\n"
    "                            .font(.system(size: 15, weight: .semibold))"
)

if OLD_UP_LABEL in up:
    up = up.replace(OLD_UP_LABEL, NEW_UP_LABEL, 1)
    print("Step 4b (UpgradePromptView CTA label): OK")
else:
    print("Step 4b ERROR: Could not find UpgradePromptView CTA label")
    idx = up.find("Start Pro")
    print(repr(up[idx-30:idx+200]))
    sys.exit(1)

# Add disclosure text and .task after the existing footer text
OLD_UP_FOOTER = (
    "                Text(\"Billed annually \\u00b7 Cancel anytime \\u00b7 Secure payment via Apple\")\n"
    "                    .font(.system(size: 11))\n"
    "                    .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                    .multilineTextAlignment(.center)"
)

NEW_UP_FOOTER = (
    "                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {\n"
    "                    Text(\"After your \\(trialLabel) free trial, you\\'ll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.\")\n"
    "                        .font(.system(size: 11))\n"
    "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                        .multilineTextAlignment(.center)\n"
    "                } else {\n"
    "                    Text(\"Billed annually \\u00b7 Cancel anytime \\u00b7 Secure payment via Apple\")\n"
    "                        .font(.system(size: 11))\n"
    "                        .foregroundColor(AppConstants.Colors.textTertiary)\n"
    "                        .multilineTextAlignment(.center)\n"
    "                }"
)

if OLD_UP_FOOTER in up:
    up = up.replace(OLD_UP_FOOTER, NEW_UP_FOOTER, 1)
    print("Step 4c (UpgradePromptView disclosure): OK")
else:
    print("Step 4c ERROR: Could not find UpgradePromptView footer")
    sys.exit(1)

# Add .task to UpgradePromptView
OLD_UP_ONAPPEAR = ".onAppear {\n            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n        }"
NEW_UP_ONAPPEAR = (
    ".onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n"
    "        }\n"
    "        .task {\n"
    "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
    "        }"
)

if OLD_UP_ONAPPEAR in up:
    up = up.replace(OLD_UP_ONAPPEAR, NEW_UP_ONAPPEAR, 1)
    print("Step 4d (UpgradePromptView .task): OK")
else:
    print("Step 4d WARNING: Could not find UpgradePromptView onAppear — skipping")

with open(up_path, "w") as f:
    f.write(up)

print("\nAll steps complete.")
