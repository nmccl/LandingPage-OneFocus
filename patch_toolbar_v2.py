#!/usr/bin/env python3
"""
Replace the two-row dumped toolbar (lines 454-857) with a clean single-row
iOS Notes-style toolbar:
  [Bold] [Italic] [Underline] [Aa ▾]  ··· flex ···  [✓ Done]

Tapping "Aa" presents a UIViewController popover with grouped rows:
  Row 1: Bold  Italic  Underline  Strikethrough
  Row 2: Bullet  Numbered list
  Row 3: Align Left  Center  Right  Justify
  Row 4: Font Size (Aa small/large)  Text Colour (circle)
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSQuickNotesView.swift"

with open(path, 'r') as f:
    lines = f.readlines()

# Find start (makeToolbar) and end (last line before findViewController extension)
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'func makeToolbar() -> UIView {' in line and start_line is None:
        start_line = i  # 0-indexed
    if 'func findViewController()' in line:
        end_line = i    # 0-indexed, keep this line
        break

assert start_line is not None and end_line is not None, f"Could not find range: start={start_line}, end={end_line}"
print(f"Replacing lines {start_line+1}–{end_line} ({end_line - start_line} lines)")

new_toolbar_code = '''        // MARK: - Keyboard toolbar (iOS Notes style)

        func makeToolbar() -> UIView {
            let h: CGFloat = 44
            let bar = UIToolbar(frame: CGRect(x: 0, y: 0, width: UIScreen.main.bounds.width, height: h))
            bar.autoresizingMask = [.flexibleWidth]
            bar.sizeToFit()

            boldBtn        = toolbarBtn("bold",          action: #selector(toggleBold))
            italicBtn      = toolbarBtn("italic",        action: #selector(toggleItalic))
            underlineBtn   = toolbarBtn("underline",     action: #selector(toggleUnderline))

            let aaBtn = UIBarButtonItem(title: "Aa", style: .plain, target: self, action: #selector(showFormatPanel))
            aaBtn.setTitleTextAttributes([
                .font: UIFont.systemFont(ofSize: 16, weight: .medium)
            ], for: .normal)

            let flex = UIBarButtonItem(barButtonSystemItem: .flexibleSpace, target: nil, action: nil)
            let done = UIBarButtonItem(title: "Done", style: .done, target: self, action: #selector(dismissKeyboard))

            bar.items = [
                boldBtn!, flex,
                italicBtn!, flex,
                underlineBtn!, flex,
                aaBtn, flex,
                done
            ]
            return bar
        }

        // MARK: - Format panel (popover)

        @objc func showFormatPanel() {
            guard let tv = textView, let vc = tv.findViewController() else { return }
            let panel = FormatPanelViewController(coordinator: self)
            panel.modalPresentationStyle = .popover
            panel.preferredContentSize   = CGSize(width: 280, height: 220)
            if let pop = panel.popoverPresentationController {
                pop.sourceView = tv
                // Anchor to the top-centre of the text view (near the toolbar)
                pop.sourceRect = CGRect(x: tv.bounds.midX, y: 0, width: 0, height: 0)
                pop.permittedArrowDirections = .down
                pop.delegate = panel
            }
            vc.present(panel, animated: true)
        }

        // MARK: - Toolbar active-state

        func updateToolbarActiveState(for tv: UITextView) {
            let attrs = tv.typingAttributes
            let font  = attrs[.font] as? UIFont ?? UIFont.preferredFont(forTextStyle: .body)
            let bold  = font.fontDescriptor.symbolicTraits.contains(.traitBold)
            let ital  = font.fontDescriptor.symbolicTraits.contains(.traitItalic)
            let under = (attrs[.underlineStyle] as? Int ?? 0) != 0
            let accent = UIColor.systemBlue
            let normal = UIColor.label
            boldBtn?.tintColor      = bold  ? accent : normal
            italicBtn?.tintColor    = ital  ? accent : normal
            underlineBtn?.tintColor = under ? accent : normal
        }

        // MARK: - Format actions

        @objc func toggleBold()          { applyTrait(.traitBold) }
        @objc func toggleItalic()        { applyTrait(.traitItalic) }
        @objc func toggleUnderline()     { applyIntAttribute(.underlineStyle,     toggleValue: NSUnderlineStyle.single.rawValue) }
        @objc func toggleStrikethrough() { applyIntAttribute(.strikethroughStyle, toggleValue: NSUnderlineStyle.single.rawValue) }

        @objc func insertBullet() {
            guard let tv = textView else { return }
            let sel = tv.selectedRange
            let text = tv.attributedText.string as NSString
            // Find the start of the current line
            let lineRange = text.lineRange(for: NSRange(location: sel.location, length: 0))
            let lineText  = text.substring(with: lineRange)
            let mutable   = NSMutableAttributedString(attributedString: tv.attributedText)
            if lineText.hasPrefix("• ") {
                // Remove bullet
                let removeRange = NSRange(location: lineRange.location, length: 2)
                mutable.deleteCharacters(in: removeRange)
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: max(0, sel.location - 2), length: 0)
            } else {
                let bullet = NSAttributedString(string: "• ", attributes: tv.typingAttributes)
                mutable.insert(bullet, at: lineRange.location)
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: sel.location + 2, length: 0)
            }
            parent.attributedText = mutable
        }

        @objc func insertNumberedList() {
            guard let tv = textView else { return }
            let sel  = tv.selectedRange
            let text = tv.attributedText.string as NSString
            let lineRange = text.lineRange(for: NSRange(location: sel.location, length: 0))
            let lineText  = text.substring(with: lineRange)
            let mutable   = NSMutableAttributedString(attributedString: tv.attributedText)
            // Check if already numbered
            let numRegex  = try? NSRegularExpression(pattern: "^\\d+\\. ")
            let isNum     = numRegex?.firstMatch(in: lineText, range: NSRange(lineText.startIndex..., in: lineText)) != nil
            if isNum {
                // Remove "N. " prefix
                if let match = numRegex?.firstMatch(in: lineText, range: NSRange(lineText.startIndex..., in: lineText)) {
                    let removeLen = match.range.length
                    mutable.deleteCharacters(in: NSRange(location: lineRange.location, length: removeLen))
                    tv.attributedText = mutable
                    tv.selectedRange  = NSRange(location: max(0, sel.location - removeLen), length: 0)
                }
            } else {
                // Find what number to use
                var num = 1
                if lineRange.location > 0 {
                    let prevLineRange = text.lineRange(for: NSRange(location: lineRange.location - 1, length: 0))
                    let prevLine = text.substring(with: prevLineRange)
                    if let match = numRegex?.firstMatch(in: prevLine, range: NSRange(prevLine.startIndex..., in: prevLine)) {
                        let numStr = (prevLine as NSString).substring(with: NSRange(location: 0, length: match.range.length - 2))
                        num = (Int(numStr) ?? 0) + 1
                    }
                }
                let prefix = NSAttributedString(string: "\\(num). ", attributes: tv.typingAttributes)
                mutable.insert(prefix, at: lineRange.location)
                tv.attributedText = mutable
                tv.selectedRange  = NSRange(location: sel.location + prefix.length, length: 0)
            }
            parent.attributedText = mutable
        }

        @objc func alignLeft()    { setAlignment(.left) }
        @objc func alignCenter()  { setAlignment(.center) }
        @objc func alignRight()   { setAlignment(.right) }
        @objc func alignJustify() { setAlignment(.justified) }

        private func setAlignment(_ alignment: NSTextAlignment) {
            guard let tv = textView else { return }
            let sel = tv.selectedRange
            let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
            let text = tv.attributedText.string as NSString
            let lineRange = sel.length > 0
                ? text.lineRange(for: sel)
                : text.lineRange(for: NSRange(location: sel.location, length: 0))
            let style = NSMutableParagraphStyle()
            style.alignment = alignment
            mutable.addAttribute(.paragraphStyle, value: style, range: lineRange)
            tv.attributedText = mutable
            tv.selectedRange  = sel
            parent.attributedText = mutable
            var typingAttrs = tv.typingAttributes
            typingAttrs[.paragraphStyle] = style
            tv.typingAttributes = typingAttrs
        }

        @objc func increaseFontSize() { adjustFontSize(by: +2) }
        @objc func decreaseFontSize() { adjustFontSize(by: -2) }

        private func adjustFontSize(by delta: CGFloat) {
            guard let tv = textView else { return }
            let currentFont = tv.typingAttributes[.font] as? UIFont
                ?? UIFont.preferredFont(forTextStyle: .body)
            let newSize = max(10, min(36, currentFont.pointSize + delta))
            tv.typingAttributes[.font] = currentFont.withSize(newSize)
            let range = tv.selectedRange
            if range.length > 0 {
                let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                mutable.enumerateAttribute(.font, in: range) { val, r, _ in
                    let f = (val as? UIFont) ?? UIFont.preferredFont(forTextStyle: .body)
                    mutable.addAttribute(.font, value: f.withSize(max(10, min(36, f.pointSize + delta))), range: r)
                }
                tv.attributedText = mutable
                tv.selectedRange  = range
                parent.attributedText = mutable
            }
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

        private func toolbarBtn(_ image: String, action: Selector) -> UIBarButtonItem {
            UIBarButtonItem(
                image: UIImage(systemName: image),
                style: .plain,
                target: self,
                action: action
            )
        }

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

// MARK: - Format Panel (popover presented by "Aa" button)

private final class FormatPanelViewController: UIViewController, UIPopoverPresentationControllerDelegate {

    weak var coordinator: iOSRichTextEditor.Coordinator?

    init(coordinator: iOSRichTextEditor.Coordinator) {
        self.coordinator = coordinator
        super.init(nibName: nil, bundle: nil)
    }
    required init?(coder: NSCoder) { fatalError() }

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor.systemBackground

        // ── Row 1: Bold · Italic · Underline · Strikethrough ──────────────
        let boldBtn  = iconButton("bold",          action: #selector(bold))
        let italBtn  = iconButton("italic",        action: #selector(italic))
        let undBtn   = iconButton("underline",     action: #selector(underline))
        let striBtn  = iconButton("strikethrough", action: #selector(strikethrough))
        let row1     = hStack([boldBtn, italBtn, undBtn, striBtn])

        // ── Row 2: Bullet · Numbered list ─────────────────────────────────
        let bulBtn   = iconButton("list.bullet",  action: #selector(bullet))
        let numBtn   = iconButton("list.number",  action: #selector(numbered))
        let row2     = hStack([bulBtn, numBtn])

        // ── Row 3: Alignment ───────────────────────────────────────────────
        let aL = iconButton("text.alignleft",    action: #selector(alignL))
        let aC = iconButton("text.aligncenter",  action: #selector(alignC))
        let aR = iconButton("text.alignright",   action: #selector(alignR))
        let aJ = iconButton("text.justify",      action: #selector(alignJ))
        let row3 = hStack([aL, aC, aR, aJ])

        // ── Row 4: Font size · Text colour ────────────────────────────────
        let smallA = sizeButton("A", size: 14, action: #selector(smaller))
        let bigA   = sizeButton("A", size: 22, action: #selector(larger))
        let colBtn = colorCircleButton()
        let row4   = hStack([smallA, bigA, colBtn])

        // ── Dividers ───────────────────────────────────────────────────────
        func div() -> UIView {
            let v = UIView(); v.backgroundColor = UIColor.separator
            v.translatesAutoresizingMaskIntoConstraints = false
            v.heightAnchor.constraint(equalToConstant: 0.5).isActive = true
            return v
        }

        let stack = UIStackView(arrangedSubviews: [row1, div(), row2, div(), row3, div(), row4])
        stack.axis      = .vertical
        stack.spacing   = 0
        stack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            stack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            stack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -8),
        ])
    }

    // ── Helpers ────────────────────────────────────────────────────────────

    private func iconButton(_ image: String, action: Selector) -> UIButton {
        let b = UIButton(type: .system)
        b.setImage(UIImage(systemName: image), for: .normal)
        b.tintColor = .label
        b.addTarget(self, action: action, for: .touchUpInside)
        b.translatesAutoresizingMaskIntoConstraints = false
        b.widthAnchor.constraint(equalToConstant: 52).isActive = true
        b.heightAnchor.constraint(equalToConstant: 44).isActive = true
        return b
    }

    private func sizeButton(_ letter: String, size: CGFloat, action: Selector) -> UIButton {
        let b = UIButton(type: .system)
        b.setTitle(letter, for: .normal)
        b.titleLabel?.font = UIFont.systemFont(ofSize: size, weight: .regular)
        b.setTitleColor(.label, for: .normal)
        b.addTarget(self, action: action, for: .touchUpInside)
        b.translatesAutoresizingMaskIntoConstraints = false
        b.widthAnchor.constraint(equalToConstant: 52).isActive = true
        b.heightAnchor.constraint(equalToConstant: 44).isActive = true
        return b
    }

    private func colorCircleButton() -> UIButton {
        let b = UIButton(type: .system)
        b.setImage(UIImage(systemName: "circle.fill")?.withTintColor(.systemBlue, renderingMode: .alwaysOriginal), for: .normal)
        b.addTarget(self, action: #selector(pickColor), for: .touchUpInside)
        b.translatesAutoresizingMaskIntoConstraints = false
        b.widthAnchor.constraint(equalToConstant: 52).isActive = true
        b.heightAnchor.constraint(equalToConstant: 44).isActive = true
        return b
    }

    private func hStack(_ views: [UIView]) -> UIStackView {
        let s = UIStackView(arrangedSubviews: views)
        s.axis      = .horizontal
        s.spacing   = 0
        s.alignment = .center
        return s
    }

    // ── Actions ────────────────────────────────────────────────────────────

    @objc private func bold()          { coordinator?.toggleBold();          dismiss(animated: true) }
    @objc private func italic()        { coordinator?.toggleItalic();        dismiss(animated: true) }
    @objc private func underline()     { coordinator?.toggleUnderline();     dismiss(animated: true) }
    @objc private func strikethrough() { coordinator?.toggleStrikethrough(); dismiss(animated: true) }
    @objc private func bullet()        { coordinator?.insertBullet();        dismiss(animated: true) }
    @objc private func numbered()      { coordinator?.insertNumberedList();  dismiss(animated: true) }
    @objc private func alignL()        { coordinator?.alignLeft();           dismiss(animated: true) }
    @objc private func alignC()        { coordinator?.alignCenter();         dismiss(animated: true) }
    @objc private func alignR()        { coordinator?.alignRight();          dismiss(animated: true) }
    @objc private func alignJ()        { coordinator?.alignJustify();        dismiss(animated: true) }
    @objc private func smaller()       { coordinator?.decreaseFontSize();    dismiss(animated: true) }
    @objc private func larger()        { coordinator?.increaseFontSize();    dismiss(animated: true) }

    @objc private func pickColor() {
        let palette: [(String, UIColor)] = [
            ("Default", .label), ("Red", .systemRed), ("Orange", .systemOrange),
            ("Yellow", .systemYellow), ("Green", .systemGreen), ("Blue", .systemBlue),
            ("Purple", .systemPurple), ("Pink", .systemPink), ("Gray", .systemGray),
        ]
        let sheet = UIAlertController(title: "Text Colour", message: nil, preferredStyle: .actionSheet)
        for (name, color) in palette {
            let action = UIAlertAction(title: name, style: .default) { [weak self] _ in
                self?.coordinator?.applyTextColor(color)
            }
            action.setValue(
                UIImage(systemName: "circle.fill")?.withTintColor(color, renderingMode: .alwaysOriginal),
                forKey: "image"
            )
            sheet.addAction(action)
        }
        sheet.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        if let pop = sheet.popoverPresentationController {
            pop.sourceView = view
            pop.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.maxY, width: 0, height: 0)
        }
        present(sheet, animated: true)
    }

    // Keep popover on iPhone (don't fall back to full-screen sheet)
    func adaptivePresentationStyle(for controller: UIPresentationController) -> UIModalPresentationStyle {
        return .none
    }
}

'''

# Replace lines start_line..end_line-1 (keep end_line onwards)
new_lines = lines[:start_line] + [new_toolbar_code] + lines[end_line:]

with open(path, 'w') as f:
    f.writelines(new_lines)

print(f"Done. Replaced {end_line - start_line} lines with new toolbar + FormatPanelViewController.")
