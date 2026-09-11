"""
Replace the iOS #else block of the system theme (lines 107-124) in AppTheme.swift.

The replacement uses UIColor(dynamicProvider:) with exact RGB values from
defaultDark and defaultLight, so System theme is pixel-identical to those themes.

No new extensions or imports needed — UIColor(dynamicProvider:) and UIColor(red:green:blue:alpha:)
are standard UIKit APIs available on all iOS versions we support.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/AppTheme.swift"
with open(path) as f:
    lines = f.readlines()

# Find the #else line inside the system theme block (line 107, 0-indexed: 106)
# and the #endif line (line 124, 0-indexed: 123)
else_line = None
endif_line = None
inside_system = False

for i, line in enumerate(lines):
    if "static let system: AppTheme = {" in line:
        inside_system = True
    if inside_system and line.strip() == "#else":
        else_line = i
    if inside_system and line.strip() == "#endif":
        endif_line = i
        break

if else_line is None or endif_line is None:
    print(f"FAIL: could not find #else ({else_line}) or #endif ({endif_line}) in system theme block")
    exit(1)

print(f"Replacing lines {else_line+1}-{endif_line+1} (0-indexed {else_line}-{endif_line})")

# The new iOS block — uses UIColor(dynamicProvider:) with exact defaultDark/defaultLight hex values
# defaultDark:  bg=1C1C1E, bgSec=2C2C2E, modal=3A3A3C, input=3A3A3C, card=2C2C2E, border=48484A
#               textPrimary=F2F2F7, textSec=8E8E93, textTert=636366, accent=999999, accentFg=111111, divider=38383A
# defaultLight: bg=FFFFFF, bgSec=F5F5F5, modal=EFEFEF, input=F0F0F0, card=FFFFFF, border=E5E5E5
#               textPrimary=111111, textSec=666666, textTert=999999, accent=111111, accentFg=FFFFFF, divider=E5E5E5

new_block = """#else
        // Use UIColor(dynamicProvider:) so System theme uses exactly the same
        // colors as defaultDark (dark mode) and defaultLight (light mode).
        // No extensions needed — UIColor(dynamicProvider:) is standard UIKit.
        func dyn(dark r1: CGFloat, _ g1: CGFloat, _ b1: CGFloat,
                 light r2: CGFloat, _ g2: CGFloat, _ b2: CGFloat) -> Color {
            Color(UIColor(dynamicProvider: { t in
                t.userInterfaceStyle == .dark
                    ? UIColor(red: r1/255, green: g1/255, blue: b1/255, alpha: 1)
                    : UIColor(red: r2/255, green: g2/255, blue: b2/255, alpha: 1)
            }))
        }
        return AppTheme(
            id: "system", name: "System", isPro: false, group: .system,
            backgroundPrimary:   dyn(dark: 28,  28,  30,  light: 255, 255, 255),
            backgroundSecondary: dyn(dark: 44,  44,  46,  light: 245, 245, 245),
            modalBackground:     dyn(dark: 58,  58,  60,  light: 239, 239, 239),
            inputBackground:     dyn(dark: 58,  58,  60,  light: 240, 240, 240),
            cardBackground:      dyn(dark: 44,  44,  46,  light: 255, 255, 255),
            cardBorder:          dyn(dark: 72,  72,  74,  light: 229, 229, 229),
            textPrimary:         dyn(dark: 242, 242, 247, light: 17,  17,  17 ),
            textSecondary:       dyn(dark: 142, 142, 147, light: 102, 102, 102),
            textTertiary:        dyn(dark: 99,  99,  102, light: 153, 153, 153),
            accent:              dyn(dark: 153, 153, 153, light: 17,  17,  17 ),
            accentForeground:    dyn(dark: 17,  17,  17,  light: 255, 255, 255),
            divider:             dyn(dark: 56,  56,  58,  light: 229, 229, 229),
            success: Color(hex: "30D158"), warning: Color(hex: "FF9F0A"), error: Color(hex: "FF453A")
        )
#endif
"""

lines[else_line:endif_line+1] = [new_block]

with open(path, "w") as f:
    f.writelines(lines)

# Verify
with open(path) as f:
    result = f.read()

ok1 = "UIColor(dynamicProvider:" in result
ok2 = "userInterfaceStyle == .dark" in result
ok3 = "28,  28,  30" in result   # dark backgroundPrimary = #1C1C1E = rgb(28,28,30)
ok4 = "255, 255, 255" in result  # light backgroundPrimary = #FFFFFF
print(("OK" if ok1 else "FAIL") + ": uses UIColor(dynamicProvider:)")
print(("OK" if ok2 else "FAIL") + ": checks userInterfaceStyle")
print(("OK" if ok3 else "FAIL") + ": dark bg = rgb(28,28,30) = #1C1C1E")
print(("OK" if ok4 else "FAIL") + ": light bg = rgb(255,255,255) = #FFFFFF")
