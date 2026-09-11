#!/usr/bin/env python3
"""Patch iOSAccountSettingsView.swift to wire Change Password functionality."""

path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSAccountSettingsView.swift'
with open(path) as f:
    content = f.read()

changed = False

# 1. Add new @State variables for change-password sheet
old_state = '    @State private var isRestoring = false'
new_state = '''    @State private var isRestoring = false
    // Change-password sheet
    @State private var showingChangePassword = false
    @State private var newPassword           = ""
    @State private var confirmNewPassword    = ""
    @State private var isChangingPassword    = false
    @State private var changePasswordError   = ""'''

if old_state in content and 'showingChangePassword' not in content:
    content = content.replace(old_state, new_state, 1)
    print('State vars added')
    changed = True
else:
    print('State vars already present or old_state not found')

# 2. Replace the "Sign out and use Forgot Password" text with a real button
old_security = '''                Text("Sign out and use \\"Forgot Password\\" on the sign-in screen to reset your password.")
                    .font(.system(size: AppConstants.FontSize.caption))
                    .foregroundColor(AppConstants.Colors.textSecondary)'''

new_security = '''                Button {
                    showingChangePassword = true
                } label: {
                    HStack {
                        Text("Change Password")
                            .font(.system(size: AppConstants.FontSize.body, weight: .medium))
                            .foregroundColor(AppConstants.Colors.primaryAccent)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textTertiary)
                    }
                }
                .buttonStyle(.plain)
                .sheet(isPresented: $showingChangePassword) {
                    iOSChangePasswordSheet(
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

if old_security in content:
    content = content.replace(old_security, new_security, 1)
    print('Security card updated with Change Password button')
    changed = True
else:
    print('Old security text not found - trying alternate match')
    # Try without escaped quotes
    alt = 'Text("Sign out and use \\"Forgot Password\\" on the sign-in screen'
    if alt in content:
        idx = content.find(alt)
        print(f'Found at idx {idx}:', repr(content[idx:idx+200]))
    else:
        idx = content.find('Forgot Password')
        if idx >= 0:
            print('Found "Forgot Password" at:', repr(content[max(0,idx-100):idx+200]))

# 3. Add iOSChangePasswordSheet struct before the Reusable iOS Settings Components section
old_reusable = '// MARK: - Reusable iOS Settings Components\nstruct iOSSettingsCard'
sheet_struct = '''// MARK: - iOS Change Password Sheet
struct iOSChangePasswordSheet: View {
    @Binding var newPassword:        String
    @Binding var confirmNewPassword: String
    @Binding var isChanging:         Bool
    @Binding var errorMessage:       String
    let onSave:   () -> Void
    let onCancel: () -> Void
    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: AppConstants.Spacing.lg) {
                VStack(spacing: AppConstants.Spacing.sm) {
                    iOSAuthTextField(
                        placeholder: "New password (min. 6 characters)",
                        text: $newPassword,
                        icon: "lock",
                        isSecure: true,
                        textContentType: .newPassword
                    )
                    iOSAuthTextField(
                        placeholder: "Confirm new password",
                        text: $confirmNewPassword,
                        icon: "lock.fill",
                        isSecure: true,
                        textContentType: .newPassword
                    )
                    if !confirmNewPassword.isEmpty && newPassword != confirmNewPassword {
                        Text("Passwords do not match")
                            .font(.system(size: 13))
                            .foregroundColor(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    if !errorMessage.isEmpty {
                        Text(errorMessage)
                            .font(.system(size: 13))
                            .foregroundColor(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
                Button(action: onSave) {
                    ZStack {
                        if isChanging { ProgressView().tint(.white) }
                        else {
                            Text("Save Password")
                                .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                                .foregroundColor(.white)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(newPassword.count >= 6 && newPassword == confirmNewPassword
                                ? AppConstants.Colors.primaryAccent
                                : AppConstants.Colors.textTertiary.opacity(0.4))
                    .cornerRadius(AppConstants.CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(newPassword.count < 6 || newPassword != confirmNewPassword || isChanging)
                Spacer()
            }
            .padding(AppConstants.Spacing.lg)
            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())
            .navigationTitle("Change Password")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel", action: onCancel)
                        .foregroundColor(AppConstants.Colors.primaryAccent)
                }
            }
        }
    }
}

// MARK: - Reusable iOS Settings Components
struct iOSSettingsCard'''

if old_reusable in content and 'iOSChangePasswordSheet' not in content:
    content = content.replace(old_reusable, sheet_struct, 1)
    print('iOSChangePasswordSheet struct added')
    changed = True
else:
    print('iOSChangePasswordSheet already present or marker not found')

with open(path, 'w') as f:
    f.write(content)
print(f'Saved. Lines: {content.count(chr(10))}. Changed: {changed}')
