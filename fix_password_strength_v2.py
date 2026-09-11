"""
Fix: Add password strength indicator to macOS and iOS sign-in views.
"""
import sys

mac_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/SignInView.swift"
ios_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Auth/iOSSignInView.swift"

with open(mac_path) as f:
    mac = f.read()
with open(ios_path) as f:
    ios = f.read()

# ── Shared password strength property text ────────────────────────────────────
STRENGTH_PROP = (
    "    private enum PasswordStrength { case weak, fair, strong }\n"
    "    private var passwordStrength: PasswordStrength {\n"
    "        let p = password\n"
    "        guard p.count >= 6 else { return .weak }\n"
    "        let hasUpper  = p.contains(where: { c in c.isUppercase })\n"
    "        let hasDigit  = p.contains(where: { c in c.isNumber })\n"
    "        let hasSymbol = p.contains(where: { c in !c.isLetter && !c.isNumber })\n"
    "        let score = [hasUpper, hasDigit, hasSymbol].filter { b in b }.count\n"
    "        if p.count >= 12 && score >= 2 { return .strong }\n"
    "        if p.count >= 8  && score >= 1 { return .fair }\n"
    "        return .weak\n"
    "    }\n"
    "\n"
)

# ── macOS ─────────────────────────────────────────────────────────────────────
MAC_COMPUTED_ANCHOR = (
    "    private var passwordMismatch: Bool {\n"
    "        isSignUpMode && !confirmPassword.isEmpty && password != confirmPassword\n"
    "    }\n"
    "\n"
    "    private var isFormValid: Bool {"
)
MAC_COMPUTED_REPLACEMENT = (
    "    private var passwordMismatch: Bool {\n"
    "        isSignUpMode && !confirmPassword.isEmpty && password != confirmPassword\n"
    "    }\n"
    "\n"
    + STRENGTH_PROP
    + "    private var isFormValid: Bool {"
)

MAC_FORM_ANCHOR = (
    "                    if isSignUpMode {\n"
    "                        AuthTextField(placeholder: \"Confirm password\", text: $confirmPassword, isSecure: true)"
)
MAC_FORM_REPLACEMENT = (
    "                    if isSignUpMode && !password.isEmpty {\n"
    "                        PasswordStrengthBar(strength: passwordStrength)\n"
    "                    }\n"
    "                    if isSignUpMode {\n"
    "                        AuthTextField(placeholder: \"Confirm password\", text: $confirmPassword, isSecure: true)"
)

MAC_BAR_COMPONENT = (
    "\n"
    "// MARK: - Password Strength Bar (macOS)\n"
    "private struct PasswordStrengthBar: View {\n"
    "    let strength: SignInView.PasswordStrength\n"
    "    private var label: String {\n"
    "        switch strength {\n"
    "        case .weak:   return \"Weak\"\n"
    "        case .fair:   return \"Fair\"\n"
    "        case .strong: return \"Strong\"\n"
    "        }\n"
    "    }\n"
    "    private var color: Color {\n"
    "        switch strength {\n"
    "        case .weak:   return .red\n"
    "        case .fair:   return .orange\n"
    "        case .strong: return .green\n"
    "        }\n"
    "    }\n"
    "    private var fillFraction: Double {\n"
    "        switch strength {\n"
    "        case .weak:   return 1.0 / 3.0\n"
    "        case .fair:   return 2.0 / 3.0\n"
    "        case .strong: return 1.0\n"
    "        }\n"
    "    }\n"
    "    var body: some View {\n"
    "        HStack(spacing: 8) {\n"
    "            GeometryReader { geo in\n"
    "                ZStack(alignment: .leading) {\n"
    "                    RoundedRectangle(cornerRadius: 2)\n"
    "                        .fill(Color.gray.opacity(0.2))\n"
    "                    RoundedRectangle(cornerRadius: 2)\n"
    "                        .fill(color)\n"
    "                        .frame(width: geo.size.width * fillFraction)\n"
    "                        .animation(.easeInOut(duration: 0.25), value: fillFraction)\n"
    "                }\n"
    "            }\n"
    "            .frame(height: 4)\n"
    "            Text(label)\n"
    "                .font(.system(size: 11, weight: .medium))\n"
    "                .foregroundColor(color)\n"
    "                .frame(width: 40, alignment: .trailing)\n"
    "        }\n"
    "    }\n"
    "}\n"
)

