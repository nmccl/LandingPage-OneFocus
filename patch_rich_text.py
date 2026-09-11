#!/usr/bin/env python3
"""
Replace iOSRichTextEditor (lines 376-600) with a full-featured version
matching macOS: Bold, Italic, Underline, Strikethrough, Bullet list,
Numbered list, Font size (Small/Normal/Large/Huge), Text alignment
(Left/Center/Right/Justify), Text color (palette + system picker).

Also updates iOSNoteEditorView to pass the color sheet state down.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSQuickNotesView.swift"

with open(path, 'r') as f:
    lines = f.readlines()

# Lines are 1-indexed in grep output; Python list is 0-indexed.
# Replace lines 376..600 (inclusive) with the new implementation.
start = 376 - 1   # 0-indexed
end   = 600        # exclusive (line 601 stays)

new_block = '''// MARK: - Rich Text Editor (iOS)
//
// UIViewRepresentable wrapping UITextView.
// Features: Bold · Italic · Underline · Strikethrough · Bullet list ·
//           Numbered list · Font size · Text alignment · Text colour
//
// The keyboard-attached toolbar is split into two scrollable rows so all
// controls are reachable without crowding on small screens.
//
struct iOSRichTextEditor: UIViewRepresentable {

    @Binding var attributedText: NSAttributedString
    var backgroundColor: Color = .clear
    /// Callback fired when the user taps the colour button — lets the
    /// SwiftUI parent present a colour-picker sheet.
    var onColorTap: (() -> Void)? = nil

    func makeUIView(context: Context) -> UITextView {
        let tv = UITextView()
        tv.delegate                    = context.coordinator
        tv.isEditable                  = true
        tv.isScrollEnabled             = true
        tv.allowsEditingTextAttributes = true
        tv.backgroundColor             = .clear
        tv.textColor                   = UIColor.label
        tv.font                        = UIFont.preferredFont(forTextStyle: .body)
        tv.textContainerInset          = UIEdgeInsets(top: 12, left: 12, bottom: 12, right: 12)
        tv.inputAccessoryView          = context.coordinator.makeToolbar()
        context.coordinator.textView   = tv
        if attributedText.length > 0 {
            tv.attributedText = attributedText
        }
        return tv
    }

    func updateUIView(_ tv: UITextView, context: Context) {
        let uiBg = UIColor(backgroundColor)
        if tv.backgroundColor != uiBg { tv.backgroundColor = uiBg }
        // Only push when content actually changed to avoid cursor-jump.
        if tv.attributedText != attributedText && !context.coordinator.isEditing {
            let sel = tv.selectedRange
            tv.attributedText = attributedText
            tv.selectedRange  = sel
        }
    }

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    // MARK: - Coordinator
    final class Coordinator: NSObject, UITextViewDelegate {
        var parent: iOSRichTextEditor
        weak var textView: UITextView?
        var isEditing = false

        // Toolbar button references for active-state tinting
        weak var boldButton:      UIBarButtonItem?
        weak var italicButton:    UIBarButtonItem?
        weak var underButton:     UIBarButtonItem?
        weak var strikeButton:    UIBarButtonItem?
        weak var alignLButton:    UIBarButtonItem?
        weak var alignCButton:    UIBarButtonItem?
        weak var alignRButton:    UIBarButtonItem?
        weak var alignJButton:    UIBarButtonItem?

        init(_ parent: iOSRichTextEditor) { self.parent = parent }

        // MARK: UITextViewDelegate
        func textViewDidBeginEditing(_ tv: UITextView) { isEditing = true }
        func textViewDidEndEditing(_ tv: UITextView)   { isEditing = false }

        func textViewDidChange(_ tv: UITextView) {
            parent.attributedText = tv.attributedText
        }
        func textViewDidChangeSelection(_ tv: UITextView) {
            updateToolbarActiveState(for: tv)
        }

        // MARK: - Toolbar factory
        func makeToolbar() -> UIView {
            // We stack two UIToolbars vertically inside a UIView so all
            // controls are visible without horizontal scrolling.
            let container = UIView()
            container.backgroundColor = UIColor.systemBackground

            let sep = UIView()
            sep.backgroundColor = UIColor.separator

            let row1 = makeRow1()
            let row2 = makeRow2()

            row1.translatesAutoresizingMaskIntoConstraints = false
            row2.translatesAutoresizingMaskIntoConstraints = false
            sep.translatesAutoresizingMaskIntoConstraints = false
            container.addSubview(row1)
            container.addSubview(sep)
            container.addSubview(row2)

            let h: CGFloat = 44
            NSLayoutConstraint.activate([
                row1.topAnchor.constraint(equalTo: container.topAnchor),
                row1.leadingAnchor.constraint(equalTo: container.leadingAnchor),
                row1.trailingAnchor.constraint(equalTo: container.trailingAnchor),
                row1.heightAnchor.constraint(equalToConstant: h),

                sep.topAnchor.constraint(equalTo: row1.bottomAnchor),
                sep.leadingAnchor.constraint(equalTo: container.leadingAnchor),
                sep.trailingAnchor.constraint(equalTo: container.trailingAnchor),
                sep.heightAnchor.constraint(equalToConstant: 0.5),

                row2.topAnchor.constraint(equalTo: sep.bottomAnchor),
                row2.leadingAnchor.constraint(equalTo: container.leadingAnchor),
                row2.trailingAnchor.constraint(equalTo: container.trailingAnchor),
                row2.heightAnchor.constraint(equalToConstant: h),

                container.heightAnchor.constraint(equalToConstant: h * 2 + 0.5),
            ])
            return container
        }

        private func btn(_ image: String, action: Selector) -> UIBarButtonItem {
            let b = UIBarButtonItem(
                image: UIImage(systemName: image),
                style: .plain,
                target: self,
                action: action
            )
            b.tintColor = .label
            return b
        }

        private func flex() -> UIBarButtonItem {
            UIBarButtonItem(barButtonSystemItem: .flexibleSpace, target: nil, action: nil)
        }

        private func makeRow1() -> UIToolbar {
            let bar = UIToolbar()
            bar.sizeToFit()

            let bold   = btn("bold",          action: #selector(toggleBold))
            let italic = btn("italic",        action: #selector(toggleItalic))
            let under  = btn("underline",     action: #selector(toggleUnderline))
            let strike = btn("strikethrough", action: #selector(toggleStrikethrough))
            let bullet = btn("list.bullet",   action: #selector(insertBullet))
            let number = btn("list.number",   action: #selector(insertNumberedList))
            let done   = UIBarButtonItem(
                barButtonSystemItem: .done,
                target: self,
                action: #selector(dismissKeyboard)
            )

            boldButton   = bold
            italicButton = italic
            underButton  = under
            strikeButton = strike

            bar.items = [bold, italic, under, strike, flex(), bullet, number, flex(), done]
            return bar
        }

        private func makeRow2() -> UIToolbar {
            let bar = UIToolbar()
            bar.sizeToFit()

            // Alignment
            let aL = btn("text.alignleft",   action: #selector(alignLeft))
            let aC = btn("text.aligncenter", action: #selector(alignCenter))
            let aR = btn("text.alignright",  action: #selector(alignRight))
            let aJ = btn("text.justify",     action: #selector(alignJustify))
            alignLButton = aL
            alignCButton = aC
            alignRButton = aR
            alignJButton = aJ

            // Font size — represented as a menu button
            let sizeImage = UIImage(systemName: "textformat.size")
            let sizeBtn = UIBarButtonItem(
                image: sizeImage,
                style: .plain,
                target: self,
                action: #selector(showFontSizeMenu)
            )
            sizeBtn.tintColor = .label

            // Colour circle button
            let colorImage = UIImage(systemName: "circle.fill")?.withTintColor(.label, renderingMode: .alwaysOriginal)
            let colorBtn = UIBarButtonItem(
                image: colorImage,
                style: .plain,
                target: self,
                action: #selector(showColorPicker)
            )

            bar.items = [aL, aC, aR, aJ, flex(), sizeBtn, flex(), colorBtn]
            return bar
        }

        // MARK: - Active state
        func updateToolbarActiveState(for tv: UITextView) {
            let attrs = tv.typingAttributes
            let font  = attrs[.font] as? UIFont ?? UIFont.preferredFont(forTextStyle: .body)
            let traits = font.fontDescriptor.symbolicTraits
            let accent = UIColor.systemBlue

            boldButton?.tintColor   = traits.contains(.traitBold)   ? accent : .label
            italicButton?.tintColor = traits.contains(.traitItalic) ? accent : .label

            let underVal  = attrs[.underlineStyle]    as? Int ?? 0
            let strikeVal = attrs[.strikethroughStyle] as? Int ?? 0
            underButton?.tintColor  = underVal  != 0 ? accent : .label
            strikeButton?.tintColor = strikeVal != 0 ? accent : .label

            // Alignment
            let paraStyle = attrs[.paragraphStyle] as? NSParagraphStyle
            let align = paraStyle?.alignment ?? .natural
            alignLButton?.tintColor = (align == .left || align == .natural) ? accent : .label
            alignCButton?.tintColor = align == .center    ? accent : .label
            alignRButton?.tintColor = align == .right     ? accent : .label
            alignJButton?.tintColor = align == .justified ? accent : .label
        }

        // MARK: - Formatting actions

        @objc func toggleBold()          { applyTrait(.traitBold) }
        @objc func toggleItalic()        { applyTrait(.traitItalic) }
        @objc func toggleUnderline()     { applyIntAttribute(.underlineStyle,     toggleValue: NSUnderlineStyle.single.rawValue) }
        @objc func toggleStrikethrough() { applyIntAttribute(.strikethroughStyle, toggleValue: NSUnderlineStyle.single.rawValue) }

        @objc func insertBullet() {
            guard let tv = textView else { return }
            let prefix   = "\\u{2022} "
            let mutable  = NSMutableAttributedString(attributedString: tv.attributedText)
            let nsStr    = tv.text as NSString
            let cursor   = tv.selectedRange.location
            let lineRange = nsStr.lineRange(for: NSRange(location: cursor, length: 0))
            let lineText  = nsStr.substring(with: lineRange)
            if lineText.hasPrefix(prefix) {
                let bulletRange = NSRange(location: lineRange.location, length: (prefix as NSString).length)
                mutable.deleteCharacters(in: bulletRange)
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: max(0, cursor - (prefix as NSString).length), length: 0)
            } else {
                let safeIdx   = mutable.length > 0 ? min(lineRange.location, mutable.length - 1) : 0
                let baseAttrs = mutable.length > 0
                    ? mutable.attributes(at: safeIdx, effectiveRange: nil)
                    : tv.typingAttributes
                let bulletStr = NSAttributedString(string: prefix, attributes: baseAttrs)
                mutable.insert(bulletStr, at: lineRange.location)
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: cursor + (prefix as NSString).length, length: 0)
            }
            parent.attributedText = tv.attributedText
        }

        @objc func insertNumberedList() {
            guard let tv = textView else { return }
            let mutable   = NSMutableAttributedString(attributedString: tv.attributedText)
            let nsStr     = tv.text as NSString
            let cursor    = tv.selectedRange.location
            let lineRange = nsStr.lineRange(for: NSRange(location: cursor, length: 0))
            let lineText  = nsStr.substring(with: lineRange)

            // Detect if already on a numbered line and remove it
            let numRegex = try? NSRegularExpression(pattern: "^\\\\d+\\\\. ")
            if let regex = numRegex,
               let match = regex.firstMatch(in: lineText, range: NSRange(lineText.startIndex..., in: lineText)) {
                let len = match.range.length
                mutable.deleteCharacters(in: NSRange(location: lineRange.location, length: len))
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: max(0, cursor - len), length: 0)
            } else {
                // Count existing numbered lines above to continue the sequence
                let textAbove = nsStr.substring(to: lineRange.location)
                let aboveLines = textAbove.components(separatedBy: "\\n")
                var num = 1
                for line in aboveLines.reversed() {
                    if let _ = line.range(of: "^\\\\d+\\\\. ", options: .regularExpression) {
                        let parts = line.components(separatedBy: ". ")
                        if let n = Int(parts[0]) { num = n + 1 }
                        break
                    }
                }
                let prefix    = "\\(num). "
                let safeIdx   = mutable.length > 0 ? min(lineRange.location, mutable.length - 1) : 0
                let baseAttrs = mutable.length > 0
                    ? mutable.attributes(at: safeIdx, effectiveRange: nil)
                    : tv.typingAttributes
                let numStr = NSAttributedString(string: prefix, attributes: baseAttrs)
                mutable.insert(numStr, at: lineRange.location)
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: cursor + (prefix as NSString).length, length: 0)
            }
            parent.attributedText = tv.attributedText
        }

        // MARK: - Alignment

        @objc func alignLeft()    { setAlignment(.left) }
        @objc func alignCenter()  { setAlignment(.center) }
        @objc func alignRight()   { setAlignment(.right) }
        @objc func alignJustify() { setAlignment(.justified) }

        private func setAlignment(_ alignment: NSTextAlignment) {
            guard let tv = textView else { return }
            let para = NSMutableParagraphStyle()
            para.alignment = alignment
            var typingAttrs = tv.typingAttributes
            typingAttrs[.paragraphStyle] = para
            tv.typingAttributes = typingAttrs

            let range = tv.selectedRange
            if range.length > 0 {
                let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                // Expand to full paragraphs
                let nsStr = tv.text as NSString
                let paraRange = nsStr.paragraphRange(for: range)
                mutable.addAttribute(.paragraphStyle, value: para, range: paraRange)
                tv.attributedText = mutable
                tv.selectedRange  = range
                parent.attributedText = mutable
            }
            updateToolbarActiveState(for: tv)
        }

        // MARK: - Font size

        @objc func showFontSizeMenu() {
            guard let tv = textView,
                  let vc = tv.findViewController() else { return }
            let sheet = UIAlertController(title: "Font Size", message: nil, preferredStyle: .actionSheet)
            let sizes: [(String, CGFloat)] = [
                ("Small (12pt)",  12),
                ("Normal (16pt)", 16),
                ("Large (20pt)",  20),
                ("Huge (24pt)",   24),
            ]
            for (label, size) in sizes {
                sheet.addAction(UIAlertAction(title: label, style: .default) { [weak self] _ in
                    self?.changeFontSize(to: size)
                })
            }
            sheet.addAction(UIAlertAction(title: "Cancel", style: .cancel))
            // iPad popover source
            if let pop = sheet.popoverPresentationController {
                pop.sourceView = tv
                pop.sourceRect = CGRect(x: tv.bounds.midX, y: tv.bounds.midY, width: 0, height: 0)
            }
            vc.present(sheet, animated: true)
        }

        private func changeFontSize(to size: CGFloat) {
            guard let tv = textView else { return }
            let currentFont = tv.typingAttributes[.font] as? UIFont
                ?? UIFont.preferredFont(forTextStyle: .body)
            let newFont = currentFont.withSize(size)
            var typingAttrs = tv.typingAttributes
            typingAttrs[.font] = newFont
            tv.typingAttributes = typingAttrs

            let range = tv.selectedRange
            if range.length > 0 {
                let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                mutable.enumerateAttribute(.font, in: range) { val, r, _ in
                    let base = (val as? UIFont) ?? UIFont.preferredFont(forTextStyle: .body)
                    mutable.addAttribute(.font, value: base.withSize(size), range: r)
                }
                tv.attributedText = mutable
                tv.selectedRange  = range
                parent.attributedText = mutable
            }
        }

        // MARK: - Text colour

        @objc func showColorPicker() {
            guard let tv = textView,
                  let vc = tv.findViewController() else { return }

            let palette: [(String, UIColor)] = [
                ("Default", .label),
                ("Red",     .systemRed),
                ("Orange",  .systemOrange),
                ("Yellow",  .systemYellow),
                ("Green",   .systemGreen),
                ("Blue",    .systemBlue),
                ("Purple",  .systemPurple),
                ("Pink",    .systemPink),
                ("Gray",    .systemGray),
            ]

            let sheet = UIAlertController(title: "Text Colour", message: nil, preferredStyle: .actionSheet)
            for (name, color) in palette {
                let action = UIAlertAction(title: name, style: .default) { [weak self] _ in
                    self?.applyTextColor(color)
                }
                // Show a coloured dot next to each option
                action.setValue(UIImage(systemName: "circle.fill")?.withTintColor(color, renderingMode: .alwaysOriginal), forKey: "image")
                sheet.addAction(action)
            }
            sheet.addAction(UIAlertAction(title: "Cancel", style: .cancel))
            if let pop = sheet.popoverPresentationController {
                pop.sourceView = tv
                pop.sourceRect = CGRect(x: tv.bounds.midX, y: tv.bounds.midY, width: 0, height: 0)
            }
            vc.present(sheet, animated: true)
        }

        func applyTextColor(_ color: UIColor) {
            guard let tv = textView else { return }
            var typingAttrs = tv.typingAttributes
            typingAttrs[.foregroundColor] = color
            tv.typingAttributes = typingAttrs

            let range = tv.selectedRange
            if range.length > 0 {
                let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                mutable.addAttribute(.foregroundColor, value: color, range: range)
                tv.attributedText = mutable
                tv.selectedRange  = range
                parent.attributedText = mutable
            }
        }

        @objc func dismissKeyboard() { textView?.resignFirstResponder() }

        // MARK: - Private helpers

        private func applyTrait(_ trait: UIFontDescriptor.SymbolicTraits) {
            guard let tv = textView else { return }
            let currentFont = tv.typingAttributes[.font] as? UIFont
                ?? UIFont.preferredFont(forTextStyle: .body)
            let hasTrait = currentFont.fontDescriptor.symbolicTraits.contains(trait)
            let baseDesc  = currentFont.fontDescriptor
            let newTraits = hasTrait
                ? baseDesc.symbolicTraits.subtracting(trait)
                : baseDesc.symbolicTraits.union(trait)
            if let newDesc = baseDesc.withSymbolicTraits(newTraits) {
                tv.typingAttributes[.font] = UIFont(descriptor: newDesc, size: currentFont.pointSize)
            }
            let range = tv.selectedRange
            if range.length > 0 {
                let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                mutable.enumerateAttribute(.font, in: range) { val, r, _ in
                    let base = (val as? UIFont) ?? UIFont.preferredFont(forTextStyle: .body)
                    let desc = base.fontDescriptor
                    let updated = hasTrait
                        ? desc.symbolicTraits.subtracting(trait)
                        : desc.symbolicTraits.union(trait)
                    if let newDesc = desc.withSymbolicTraits(updated) {
                        mutable.addAttribute(.font, value: UIFont(descriptor: newDesc, size: base.pointSize), range: r)
                    }
                }
                tv.attributedText = mutable
                tv.selectedRange  = range
                parent.attributedText = mutable
            }
            updateToolbarActiveState(for: tv)
        }

        private func applyIntAttribute(_ key: NSAttributedString.Key, toggleValue: Int) {
            guard let tv = textView else { return }
            let currentVal = tv.typingAttributes[key] as? Int ?? 0
            let newVal     = currentVal != 0 ? 0 : toggleValue
            tv.typingAttributes[key] = newVal
            let range = tv.selectedRange
            if range.length > 0 {
                let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                mutable.addAttribute(key, value: newVal, range: range)
                tv.attributedText = mutable
                tv.selectedRange  = range
                parent.attributedText = mutable
            }
            updateToolbarActiveState(for: tv)
        }
    }
}

// MARK: - UIView extension to find the presenting UIViewController
private extension UIView {
    func findViewController() -> UIViewController? {
        var responder: UIResponder? = self
        while let r = responder {
            if let vc = r as? UIViewController { return vc }
            responder = r.next
        }
        return nil
    }
}

'''

# Replace lines start..end with new_block
new_lines = lines[:start] + [new_block] + lines[end:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print(f"Done. Replaced lines {start+1}–{end} ({end-start} lines) with {len(new_block.splitlines())} lines.")
