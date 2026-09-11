path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/NotesStore.swift"
with open(path, "r") as f:
    src = f.read()

old = """    func toRow(userID: String) -> NoteRow {
        let rtfBase64: String
        if let rtfData = try? content.data(
            from: NSRange(location: 0, length: content.length),
            documentAttributes: [.documentType: NSAttributedString.DocumentType.rtf]
        ) {
            rtfBase64 = rtfData.base64EncodedString()
        } else {
            rtfBase64 = (content.string.data(using: .utf8) ?? Data()).base64EncodedString()
        }
        return NoteRow(
            id:            id.uuidString,
            user_id:       userID,
            title:         title,
            content_html:  htmlString,
            folder_id:     folderID?.uuidString,
            created_date:  createdDate,
            modified_date: modifiedDate,
            updated_at:    Date()
        )
    }"""

new = """    func toRow(userID: String) -> NoteRow {
        // Encode NSAttributedString as HTML \u2014 works on both macOS and iOS.
        let htmlString: String
        if let htmlData = try? content.data(
            from: NSRange(location: 0, length: content.length),
            documentAttributes: [.documentType: NSAttributedString.DocumentType.html]
        ), let str = String(data: htmlData, encoding: .utf8) {
            htmlString = str
        } else {
            htmlString = content.string
        }
        return NoteRow(
            id:            id.uuidString,
            user_id:       userID,
            title:         title,
            content_html:  htmlString,
            folder_id:     folderID?.uuidString,
            created_date:  createdDate,
            modified_date: modifiedDate,
            updated_at:    Date()
        )
    }"""

if old in src:
    src = src.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(src)
    print("OK: toRow() fixed")
else:
    print("FAIL: old pattern not found — printing current toRow block:")
    import re
    m = re.search(r'func toRow\(userID.*?\n    \}', src, re.DOTALL)
    if m:
        print(m.group(0))
    else:
        print("toRow not found at all")
