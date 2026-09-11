path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Components/UpgradePromptView.swift"
with open(path) as f:
    content = f.read()

# Fix 1: Optimistic Pro status update — set isProUser = true immediately after
# purchase succeeds, then call evaluateProStatus in background to confirm.
# proAccess.grantPro() already exists (line 184: isProUser = true)
old_purchase = """                    _Concurrency.Task {
                        do {
                            try await storeKit.purchase()
                            await proAccess.evaluateProStatus()
                            closeSheet()
                        } catch {
                            purchaseErrorMessage = error.localizedDescription
                        }
                        isPurchasing = false
                    }"""

new_purchase = """                    _Concurrency.Task {
                        do {
                            try await storeKit.purchase()
                            // Optimistically grant Pro immediately so the UI
                            // updates right away, even in sandbox where
                            // evaluateProStatus() may lag by minutes.
                            proAccess.grantPro()
                            // Then confirm in the background via Supabase.
                            _Concurrency.Task.detached {
                                await proAccess.evaluateProStatus()
                            }
                            closeSheet()
                        } catch {
                            purchaseErrorMessage = error.localizedDescription
                        }
                        isPurchasing = false
                    }"""

if old_purchase in content:
    content = content.replace(old_purchase, new_purchase, 1)
    print("✓ Fix 1: Optimistic Pro status update applied")
else:
    print("✗ Fix 1: Could not find purchase Task block")

# Fix 2: Add Privacy Policy and Terms of Use links below the billing text.
# Insert after the closing brace of the if/else block for billing text,
# before the closing of the VStack.
old_footer = """                } else {
                    Text("Billed annually · Cancel anytime · Secure payment via Apple")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                }
            }
            .padding(.horizontal, 32)
            .padding(.top, 16)
            .padding(.bottom, 24)"""

new_footer = """                } else {
                    Text("Billed annually · Cancel anytime · Secure payment via Apple")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .multilineTextAlignment(.center)
                }
                // Privacy Policy & Terms links — required by App Store guidelines
                HStack(spacing: 4) {
                    Link("Privacy Policy", destination: URL(string: "https://onefocus.info/privacy")!)
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                    Text("·")
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                    Link("Terms of Use", destination: URL(string: "https://onefocus.info/terms")!)
                        .font(.system(size: 11))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                }
            }
            .padding(.horizontal, 32)
            .padding(.top, 16)
            .padding(.bottom, 24)"""

if old_footer in content:
    content = content.replace(old_footer, new_footer, 1)
    print("✓ Fix 2: Privacy Policy and Terms of Use links added")
else:
    print("✗ Fix 2: Could not find footer block")

with open(path, 'w') as f:
    f.write(content)
print("Done")
