#!/usr/bin/env python3
"""
Fix three bugs:
1. NotesStore.swift Note(row:) - strip hardcoded foreground colors after HTML decode
2. iOSQuickNotesView.swift makeUIView - set stable typingAttributes font on load
3. AppLockView.swift - fix invisible button text (white on white/near-white)
"""
import re

# ─── 1. NotesStore.swift ───────────────────────────────────────────────────────
notes_store_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/NotesStore.swift"

with open(notes_store_path, "r") as f:
    src = f.read()

old_decode = '''        if !html.isEmpty,
           let data = html.data(using: .utf8),
           let attr = try? NSAttributedString(
               data: data,
               options: [
                   .documentType: NSAttributedString.DocumentType.html,
                   .characterEncoding: String.Encoding.utf8.rawValue
               ],
               documentAttributes: nil
           ) {
            body = attr
        } else {
            body = NSAttributedString(string: "")
        }'''

new_decode = '''        if !html.isEmpty,
           let data = html.data(using: .utf8),
           let attr = try? NSAttributedString(
               data: data,
               options: [
                   .documentType: NSAttributedString.DocumentType.html,
                   .characterEncoding: String.Encoding.utf8.rawValue
               ],
               documentAttributes: nil
           ) {
            // Strip hardcoded foreground colors baked in by the HTML encoder on
            // the other platform (e.g. macOS encodes NSColor.textColor as a
            // light-gray CSS color which is invisible on iOS dark backgrounds,
            // and vice-versa). Replace with the platform adaptive text color
            // so the note always renders correctly in the current theme.
            let mutable = NSMutableAttributedString(attributedString: attr)
            let fullRange = NSRange(location: 0, length: mutable.length)
            mutable.removeAttribute(.foregroundColor, range: fullRange)
            #if os(macOS)
            mutable.addAttribute(.foregroundColor, value: NSColor.textColor, range: fullRange)
            #else
            mutable.addAttribute(.foregroundColor, value: UIColor.label, range: fullRange)
            #endif
            body = mutable
        } else {
            body = NSAttributedString(string: "")
        }'''

if old_decode in src:
    src = src.replace(old_decode, new_decode)
    with open(notes_store_path, "w") as f:
        f.write(src)
    print("✓ NotesStore.swift: foreground color stripping added")
else:
    print("✗ NotesStore.swift: pattern not found — check manually")

# ─── 2. iOSQuickNotesView.swift ───────────────────────────────────────────────
ios_notes_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSQuickNotesView.swift"

with open(ios_notes_path, "r") as f:
    src2 = f.read()

# After setting tv.attributedText in makeUIView, set stable typingAttributes
old_make = '''        if attributedText.length > 0 {
            tv.attributedText = attributedText
        }
        return tv'''

new_make = '''        if attributedText.length > 0 {
            tv.attributedText = attributedText
        }
        // Set stable default typingAttributes so that characters typed after
        // an HTML-decoded note inherit a consistent iOS system font instead of
        // whatever font was embedded in the cross-platform HTML. This prevents
        // the font from randomly changing mid-typing.
        tv.typingAttributes = [
            .font: UIFont.systemFont(ofSize: 17),
            .foregroundColor: UIColor.label
        ]
        return tv'''

if old_make in src2:
    src2 = src2.replace(old_make, new_make)
    with open(ios_notes_path, "w") as f:
        f.write(src2)
    print("✓ iOSQuickNotesView.swift: stable typingAttributes set on load")
else:
    print("✗ iOSQuickNotesView.swift: makeUIView pattern not found — check manually")

# ─── 3. AppLockView.swift ─────────────────────────────────────────────────────
lock_view_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/AppLockView.swift"

with open(lock_view_path, "r") as f:
    src3 = f.read()

# The button uses .foregroundColor(.white) hardcoded — in dark mode textPrimary
# is near-white (#F2F2F7), making the button background near-white and the
# white label invisible. Use accentForeground which is always the inverse.
old_btn = '''                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(AppConstants.Colors.textPrimary)'''

new_btn = '''                        .foregroundColor(AppConstants.Colors.accentForeground)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(AppConstants.Colors.accent)'''

if old_btn in src3:
    src3 = src3.replace(old_btn, new_btn)
    with open(lock_view_path, "w") as f:
        f.write(src3)
    print("✓ AppLockView.swift: button foreground/background fixed")
else:
    print("✗ AppLockView.swift: button pattern not found — printing relevant lines:")
    for i, line in enumerate(src3.splitlines(), 1):
        if "foregroundColor" in line or "background" in line or "textPrimary" in line:
            print(f"  {i}: {line}")
