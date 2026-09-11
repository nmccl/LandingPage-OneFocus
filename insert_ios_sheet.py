#!/usr/bin/env python3
"""Insert iOSChangePasswordSheet struct before the Reusable section."""

path = '/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSAccountSettingsView.swift'
with open(path) as f:
    lines = f.readlines()

if any('struct iOSChangePasswordSheet' in l for l in lines):
    print('Already present')
    exit(0)

# Find the line with "// MARK: - Reusable iOS Settings Components"
insert_at = None
for i, line in enumerate(lines):
    if '// MARK: - Reusable iOS Settings Components' in line:
        insert_at = i
        break

if insert_at is None:
    print('Could not find insertion point')
    exit(1)

sheet_lines = [
    '// MARK: - iOS Change Password Sheet\n',
    'struct iOSChangePasswordSheet: View {\n',
    '    @Binding var newPassword:        String\n',
    '    @Binding var confirmNewPassword: String\n',
    '    @Binding var isChanging:         Bool\n',
    '    @Binding var errorMessage:       String\n',
    '    let onSave:   () -> Void\n',
    '    let onCancel: () -> Void\n',
    '    var body: some View {\n',
    '        NavigationStack {\n',
    '            VStack(alignment: .leading, spacing: AppConstants.Spacing.lg) {\n',
    '                VStack(spacing: AppConstants.Spacing.sm) {\n',
    '                    iOSAuthTextField(\n',
    '                        placeholder: "New password (min. 6 characters)",\n',
    '                        text: $newPassword,\n',
    '                        icon: "lock",\n',
    '                        isSecure: true,\n',
    '                        textContentType: .newPassword\n',
    '                    )\n',
    '                    iOSAuthTextField(\n',
    '                        placeholder: "Confirm new password",\n',
    '                        text: $confirmNewPassword,\n',
    '                        icon: "lock.fill",\n',
    '                        isSecure: true,\n',
    '                        textContentType: .newPassword\n',
    '                    )\n',
    '                    if !confirmNewPassword.isEmpty && newPassword != confirmNewPassword {\n',
    '                        Text("Passwords do not match")\n',
    '                            .font(.system(size: 13))\n',
    '                            .foregroundColor(.red)\n',
    '                            .frame(maxWidth: .infinity, alignment: .leading)\n',
    '                    }\n',
    '                    if !errorMessage.isEmpty {\n',
    '                        Text(errorMessage)\n',
    '                            .font(.system(size: 13))\n',
    '                            .foregroundColor(.red)\n',
    '                            .frame(maxWidth: .infinity, alignment: .leading)\n',
    '                    }\n',
    '                }\n',
    '                Button(action: onSave) {\n',
    '                    ZStack {\n',
    '                        if isChanging { ProgressView().tint(.white) }\n',
    '                        else {\n',
    '                            Text("Save Password")\n',
    '                                .font(.system(size: AppConstants.FontSize.body, weight: .semibold))\n',
    '                                .foregroundColor(.white)\n',
    '                        }\n',
    '                    }\n',
    '                    .frame(maxWidth: .infinity)\n',
    '                    .frame(height: 50)\n',
    '                    .background(newPassword.count >= 6 && newPassword == confirmNewPassword\n',
    '                                ? AppConstants.Colors.primaryAccent\n',
    '                                : AppConstants.Colors.textTertiary.opacity(0.4))\n',
    '                    .cornerRadius(AppConstants.CornerRadius.medium)\n',
    '                }\n',
    '                .buttonStyle(.plain)\n',
    '                .disabled(newPassword.count < 6 || newPassword != confirmNewPassword || isChanging)\n',
    '                Spacer()\n',
    '            }\n',
    '            .padding(AppConstants.Spacing.lg)\n',
    '            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())\n',
    '            .navigationTitle("Change Password")\n',
    '            .navigationBarTitleDisplayMode(.inline)\n',
    '            .toolbar {\n',
    '                ToolbarItem(placement: .cancellationAction) {\n',
    '                    Button("Cancel", action: onCancel)\n',
    '                        .foregroundColor(AppConstants.Colors.primaryAccent)\n',
    '                }\n',
    '            }\n',
    '        }\n',
    '    }\n',
    '}\n',
    '\n',
]

new_lines = lines[:insert_at] + sheet_lines + lines[insert_at:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print(f'Inserted iOSChangePasswordSheet before line {insert_at+1}. New total: {len(new_lines)} lines')
