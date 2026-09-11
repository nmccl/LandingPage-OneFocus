import re

# ── Fix 1: AuthManager — robust window lookup for iPad multi-scene ────────────
auth_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/AuthManager.swift"
with open(auth_path) as f:
    content = f.read()

old_window = """                #if os(iOS)
                self.cachedPresentationWindow = UIApplication.shared.connectedScenes
                    .compactMap { $0 as? UIWindowScene }
                    .flatMap { $0.windows }
                    .first { $0.isKeyWindow }
                #elseif os(macOS)"""

new_window = """                #if os(iOS)
                // On iPad, multiple UIWindowScenes may exist (multi-window).
                // Search all scenes for the key window, falling back to the
                // foreground-active scene's first window if none is key.
                self.cachedPresentationWindow = UIApplication.shared.connectedScenes
                    .compactMap { $0 as? UIWindowScene }
                    .flatMap { $0.windows }
                    .first { $0.isKeyWindow }
                    ?? UIApplication.shared.connectedScenes
                        .compactMap { $0 as? UIWindowScene }
                        .first { $0.activationState == .foregroundActive }?
                        .windows.first
                #elseif os(macOS)"""

if old_window in content:
    content = content.replace(old_window, new_window, 1)
    print("✓ Fix 1: Improved iPad window lookup in AuthManager")
else:
    print("✗ Fix 1: Could not find window lookup block")

with open(auth_path, 'w') as f:
    f.write(content)

# ── Fix 2: macOS OnboardingView — add Privacy Policy + Terms links ─────────────
onboarding_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/OnboardingView.swift"
with open(onboarding_path) as f:
    content = f.read()

# Find the existing disclosure text and add links below it
old_disclosure = """                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {
                    Text("After your \\(trialLabel) free trial, you'll be billed \\(storeKit.formattedPrice). Cancel before the trial ends to avoid being charged.")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                } else {
                    Text("Billed annually · Cancel anytime · Secure payment via Apple")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                }"""

new_disclosure = """                if isEligibleForTrial, let trialLabel = storeKit.trialPeriodLabel {
                    Text("After your \\(trialLabel) free trial, you'll be billed \\(storeKit.formattedPrice)/month. Cancel before the trial ends to avoid being charged.")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                } else {
                    Text("OneFocus Pro · Monthly Subscription · \\(storeKit.formattedPrice)/month. Renews automatically. Cancel anytime.")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                }
                HStack(spacing: 16) {
                    Link("Privacy Policy", destination: URL(string: "https://onefocus.info/privacy")!)
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
                    Link("Terms of Use", destination: URL(string: "https://onefocus.info/terms")!)
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
                }"""

if old_disclosure in content:
    content = content.replace(old_disclosure, new_disclosure, 1)
    print("✓ Fix 2: Added Privacy Policy + Terms links to macOS onboarding paywall")
else:
    print("~ Fix 2: Exact match not found, trying flexible match")
    # Try with slightly different whitespace
    match = re.search(
        r'(if isEligibleForTrial.*?trialPeriodLabel.*?\}.*?else \{.*?Billed annually.*?\})',
        content, re.DOTALL
    )
    if match:
        old2 = match.group(0)
        new2 = old2 + """
                HStack(spacing: 16) {
                    Link("Privacy Policy", destination: URL(string: "https://onefocus.info/privacy")!)
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
                    Link("Terms of Use", destination: URL(string: "https://onefocus.info/terms")!)
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
                }"""
        content = content.replace(old2, new2, 1)
        print("✓ Fix 2 (regex): Added links to macOS paywall")
    else:
        print("✗ Fix 2: Could not find disclosure block")

with open(onboarding_path, 'w') as f:
    f.write(content)

print("Done")
