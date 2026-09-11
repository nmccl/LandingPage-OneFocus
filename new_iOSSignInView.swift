//
//  iOSSignInView.swift
//  OneFocus
//
//  iOS Sign-In screen — single-column mobile layout.
//  Sign-up includes confirm-password validation.
//  After sign-up, an OTP overlay is shown for email verification.
//  Uses only cross-platform SwiftUI; no AppKit, NSColor, or macOS-only APIs.
//
#if os(iOS)
import SwiftUI

struct iOSSignInView: View {
    // MARK: - Environment
    @EnvironmentObject var authManager:  AuthManager
    @EnvironmentObject var userSettings: UserSettings

    // MARK: - State
    @State private var email           = ""
    @State private var password        = ""
    @State private var confirmPassword = ""
    @State private var name            = ""
    @State private var isSignUpMode    = false
    @State private var showingError    = false
    @State private var errorMessage    = ""
    @State private var isLoading       = false
    @State private var formAppeared    = false

    // OTP
    @State private var otpCode           = ""
    @State private var otpResendCooldown = 0
    @State private var otpTimer: Timer?  = nil

    // MARK: - Computed
    private var passwordMismatch: Bool {
        isSignUpMode && !confirmPassword.isEmpty && password != confirmPassword
    }

    private var isFormValid: Bool {
        if isSignUpMode {
            return !name.isEmpty
                && !email.isEmpty
                && password.count >= 6
                && password == confirmPassword
        }
        return !email.isEmpty && !password.isEmpty
    }

