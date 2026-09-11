//
//  SignInView.swift
//  OneFocus
//
//  Split-panel sign-in/sign-up screen for macOS.
//  Sign-up includes confirm-password validation.
//  After sign-up, an OTP overlay is shown for email verification.
//
#if os(macOS)
import SwiftUI

struct SignInView: View {
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

    // OTP
    @State private var otpCode         = ""
    @State private var otpResendCooldown = 0
    @State private var otpTimer: Timer? = nil

    // Animation
    @State private var formAppeared  = false
    @State private var panelAppeared = false

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
            Color(nsColor: .windowBackgroundColor).ignoresSafeArea()

            HStack(spacing: 0) {
                leftPanel
                    .frame(maxWidth: .infinity)
                    .opacity(panelAppeared ? 1 : 0)
                    .offset(x: panelAppeared ? 0 : -20)

                Rectangle()
                    .fill(Color(nsColor: .separatorColor))
                    .frame(width: 0.5)

                rightPanel
                    .frame(maxWidth: .infinity)
                    .opacity(formAppeared ? 1 : 0)
                    .offset(x: formAppeared ? 0 : 20)
            }

            // OTP overlay
            if authManager.needsEmailVerification {
                otpOverlay
                    .transition(.opacity.combined(with: .scale(scale: 0.97)))
            }
        }
        .frame(minWidth: 700, minHeight: 480)
        .animation(.easeInOut(duration: 0.25), value: authManager.needsEmailVerification)
        .onAppear {
            withAnimation(.easeOut(duration: 0.45)) { panelAppeared = true }
            withAnimation(.easeOut(duration: 0.45).delay(0.1)) { formAppeared = true }
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

    // MARK: - Left Panel
    private var leftPanel: some View {
        VStack(alignment: .leading, spacing: 0) {
            Spacer()
            ZStack {
                RoundedRectangle(cornerRadius: 16)
                    .fill(AppConstants.Colors.backgroundTertiary)
                    .frame(width: 56, height: 56)
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 28, weight: .medium))
                    .foregroundColor(AppConstants.Colors.textPrimary)
            }
            .padding(.bottom, 28)
            Text("OneFocus")
                .font(.system(size: 36, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textPrimary)
            Text("Focus on what matters")
                .font(.system(size: 16))
                .foregroundColor(AppConstants.Colors.textSecondary)
                .padding(.top, 6)
                .padding(.bottom, 40)
            VStack(alignment: .leading, spacing: 20) {
                SignInFeatureRow(icon: "timer",            title: "Pomodoro Focus Sessions",  subtitle: "Deep work in structured intervals")
                SignInFeatureRow(icon: "checklist",        title: "Task Management",           subtitle: "Prioritise and track your work")
                SignInFeatureRow(icon: "chart.bar",        title: "Productivity Analytics",    subtitle: "Understand your focus patterns")
                SignInFeatureRow(icon: "doc.on.clipboard", title: "Clipboard History",         subtitle: "Never lose copied content again")
            }
            Spacer()
            Text("Your data syncs across all your devices.")
                .font(.system(size: 12))
                .foregroundColor(AppConstants.Colors.textTertiary)
                .padding(.bottom, 8)
        }
        .padding(.horizontal, 44)
        .padding(.vertical, 40)
        .background(AppConstants.Colors.backgroundSecondary)
    }

    // MARK: - Right Panel
    private var rightPanel: some View {
        VStack(spacing: 0) {
            Spacer()
            VStack(alignment: .leading, spacing: 20) {
                // Title
                VStack(alignment: .leading, spacing: 4) {
                    Text(isSignUpMode ? "Create account" : "Welcome back")
                        .font(.system(size: 24, weight: .semibold))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                    Text(isSignUpMode ? "Sign up to get started" : "Sign in to continue")
                        .font(.system(size: 14))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }

                // OAuth buttons
                VStack(spacing: 10) {
                    OAuthButton(
                        icon: "apple.logo",
                        label: isSignUpMode ? "Sign up with Apple" : "Sign in with Apple",
                        action: { authManager.signInWithApple() }
                    )
                    OAuthButton(
                        icon: "globe",
                        label: isSignUpMode ? "Sign up with Google" : "Sign in with Google",
                        action: { authManager.signInWithGoogle() }
                    )
                }

                // Divider
                HStack(spacing: 12) {
                    Rectangle().fill(Color(nsColor: .separatorColor)).frame(height: 0.5)
                    Text("or continue with email")
                        .font(.system(size: 12))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .fixedSize()
                    Rectangle().fill(Color(nsColor: .separatorColor)).frame(height: 0.5)
                }

                // Email / password form
                VStack(spacing: 10) {
                    if isSignUpMode {
                        AuthTextField(placeholder: "Full name", text: $name, isSecure: false)
                    }
                    AuthTextField(placeholder: "Email address", text: $email, isSecure: false)
                    AuthTextField(
                        placeholder: isSignUpMode ? "Create password" : "Password",
                        text: $password,
                        isSecure: true
                    )
                    if isSignUpMode {
                        AuthTextField(placeholder: "Confirm password", text: $confirmPassword, isSecure: true)
                        if passwordMismatch {
                            Text("Passwords do not match")
                                .font(.system(size: 12))
                                .foregroundColor(.red)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                    }
                }

                // Primary action
                Button(action: handleAuth) {
                    ZStack {
                        RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                            .fill(isFormValid
                                  ? AppConstants.Colors.primaryAccent
                                  : AppConstants.Colors.textTertiary.opacity(0.4))
                            .frame(height: 44)
                        if isLoading {
                            ProgressView()
                                .progressViewStyle(.circular)
                                .scaleEffect(0.8)
                                .tint(.white)
                        } else {
                            Text(isSignUpMode ? "Create Account" : "Sign In")
                                .font(.system(size: 15, weight: .medium))
                                .foregroundColor(.white)
                        }
                    }
                }
                .buttonStyle(.plain)
                .disabled(!isFormValid || isLoading)

                // Toggle mode
                HStack(spacing: 4) {
                    Text(isSignUpMode ? "Already have an account?" : "Don't have an account?")
                        .font(.system(size: 13))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                    Button(isSignUpMode ? "Sign In" : "Sign Up") {
                        withAnimation(.easeInOut(duration: 0.2)) {
                            isSignUpMode.toggle()
                            email = ""; password = ""; confirmPassword = ""; name = ""
                        }
                    }
                    .buttonStyle(.plain)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(AppConstants.Colors.textPrimary)
                }
            }
            .frame(maxWidth: 340)
            Spacer()
        }
        .padding(.horizontal, 44)
        .padding(.vertical, 40)
    }

    // MARK: - OTP Overlay
    private var otpOverlay: some View {
        ZStack {
            Color(nsColor: .windowBackgroundColor)
                .opacity(0.92)
                .ignoresSafeArea()
                .background(.ultraThinMaterial)

            VStack(spacing: 24) {
                // Icon
                ZStack {
                    RoundedRectangle(cornerRadius: 16)
                        .fill(AppConstants.Colors.backgroundTertiary)
                        .frame(width: 56, height: 56)
                    Image(systemName: "envelope.badge")
                        .font(.system(size: 26, weight: .medium))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                }

                VStack(spacing: 6) {
                    Text("Check your email")
                        .font(.system(size: 22, weight: .semibold))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                    Text("We sent a 6-digit code to\n\(authManager.pendingVerificationEmail)")
                        .font(.system(size: 14))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                        .multilineTextAlignment(.center)
                }

                // Code input
                TextField("Enter 6-digit code", text: $otpCode)
                    .textFieldStyle(.plain)
                    .font(.system(size: 22, weight: .semibold, design: .monospaced))
                    .multilineTextAlignment(.center)
                    .foregroundColor(AppConstants.Colors.textPrimary)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 12)
                    .background(AppConstants.Colors.backgroundSecondary)
                    .cornerRadius(AppConstants.CornerRadius.medium)
                    .overlay(
                        RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                            .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5)
                    )
                    .frame(maxWidth: 220)
                    .onChange(of: otpCode) { val in
                        // Limit to 6 digits
                        let filtered = val.filter { $0.isNumber }
                        if filtered.count > 6 { otpCode = String(filtered.prefix(6)) }
                        else if filtered != val { otpCode = filtered }
                        // Auto-submit when 6 digits entered
                        if otpCode.count == 6 { submitOTP() }
                    }

                // Verify button
                Button(action: submitOTP) {
                    ZStack {
                        RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                            .fill(otpCode.count == 6
                                  ? AppConstants.Colors.primaryAccent
                                  : AppConstants.Colors.textTertiary.opacity(0.4))
                            .frame(height: 44)
                        if authManager.isLoading {
                            ProgressView().progressViewStyle(.circular).scaleEffect(0.8).tint(.white)
                        } else {
                            Text("Verify Email")
                                .font(.system(size: 15, weight: .medium))
                                .foregroundColor(.white)
                        }
                    }
                }
                .buttonStyle(.plain)
                .disabled(otpCode.count < 6 || authManager.isLoading)
                .frame(maxWidth: 220)

                // Resend
                Button(action: resendOTP) {
                    if otpResendCooldown > 0 {
                        Text("Resend code in \(otpResendCooldown)s")
                            .font(.system(size: 13))
                            .foregroundColor(AppConstants.Colors.textTertiary)
                    } else {
                        Text("Resend code")
                            .font(.system(size: 13, weight: .medium))
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
                .font(.system(size: 12))
                .foregroundColor(AppConstants.Colors.textTertiary)
            }
            .padding(40)
            .frame(maxWidth: 380)
        }
    }

    // MARK: - Actions
    private func handleAuth() {
        guard isFormValid else { return }
        isLoading = true
        if isSignUpMode {
            authManager.signUp(email: email, password: password, name: name)
            userSettings.userName = name
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
            if otpResendCooldown > 0 {
                otpResendCooldown -= 1
            } else {
                stopCooldown()
            }
        }
    }

    private func stopCooldown() {
        otpTimer?.invalidate()
        otpTimer = nil
        otpResendCooldown = 0
    }
}