ok1 = MAC_COMPUTED_ANCHOR in mac
ok2 = MAC_FORM_ANCHOR in mac
if ok1 and ok2:
    mac = mac.replace(MAC_COMPUTED_ANCHOR, MAC_COMPUTED_REPLACEMENT)
    mac = mac.replace(MAC_FORM_ANCHOR, MAC_FORM_REPLACEMENT)
    mac = mac.replace("#endif // os(macOS)", MAC_BAR_COMPONENT + "#endif // os(macOS)")
    with open(mac_path, "w") as f:
        f.write(mac)
    print("macOS SignInView: OK")
else:
    print(f"macOS FAIL: computed={ok1} form={ok2}")
    sys.exit(1)

# ── iOS ───────────────────────────────────────────────────────────────────────
IOS_COMPUTED_ANCHOR = (
    "    private var passwordMismatch: Bool {\n"
    "        isSignUpMode && !confirmPassword.isEmpty && password != confirmPassword\n"
    "    }\n"
    "\n"
    "    private var isFormValid: Bool {"
)
IOS_COMPUTED_REPLACEMENT = (
    "    private var passwordMismatch: Bool {\n"
    "        isSignUpMode && !confirmPassword.isEmpty && password != confirmPassword\n"
    "    }\n"
    "\n"
    + STRENGTH_PROP
    + "    private var isFormValid: Bool {"
)

IOS_FORM_ANCHOR = (
    "            if isSignUpMode {\n"
    "                iOSAuthTextField(\n"
    "                    placeholder: \"Confirm password\","
)
IOS_FORM_REPLACEMENT = (
    "            if isSignUpMode && !password.isEmpty {\n"
    "                iOSPasswordStrengthBar(strength: passwordStrength)\n"
    "            }\n"
    "            if isSignUpMode {\n"
    "                iOSAuthTextField(\n"
    "                    placeholder: \"Confirm password\","
)

IOS_BAR_COMPONENT = (
    "\n"
    "// MARK: - Password Strength Bar (iOS)\n"
    "private struct iOSPasswordStrengthBar: View {\n"
    "    let strength: iOSSignInView.PasswordStrength\n"
    "    private var label: String {\n"
    "        switch strength {\n"
    "        case .weak:   return \"Weak\"\n"
    "        case .fair:   return \"Fair\"\n"
    "        case .strong: return \"Strong\"\n"
    "        }\n"
    "    }\n"
    "    private var color: Color {\n"
    "        switch strength {\n"
    "        case .weak:   return .red\n"
    "        case .fair:   return .orange\n"
    "        case .strong: return .green\n"
    "        }\n"
    "    }\n"
    "    private var fillFraction: Double {\n"
    "        switch strength {\n"
    "        case .weak:   return 1.0 / 3.0\n"
    "        case .fair:   return 2.0 / 3.0\n"
    "        case .strong: return 1.0\n"
    "        }\n"
    "    }\n"
    "    var body: some View {\n"
    "        HStack(spacing: 8) {\n"
    "            GeometryReader { geo in\n"
    "                ZStack(alignment: .leading) {\n"
    "                    RoundedRectangle(cornerRadius: 2)\n"
    "                        .fill(Color.gray.opacity(0.2))\n"
    "                    RoundedRectangle(cornerRadius: 2)\n"
    "                        .fill(color)\n"
    "                        .frame(width: geo.size.width * fillFraction)\n"
    "                        .animation(.easeInOut(duration: 0.25), value: fillFraction)\n"
    "                }\n"
    "            }\n"
    "            .frame(height: 4)\n"
    "            Text(label)\n"
    "                .font(.system(size: 12, weight: .medium))\n"
    "                .foregroundColor(color)\n"
    "                .frame(width: 44, alignment: .trailing)\n"
    "        }\n"
    "    }\n"
    "}\n"
)

ok3 = IOS_COMPUTED_ANCHOR in ios
ok4 = IOS_FORM_ANCHOR in ios
if ok3 and ok4:
    ios = ios.replace(IOS_COMPUTED_ANCHOR, IOS_COMPUTED_REPLACEMENT)
    ios = ios.replace(IOS_FORM_ANCHOR, IOS_FORM_REPLACEMENT)
    ios = ios.replace("#endif // os(iOS)", IOS_BAR_COMPONENT + "#endif // os(iOS)")
    with open(ios_path, "w") as f:
        f.write(ios)
    print("iOS iOSSignInView: OK")
else:
    print(f"iOS FAIL: computed={ok3} form={ok4}")
    sys.exit(1)
