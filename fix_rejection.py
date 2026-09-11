import re

# ── Fix 1: iOSFocusView — navbar always visible in portrait ──────────────────
focus_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSFocusView.swift"
with open(focus_path) as f:
    content = f.read()

# Replace the single toolbar modifier with one that explicitly forces visible in portrait
old = "        // Hide the tab bar while in landscape focus mode\n        .toolbar(isLandscape ? .hidden : .visible, for: .tabBar)"
new = "        // Hide the tab bar in landscape focus mode; force visible in portrait\n        // (needed because .tabBarMinimizeBehavior(.onScrollDown) can leave the bar\n        //  minimized when switching to a non-scrolling tab like Focus)\n        .toolbar(isLandscape ? .hidden : .visible, for: .tabBar)\n        .toolbarVisibility(isLandscape ? .hidden : .visible, for: .tabBar)"

if old in content:
    content = content.replace(old, new, 1)
    print("✓ Fix 1: Added .toolbarVisibility to iOSFocusView")
else:
    print("~ Fix 1: toolbar modifier not found with exact text, trying alternate")
    # Try without the comment
    old2 = "        .toolbar(isLandscape ? .hidden : .visible, for: .tabBar)"
    new2 = "        // Force tab bar visible in portrait; hide in landscape focus mode\n        .toolbar(isLandscape ? .hidden : .visible, for: .tabBar)\n        .toolbarVisibility(isLandscape ? .hidden : .visible, for: .tabBar)"
    if old2 in content:
        content = content.replace(old2, new2, 1)
        print("✓ Fix 1 (alt): Added .toolbarVisibility to iOSFocusView")
    else:
        print("✗ Fix 1: Could not find toolbar modifier")

with open(focus_path, 'w') as f:
    f.write(content)

# ── Fix 2: iOSOnboardingView — add subscription disclosure ───────────────────
onboarding_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/iOSOnboardingView.swift"
with open(onboarding_path) as f:
    content = f.read()

# Add subscription disclosure text below the auto-charge disclosure block
# The disclosure needs: title, length, price, EULA link, privacy policy link
# Find the .task block and insert before it
old_task = """        .task {
            isEligibleForTrial = await storeKit.checkTrialEligibility()
        }"""

new_disclosure = """        // ── Subscription disclosure (Guideline 3.1.2c) ──────────────────────
        VStack(spacing: 6) {
            Text("OneFocus Pro · Monthly Subscription")
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textTertiary)
            Text("Billed monthly at \\(storeKit.formattedPrice). Cancel anytime before renewal. Subscription renews automatically unless cancelled at least 24 hours before the end of the current period.")
                .font(.system(size: 11))
                .foregroundColor(AppConstants.Colors.textTertiary.opacity(0.8))
                .multilineTextAlignment(.center)
            HStack(spacing: 16) {
                Link("Privacy Policy", destination: URL(string: "https://onefocus.info/privacy")!)
                    .font(.system(size: 11))
                    .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
                Link("Terms of Use", destination: URL(string: "https://onefocus.info/terms")!)
                    .font(.system(size: 11))
                    .foregroundColor(AppConstants.Colors.primaryAccent.opacity(0.8))
            }
        }
        .padding(.horizontal, 32)
        .padding(.bottom, 16)
"""

if old_task in content:
    content = content.replace(old_task, new_disclosure + "\n        " + old_task, 1)
    print("✓ Fix 2: Added subscription disclosure to iOSPaywallPage")
else:
    print("✗ Fix 2: Could not find .task block in iOSOnboardingView")

with open(onboarding_path, 'w') as f:
    f.write(content)

print("Done")
