#!/usr/bin/env python3
"""Insert ChangePasswordSheet struct at line 575 of AccountSettingsView.swift"""

path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift'
with open(path) as f:
    lines = f.readlines()

# Check if already present
if any('private struct ChangePasswordSheet' in l for l in lines):
    print('Already present')
    exit(0)

sheet_struct_lines = [
    '\n',
    '// MARK: - Change Password Sheet\n',
    'private struct ChangePasswordSheet: View {\n',
    '    @Binding var newPassword:        String\n',
    '    @Binding var confirmNewPassword: String\n',
    '    @Binding var isChanging:         Bool\n',
    '    @Binding var errorMessage:       String\n',
    '    let onSave:   () -> Void\n',
    '    let onCancel: () -> Void\n',
    '    var body: some View {\n',
    '        VStack(alignment: .leading, spacing: AppConstants.Spacing.lg) {\n',
    '            Text("Change Password")\n',
    '                .font(.system(size: 20, weight: .semibold))\n',
    '                .foregroundColor(AppConstants.Colors.textPrimary)\n',
    '            VStack(spacing: AppConstants.Spacing.sm) {\n',
    '                SecureField("New password (min. 6 characters)", text: $newPassword)\n',
    '                    .textFieldStyle(.plain)\n',
    '                    .padding(AppConstants.Spacing.md)\n',
    '                    .background(AppConstants.Colors.backgroundSecondary)\n',
    '                    .cornerRadius(AppConstants.CornerRadius.medium)\n',
    '                    .overlay(RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)\n',
    '                        .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5))\n',
    '                SecureField("Confirm new password", text: $confirmNewPassword)\n',
    '                    .textFieldStyle(.plain)\n',
    '                    .padding(AppConstants.Spacing.md)\n',
    '                    .background(AppConstants.Colors.backgroundSecondary)\n',
    '                    .cornerRadius(AppConstants.CornerRadius.medium)\n',
    '                    .overlay(RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)\n',
    '                        .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5))\n',
    '                if !confirmNewPassword.isEmpty && newPassword != confirmNewPassword {\n',
    '                    Text("Passwords do not match")\n',
    '                        .font(.system(size: 12))\n',
    '                        .foregroundColor(.red)\n',
    '                }\n',
    '                if !errorMessage.isEmpty {\n',
    '                    Text(errorMessage)\n',
    '                        .font(.system(size: 12))\n',
    '                        .foregroundColor(.red)\n',
    '                }\n',
    '            }\n',
    '            HStack(spacing: AppConstants.Spacing.md) {\n',
    '                Button("Cancel", action: onCancel)\n',
    '                    .buttonStyle(.plain)\n',
    '                    .foregroundColor(AppConstants.Colors.textSecondary)\n',
    '                Spacer()\n',
    '                Button(action: onSave) {\n',
    '                    HStack(spacing: 8) {\n',
    '                        if isChanging { ProgressView().controlSize(.small) }\n',
    '                        Text(isChanging ? "Saving\u2026" : "Save Password")\n',
    '                    }\n',
    '                    .foregroundColor(.white)\n',
    '                    .padding(.horizontal, 16)\n',
    '                    .padding(.vertical, 10)\n',
    '                    .background(newPassword.count >= 6 && newPassword == confirmNewPassword\n',
    '                                ? AppConstants.Colors.primaryAccent\n',
    '                                : AppConstants.Colors.textTertiary.opacity(0.4))\n',
    '                    .cornerRadius(AppConstants.CornerRadius.medium)\n',
    '                }\n',
    '                .buttonStyle(.plain)\n',
    '                .disabled(newPassword.count < 6 || newPassword != confirmNewPassword || isChanging)\n',
    '            }\n',
    '        }\n',
    '        .padding(AppConstants.Spacing.xl)\n',
    '        .frame(width: 360)\n',
    '    }\n',
    '}\n',
    '\n',
]

# Insert before line 576 (index 575)
insert_at = 575  # 0-indexed, before the "// MARK: - Preview" line
new_lines = lines[:insert_at] + sheet_struct_lines + lines[insert_at:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print(f'Inserted ChangePasswordSheet at line {insert_at+1}. New total: {len(new_lines)} lines')
