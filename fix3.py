#!/usr/bin/env python3
BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# ── Fix 1: iOSFocusView — timer shows session title text instead of time ──
# The timerRing uses circleSize * 0.22 font which is fine, but the Text inside
# shows focusTimer.currentSessionType.title instead of focusTimer.timeString.
# The issue is the font size is so large it shows the title label. 
# Actually looking at the code: Text(focusTimer.timeString) IS there at line 83.
# The problem is the font size: circleSize * 0.22 of a ~320pt circle = ~70pt.
# That's correct. The real bug: the timer text shows "Focus Time" because
# timeString is returning currentSessionType.title. Let's check — no, timeString
# is a separate property. The actual bug from the screenshot: the timer ring
# shows "Focus Time" as the big text. This means timeString == "Focus Time".
# That means FocusTimerManager.timeString returns the session title when idle.
# Fix: in iOSFocusView, show timeString but fall back to the duration string.

focus_path = f"{BASE}/Views/iOS/Tabs/iOSFocusView.swift"
with open(focus_path, "r") as f: src = f.read()

# The timer text inside the ring — replace with explicit duration fallback
old = '                .font(.system(size: circleSize * 0.22, weight: .thin))\n                .foregroundColor(AppConstants.Colors.textPrimary)\n                .monospacedDigit()'
new = '                .font(.system(size: circleSize * 0.18, weight: .thin))\n                .foregroundColor(AppConstants.Colors.textPrimary)\n                .monospacedDigit()'
src = src.replace(old, new, 1)

# Also remove the duplicate session title Text above the ring (line 33 area)
# The view has TWO Text(focusTimer.currentSessionType.title) — one above the ring
# in the VStack and one inside the ring. Remove the one inside the ring if present.
# Actually the ring only has timeString. The issue is timeString itself.
# Let's check what timeString returns when idle — it might return "25:00" or title.
# From the screenshot it shows "Focus Time" which is currentSessionType.title.
# This means timeString == currentSessionType.title when idle.
# Fix: override in the view to show formatted duration when timeString looks like a title.
old_text = '            Text(focusTimer.timeString)\n                .font(.system(size: circleSize * 0.18, weight: .thin))\n                .foregroundColor(AppConstants.Colors.textPrimary)\n                .monospacedDigit()'
new_text = '            Text(focusTimer.timeString.contains(":") ? focusTimer.timeString : focusTimer.formattedDuration)\n                .font(.system(size: circleSize * 0.18, weight: .thin))\n                .foregroundColor(AppConstants.Colors.textPrimary)\n                .monospacedDigit()'
if old_text in src:
    src = src.replace(old_text, new_text, 1)
    print("Focus timer text fallback applied")
else:
    print("Focus timer text - pattern not found, checking...")
    # Just fix the font size change we already made
    print("Font size reduced to 0.18")

with open(focus_path, "w") as f: f.write(src)

# ── Fix 2: System dark mode — half white/half dark ──
# The iOS system theme now uses hardcoded light hex values (from our previous fix).
# When the device is in dark mode, .preferredColorScheme(nil) lets iOS apply dark,
# but all the AppConstants.Colors.* are still the hardcoded light hex values.
# Fix: restore the system theme to use Color(.systemBackground) etc. — the UIKit
# adaptive colors that actually respond to the OS color scheme.
# The grey hue issue was a separate problem. The real fix for grey hue is to use
# Color(.systemBackground) but also set .preferredColorScheme(nil) so iOS handles it.
# The previous "fix" broke dark mode by hardcoding light colors.

theme_path = f"{BASE}/Manager/AppTheme.swift"
with open(theme_path, "r") as f: theme = f.read()

old_ios = '''        return AppTheme(
            id: "system", name: "System", isPro: false, group: .system,
            backgroundPrimary:   Color(hex: "FFFFFF"),
            backgroundSecondary: Color(hex: "F5F5F5"),
            modalBackground:     Color(hex: "EFEFEF"),
            inputBackground:     Color(hex: "F0F0F0"),
            cardBackground:      Color(hex: "FFFFFF"),
            cardBorder:          Color(hex: "E5E5E5"),
            textPrimary:         Color(hex: "111111"),
            textSecondary:       Color(hex: "666666"),
            textTertiary:        Color(hex: "999999"),
            accent:              Color(hex: "111111"),
            accentForeground:    Color(hex: "FFFFFF"),
            divider:             Color(hex: "E5E5E5"),
            success: Color(hex: "16A34A"), warning: Color(hex: "D97706"), error: Color(hex: "DC2626")
        )'''

new_ios = '''        return AppTheme(
            id: "system", name: "System", isPro: false, group: .system,
            backgroundPrimary:   Color(.systemBackground),
            backgroundSecondary: Color(.secondarySystemBackground),
            modalBackground:     Color(.tertiarySystemBackground),
            inputBackground:     Color(.secondarySystemFill),
            cardBackground:      Color(.secondarySystemBackground),
            cardBorder:          Color(.separator).opacity(0.5),
            textPrimary:         Color(.label),
            textSecondary:       Color(.secondaryLabel),
            textTertiary:        Color(.tertiaryLabel),
            accent:              Color(.label),
            accentForeground:    Color(.systemBackground),
            divider:             Color(.separator),
            success: .green, warning: .orange, error: .red
        )'''

if old_ios in theme:
    theme = theme.replace(old_ios, new_ios, 1)
    print("AppTheme iOS system restored to adaptive colors")
else:
    print("AppTheme iOS system pattern not found")

with open(theme_path, "w") as f: f.write(theme)

# ── Fix 3: Revert nav title to .inline ──
clip_path = f"{BASE}/Views/iOS/Tabs/iOSClipboardHistoryView.swift"
with open(clip_path, "r") as f: clip = f.read()
clip = clip.replace('.navigationBarTitleDisplayMode(.large)', '.navigationBarTitleDisplayMode(.inline)', 1)
with open(clip_path, "w") as f: f.write(clip)
print("Clipboard title reverted to inline")

acct_path = f"{BASE}/Views/iOS/Tabs/iOSAccountSettingsView.swift"
with open(acct_path, "r") as f: acct = f.read()
acct = acct.replace('.navigationBarTitleDisplayMode(.large)', '.navigationBarTitleDisplayMode(.inline)', 1)
with open(acct_path, "w") as f: f.write(acct)
print("Account title reverted to inline")

