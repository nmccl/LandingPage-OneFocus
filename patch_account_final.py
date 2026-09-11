#!/usr/bin/env python3
"""Patch AccountSettingsView.swift to wire Change Password functionality."""

path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift'
with open(path) as f:
    content = f.read()

changed = False

# 1. Remove .disabled(true) / .opacity(0.55) from Change Password button
old_disabled = '                .buttonStyle(.plain)\n                .disabled(true)\n                .opacity(0.55)'
new_enabled   = '                .buttonStyle(.plain)'
if old_disabled in content:
    content = content.replace(old_disabled, new_enabled, 1)
    print('Removed disabled/opacity modifiers')
    changed = True

# 2. Add .sheet modifier after the Change Password button's .buttonStyle(.plain)
# Find the button by its action and insert sheet after the first .buttonStyle(.plain) following it
marker = '                Button(action: { showingChangePassword = true }) {'
sheet_mod = '''
                .sheet(isPresented: $showingChangePassword) {
                    ChangePasswordSheet(
                        newPassword: $newPassword,
                        confirmNewPassword: $confirmNewPassword,
                        isChanging: $isChangingPassword,
                        errorMessage: $changePasswordError,
                        onSave: {
                            guard newPassword.count >= 6, newPassword == confirmNewPassword else {
                                changePasswordError = newPassword != confirmNewPassword
                                    ? "Passwords do not match."
                                    : "Password must be at least 6 characters."
                                return
                            }
                            isChangingPassword = true
                            changePasswordError = ""
                            authManager.updatePassword(newPassword: newPassword)
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                                isChangingPassword = false
                                if authManager.authError == nil {
                                    newPassword = ""
                                    confirmNewPassword = ""
                                    showingChangePassword = false
                                } else {
                                    changePasswordError = authManager.authError ?? "Unknown error."
                                    authManager.authError = nil
                                }
                            }
                        },
                        onCancel: {
                            newPassword = ""
                            confirmNewPassword = ""
                            changePasswordError = ""
                            showingChangePassword = false
                        }
                    )
                }'''

if marker in content and '.sheet(isPresented: $showingChangePassword)' not in content:
    idx = content.find(marker)
    bs_idx = content.find('                .buttonStyle(.plain)', idx)
    end_idx = bs_idx + len('                .buttonStyle(.plain)')
    content = content[:end_idx] + sheet_mod + content[end_idx:]
    print('Sheet modifier added')
    changed = True
else:
    print('Sheet already present or marker not found')

# 3. Add ChangePasswordSheet struct before the Preview section
sheet_struct = '''// MARK: - Change Password Sheet
private struct ChangePasswordSheet: View {
    @Binding var newPassword:        String
    @Binding var confirmNewPassword: String
    @Binding var isChanging:         Bool
    @Binding var errorMessage:       String
    let onSave:   () -> Void
    let onCancel: () -> Void
    var body: some View {
        VStack(alignment: .leading, spacing: AppConstants.Spacing.lg) {
            Text("Change Password")
                .font(.system(size: 20, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textPrimary)
            VStack(spacing: AppConstants.Spacing.sm) {
                SecureField("New password (min. 6 characters)", text: $newPassword)
                    .textFieldStyle(.plain)
                    .padding(AppConstants.Spacing.md)
                    .background(AppConstants.Colors.backgroundSecondary)
                    .cornerRadius(AppConstants.CornerRadius.medium)
                    .overlay(RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                        .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5))
                SecureField("Confirm new password", text: $confirmNewPassword)
                    .textFieldStyle(.plain)
                    .padding(AppConstants.Spacing.md)
                    .background(AppConstants.Colors.backgroundSecondary)
                    .cornerRadius(AppConstants.CornerRadius.medium)
                    .overlay(RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                        .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5))
                if !confirmNewPassword.isEmpty && newPassword != confirmNewPassword {
                    Text("Passwords do not match")
                        .font(.system(size: 12))
                        .foregroundColor(.red)
                }
                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .font(.system(size: 12))
                        .foregroundColor(.red)
                }
            }
            HStack(spacing: AppConstants.Spacing.md) {
                Button("Cancel", action: onCancel)
                    .buttonStyle(.plain)
                    .foregroundColor(AppConstants.Colors.textSecondary)
                Spacer()
                Button(action: onSave) {
                    HStack(spacing: 8) {
                        if isChanging { ProgressView().controlSize(.small) }
                        Text(isChanging ? "Saving\u2026" : "Save Password")
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 10)
                    .background(newPassword.count >= 6 && newPassword == confirmNewPassword
                                ? AppConstants.Colors.primaryAccent
                                : AppConstants.Colors.textTertiary.opacity(0.4))
                    .cornerRadius(AppConstants.CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(newPassword.count < 6 || newPassword != confirmNewPassword || isChanging)
            }
        }
        .padding(AppConstants.Spacing.xl)
        .frame(width: 360)
    }
}

'''

old_preview = '// MARK: - Preview\nstruct AccountSettingsView_Previews'
if old_preview in content and 'ChangePasswordSheet' not in content:
    content = content.replace(old_preview, sheet_struct + old_preview, 1)
    print('ChangePasswordSheet struct added')
    changed = True
else:
    print('ChangePasswordSheet already present or preview marker not found')

with open(path, 'w') as f:
    f.write(content)
print(f'Saved. Lines: {content.count(chr(10))}. Changed: {changed}')