    // MARK: - Body
    var body: some View {
        ZStack {
            ScrollView {
                VStack(spacing: 0) {
                    brandingHeader
                        .padding(.top, 60)
                        .padding(.bottom, 40)
                    formCard
                        .padding(.horizontal, AppConstants.Spacing.md)
                        .opacity(formAppeared ? 1 : 0)
                        .offset(y: formAppeared ? 0 : 20)
                    Spacer(minLength: 40)
                }
            }
            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())

            // OTP overlay
            if authManager.needsEmailVerification {
                otpOverlay
                    .transition(.opacity.combined(with: .move(edge: .bottom)))
            }
        }
        .animation(.easeInOut(duration: 0.3), value: authManager.needsEmailVerification)
        .onAppear {
            withAnimation(.easeOut(duration: 0.45)) { formAppeared = true }
        }
        .onChange(of: authManager.authError) { error in
            if let error = error, !error.isEmpty {
                errorMessage = error
                showingError = true
                isLoading    = false
            }
        }
        .alert("Error", isPresented: $showingError) {
            Button("OK", role: .cancel) { authManager.authError = nil }
        } message: {
            Text(errorMessage)
        }
    }

    // MARK: - Branding Header
    private var brandingHeader: some View {
        VStack(spacing: AppConstants.Spacing.md) {
            ZStack {
                RoundedRectangle(cornerRadius: 22)
                    .fill(AppConstants.Colors.primaryAccent)
                    .frame(width: 80, height: 80)
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 38, weight: .medium))
                    .foregroundColor(.white)
            }
            Text("OneFocus")
                .font(.system(size: 32, weight: .bold))
                .foregroundColor(AppConstants.Colors.textPrimary)
            Text("Stay focused. Get things done.")
                .font(.system(size: AppConstants.FontSize.body))
                .foregroundColor(AppConstants.Colors.textSecondary)
                .multilineTextAlignment(.center)
        }
    }

    // MARK: - Form Card
    private var formCard: some View {
        VStack(spacing: AppConstants.Spacing.lg) {
            // Mode toggle
            HStack(spacing: 0) {
                modeButton(title: "Sign In", isActive: !isSignUpMode) { isSignUpMode = false }
                modeButton(title: "Sign Up", isActive:  isSignUpMode) { isSignUpMode = true  }
            }
            .background(AppConstants.Colors.backgroundSecondary)
            .cornerRadius(AppConstants.CornerRadius.pill)

            // Fields
            VStack(spacing: AppConstants.Spacing.sm) {
                if isSignUpMode {
                    iOSAuthTextField(
                        placeholder: "Full name",
                        text: $name,
                        icon: "person",
                        isSecure: false
                    )
                }
                iOSAuthTextField(
                    placeholder: "Email address",
                    text: $email,
                    icon: "envelope",
                    isSecure: false,
                    keyboardType: .emailAddress,
                    textContentType: .emailAddress
                )
                iOSAuthTextField(
                    placeholder: isSignUpMode ? "Create password" : "Password",
                    text: $password,
                    icon: "lock",
                    isSecure: true,
                    textContentType: isSignUpMode ? .newPassword : .password
                )
                if isSignUpMode {
                    iOSAuthTextField(
                        placeholder: "Confirm password",
                        text: $confirmPassword,
                        icon: "lock.fill",
                        isSecure: true,
                        textContentType: .newPassword
                    )
                    if passwordMismatch {
                        Text("Passwords do not match")
                            .font(.system(size: 13))
                            .foregroundColor(.red)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.horizontal, 4)
                    }
                }
            }

            // Primary action
            Button(action: submit) {
                ZStack {
                    if isLoading {
                        ProgressView().tint(.white)
                    } else {
                        Text(isSignUpMode ? "Create Account" : "Sign In")
                            .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                            .foregroundColor(.white)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(isFormValid
                             ? AppConstants.Colors.primaryAccent
                             : AppConstants.Colors.textTertiary.opacity(0.4))
                .cornerRadius(AppConstants.CornerRadius.medium)
            }
            .buttonStyle(.plain)
            .disabled(isLoading || !isFormValid)

            // Divider
            HStack {
                Rectangle().fill(AppConstants.Colors.divider).frame(height: 0.5)
                Text("or")
                    .font(.system(size: AppConstants.FontSize.caption))
                    .foregroundColor(AppConstants.Colors.textTertiary)
                    .padding(.horizontal, AppConstants.Spacing.sm)
                Rectangle().fill(AppConstants.Colors.divider).frame(height: 0.5)
            }

            // Google OAuth
            Button {
                authManager.signInWithGoogle()
            } label: {
                HStack(spacing: AppConstants.Spacing.sm) {
                    Image(systemName: "globe")
                        .font(.system(size: 18, weight: .medium))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                    Text("Continue with Google")
                        .font(.system(size: AppConstants.FontSize.body, weight: .medium))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(AppConstants.Colors.cardBackground)
                .cornerRadius(AppConstants.CornerRadius.medium)
                .overlay(
                    RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                        .stroke(AppConstants.Colors.cardBorder, lineWidth: 1)
                )
            }
            .buttonStyle(.plain)
        }
        .padding(AppConstants.Spacing.xl)
        .background(AppConstants.Colors.cardBackground)
        .cornerRadius(AppConstants.CornerRadius.large)
        .overlay(
            RoundedRectangle(cornerRadius: AppConstants.CornerRadius.large)
                .stroke(AppConstants.Colors.cardBorder, lineWidth: AppConstants.Card.borderWidth)
        )
    }

    // MARK: - OTP Overlay
    private var otpOverlay: some View {
        ZStack {
            AppConstants.Colors.backgroundPrimary
                .ignoresSafeArea()
                .opacity(0.97)

            VStack(spacing: 28) {
                Spacer()

                // Icon
                ZStack {
                    RoundedRectangle(cornerRadius: 22)
                        .fill(AppConstants.Colors.backgroundSecondary)
                        .frame(width: 80, height: 80)
                    Image(systemName: "envelope.badge")
                        .font(.system(size: 36, weight: .medium))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                }

                VStack(spacing: 8) {
                    Text("Check your email")
                        .font(.system(size: 26, weight: .bold))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                    Text("We sent a 6-digit code to")
                        .font(.system(size: AppConstants.FontSize.body))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                    Text(authManager.pendingVerificationEmail)
                        .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                }
                .multilineTextAlignment(.center)

                // Code input
                iOSAuthTextField(
                    placeholder: "6-digit code",
                    text: $otpCode,
                    icon: "number",
                    isSecure: false,
                    keyboardType: .numberPad,
                    textContentType: .oneTimeCode
                )
                .font(.system(size: 22, weight: .semibold, design: .monospaced))
                .padding(.horizontal, AppConstants.Spacing.xl)
                .onChange(of: otpCode) { val in
                    let filtered = val.filter { $0.isNumber }
                    if filtered.count > 6 { otpCode = String(filtered.prefix(6)) }
                    else if filtered != val { otpCode = filtered }
                    if otpCode.count == 6 { submitOTP() }
                }

                // Verify button
                Button(action: submitOTP) {
                    ZStack {
                        if authManager.isLoading {
                            ProgressView().tint(.white)
                        } else {
                            Text("Verify Email")
                                .font(.system(size: AppConstants.FontSize.body, weight: .semibold))
                                .foregroundColor(.white)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 50)
                    .background(otpCode.count == 6
                                 ? AppConstants.Colors.primaryAccent
                                 : AppConstants.Colors.textTertiary.opacity(0.4))
                    .cornerRadius(AppConstants.CornerRadius.medium)
                }
                .buttonStyle(.plain)
                .disabled(otpCode.count < 6 || authManager.isLoading)
                .padding(.horizontal, AppConstants.Spacing.xl)

                // Resend
                Button(action: resendOTP) {
                    if otpResendCooldown > 0 {
                        Text("Resend code in \(otpResendCooldown)s")
                            .font(.system(size: 14))
                            .foregroundColor(AppConstants.Colors.textTertiary)
                    } else {
                        Text("Resend code")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(AppConstants.Colors.textPrimary)
                    }
                }
                .buttonStyle(.plain)
                .disabled(otpResendCooldown > 0)

                // Back
                Button("Use a different email") {
                    authManager.needsEmailVerification = false
                    authManager.pendingVerificationEmail = ""
                    otpCode = ""
                    stopCooldown()
                }
                .buttonStyle(.plain)
                .font(.system(size: 13))
                .foregroundColor(AppConstants.Colors.textTertiary)

                Spacer()
            }
            .padding(.horizontal, AppConstants.Spacing.xl)
        }
    }

    // MARK: - Mode Button
    private func modeButton(title: String, isActive: Bool, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: AppConstants.FontSize.subheadline, weight: isActive ? .semibold : .regular))
                .foregroundColor(isActive ? AppConstants.Colors.textPrimary : AppConstants.Colors.textSecondary)
                .frame(maxWidth: .infinity)
                .padding(.vertical, AppConstants.Spacing.sm)
                .background(
                    isActive
                        ? AppConstants.Colors.backgroundPrimary
                        : Color.clear
                )
                .cornerRadius(AppConstants.CornerRadius.pill)
                .padding(3)
        }
        .buttonStyle(.plain)
        .animation(.easeInOut(duration: AppConstants.Animation.fast), value: isActive)
    }

    // MARK: - Actions
    private func submit() {
        guard isFormValid else { return }
        isLoading = true
        if isSignUpMode {
            authManager.signUp(email: email, password: password, name: name)
        } else {
            authManager.signIn(email: email, password: password)
        }
        isLoading = false
    }

    private func submitOTP() {
        guard otpCode.count == 6 else { return }
        authManager.verifyOTP(email: authManager.pendingVerificationEmail, token: otpCode, name: name)
        otpCode = ""
        stopCooldown()
    }

    private func resendOTP() {
        authManager.resendOTP(email: authManager.pendingVerificationEmail)
        startCooldown()
    }

    private func startCooldown() {
        otpResendCooldown = 60
        otpTimer?.invalidate()
        otpTimer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            DispatchQueue.main.async {
                if self.otpResendCooldown > 0 {
                    self.otpResendCooldown -= 1
                } else {
                    self.stopCooldown()
                }
            }
        }
    }

    private func stopCooldown() {
        otpTimer?.invalidate()
        otpTimer = nil
        otpResendCooldown = 0
    }
}