// MARK: - Feature Row
struct SignInFeatureRow: View {
    let icon: String
    let title: String
    let subtitle: String
    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                RoundedRectangle(cornerRadius: 8)
                    .fill(AppConstants.Colors.backgroundTertiary)
                    .frame(width: 36, height: 36)
                Image(systemName: icon)
                    .font(.system(size: 16, weight: .regular))
                    .foregroundColor(AppConstants.Colors.textPrimary)
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(AppConstants.Colors.textPrimary)
                Text(subtitle)
                    .font(.system(size: 12))
                    .foregroundColor(AppConstants.Colors.textSecondary)
            }
        }
    }
}

// MARK: - OAuth Button
struct OAuthButton: View {
    let icon: String
    let label: String
    let action: () -> Void
    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                Image(systemName: icon)
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(AppConstants.Colors.textPrimary)
                Text(label)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(AppConstants.Colors.textPrimary)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 44)
            .background(AppConstants.Colors.backgroundSecondary)
            .cornerRadius(AppConstants.CornerRadius.medium)
            .overlay(
                RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                    .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5)
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Auth Text Field
struct AuthTextField: View {
    let placeholder: String
    @Binding var text: String
    let isSecure: Bool
    var body: some View {
        Group {
            if isSecure {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
            }
        }
        .textFieldStyle(.plain)
        .font(.system(size: 14))
        .foregroundColor(AppConstants.Colors.textPrimary)
        .padding(.horizontal, 14)
        .padding(.vertical, 11)
        .background(AppConstants.Colors.backgroundSecondary)
        .cornerRadius(AppConstants.CornerRadius.medium)
        .overlay(
            RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
                .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5)
        )
    }
}

// MARK: - Preview
struct SignInView_Previews: PreviewProvider {
    static var previews: some View {
        SignInView()
            .environmentObject(AuthManager())
            .environmentObject(UserSettings.sample)
            .frame(width: 760, height: 520)
    }
}
#endif // os(macOS)
