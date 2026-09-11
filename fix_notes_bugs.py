#!/usr/bin/env python3
"""
Fix two notes bugs:
1. macOS text color wrong for notes synced from iOS — add color stripping in NotesStore init?(row:)
2. iOS bullet/number list not continuing on Return — add shouldChangeTextIn delegate method
"""

import re

# ─── Fix 1: NotesStore.swift — strip explicit colors in init?(row:) on macOS ───

notes_store_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/NotesStore.swift"

with open(notes_store_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = '''        self.init(
            id:           uuid,
            title:        row.title,
            content:      body,
            createdDate:  row.created_date,
            modifiedDate: row.modified_date,
            folderID:     row.folder_id.flatMap(UUID.init)
        )
    }
}'''

new_block = '''        // Ensure text colour adapts to dark/light mode on macOS.
        // Notes created on iOS embed explicit UIColor values in the HTML which
        // render as dark grey on macOS dark mode. Strip them and replace with
        // the semantic NSColor.textColor so the editor always shows readable text.
        #if os(macOS)
        let adaptedBody: NSAttributedString = {
            let mutable = NSMutableAttributedString(attributedString: body)
            let range = NSRange(location: 0, length: mutable.length)
            mutable.addAttribute(.foregroundColor, value: NSColor.textColor, range: range)
            return mutable
        }()
        #else
        let adaptedBody = body
        #endif

        self.init(
            id:           uuid,
            title:        row.title,
            content:      adaptedBody,
            createdDate:  row.created_date,
            modifiedDate: row.modified_date,
            folderID:     row.folder_id.flatMap(UUID.init)
        )
    }
}'''

if old_block in content:
    content = content.replace(old_block, new_block, 1)
    with open(notes_store_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ NotesStore.swift — color stripping added to init?(row:)")
else:
    print("✗ NotesStore.swift — could not find init?(row:) self.init block")

# ─── Fix 2: iOSQuickNotesView.swift — add shouldChangeTextIn for list continuation ───

ios_notes_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSQuickNotesView.swift"

with open(ios_notes_path, "r", encoding="utf-8") as f:
    content = f.read()

# Insert shouldChangeTextIn right after textViewDidChangeSelection
old_delegate = '''        func textViewDidChangeSelection(_ tv: UITextView) {
            updateToolbarActiveState(for: tv)
        }'''

new_delegate = '''        func textViewDidChangeSelection(_ tv: UITextView) {
            updateToolbarActiveState(for: tv)
        }

        // MARK: - List continuation on Return
        func textView(_ tv: UITextView, shouldChangeTextIn range: NSRange, replacementText text: String) -> Bool {
            guard text == "\\n" else { return true }
            let nsStr = tv.attributedText.string as NSString
            let lineRange = nsStr.lineRange(for: NSRange(location: range.location, length: 0))
            let lineText  = nsStr.substring(with: lineRange)

            // ── Bullet list ──────────────────────────────────────────────────
            if lineText.hasPrefix("\\u{2022} ") {
                let content = String(lineText.dropFirst(2))
                    .trimmingCharacters(in: .newlines)
                if content.trimmingCharacters(in: .whitespaces).isEmpty {
                    // Empty bullet → exit list: replace the whole line with a blank line
                    let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                    let replaceRange = NSRange(location: lineRange.location, length: lineRange.length)
                    mutable.replaceCharacters(in: replaceRange, with: "\\n")
                    tv.attributedText = mutable
                    tv.selectedRange  = NSRange(location: lineRange.location + 1, length: 0)
                    parent.attributedText = mutable
                } else {
                    // Continue bullet on next line
                    let attrs = tv.typingAttributes
                    let insertion = NSAttributedString(string: "\\n\\u{2022} ", attributes: attrs)
                    let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                    mutable.replaceCharacters(in: range, with: insertion)
                    tv.attributedText = mutable
                    tv.selectedRange  = NSRange(location: range.location + insertion.length, length: 0)
                    parent.attributedText = mutable
                }
                return false
            }

            // ── Numbered list ────────────────────────────────────────────────
            let numRegex = try? NSRegularExpression(pattern: "^(\\\\d+)\\\\. ")
            if let regex = numRegex,
               let match = regex.firstMatch(in: lineText, range: NSRange(location: 0, length: (lineText as NSString).length)) {
                let numRange = Range(match.range(at: 1), in: lineText)!
                let num      = Int(lineText[numRange]) ?? 0
                let prefixLen = match.range.length
                let content  = String(lineText.dropFirst(prefixLen))
                    .trimmingCharacters(in: .newlines)
                if content.trimmingCharacters(in: .whitespaces).isEmpty {
                    // Empty numbered line → exit list
                    let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                    let replaceRange = NSRange(location: lineRange.location, length: lineRange.length)
                    mutable.replaceCharacters(in: replaceRange, with: "\\n")
                    tv.attributedText = mutable
                    tv.selectedRange  = NSRange(location: lineRange.location + 1, length: 0)
                    parent.attributedText = mutable
                } else {
                    let attrs = tv.typingAttributes
                    let insertion = NSAttributedString(string: "\\n\\(num + 1). ", attributes: attrs)
                    let mutable = NSMutableAttributedString(attributedString: tv.attributedText)
                    mutable.replaceCharacters(in: range, with: insertion)
                    tv.attributedText = mutable
                    tv.selectedRange  = NSRange(location: range.location + insertion.length, length: 0)
                    parent.attributedText = mutable
                }
                return false
            }

            return true
        }'''

if old_delegate in content:
    content = content.replace(old_delegate, new_delegate, 1)
    with open(ios_notes_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ iOSQuickNotesView.swift — list continuation delegate method added")
else:
    print("✗ iOSQuickNotesView.swift — could not find textViewDidChangeSelection block")