// MARK: - Auth Text Field (iOS)
struct iOSAuthTextField: View {
    let placeholder: String
    @Binding var text: String
    let icon: String
    let isSecure: Bool
    var keyboardType: UIKeyboardType = .default
    var textContentType: UITextContentType? = nil

    var body: some View {
        HStack(spacing: AppConstants.Spacing.sm) {
            Image(systemName: icon)
                .font(.system(size: 16))
                .foregroundColor(AppConstants.Colors.textTertiary)
                .frame(width: 20)
            if isSecure {
                SecureField(placeholder, text: $text)
                    .font(.system(size: AppConstants.FontSize.body))
                    .foregroundColor(AppConstants.Colors.textPrimary)
                    .textContentType(textContentType)
                    .autocorrectionDisabled()
            } else {
                TextField(placeholder, text: $text)
                    .font(.system(size: AppConstants.FontSize.body))
                    .foregroundColor(AppConstants.Colors.textPrimary)
                    .keyboardType(keyboardType)
                    .textContentType(textContentType)
                    .autocorrectionDisabled()
                    .textInputAutocapitalization(.never)
            }
        }
        .padding(AppConstants.Spacing.md)
        .background(AppConstants.Colors.backgroundSecondary)
        .cornerRadius(AppConstants.CornerRadius.medium)
    }
}
#endif // os(iOS)
