"""
Fix Note.swift: replace RTF-based Codable encode/decode with HTML.

The local UserDefaults cache uses Note's Codable conformance.
encode(to:) was saving content as RTF Data — this fails silently on iOS,
producing empty data. On next load, the note appears blank.

Fix: store content as an HTML string in the cache (same format as Supabase).
This makes the cache consistent with Supabase and works on both platforms.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Models/Note.swift"
with open(path) as f:
    src = f.read()

# Fix 1: CodingKeys — rename contentData -> contentHTML
old_keys = """    enum CodingKeys: String, CodingKey {
        case id, title, contentData, createdDate, modifiedDate, folderID
    }"""
new_keys = """    enum CodingKeys: String, CodingKey {
        case id, title, contentHTML, contentData, createdDate, modifiedDate, folderID
    }"""
src = src.replace(old_keys, new_keys, 1)

# Fix 2: init(from:) — read contentHTML first, fall back to contentData for migration
old_decode = """    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id    = try container.decode(UUID.self,   forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        let contentData   = try container.decode(Data.self, forKey: .contentData)
        let loadedContent = (try? NSAttributedString(
            data: contentData,
            options: [.documentType: NSAttributedString.DocumentType.rtf],
            documentAttributes: nil
        )) ?? NSAttributedString(string: "")
        // Ensure text colour adapts to dark/light mode
        #if os(macOS)
        let mutableContent = NSMutableAttributedString(attributedString: loadedContent)
        let range = NSRange(location: 0, length: mutableContent.length)
        mutableContent.addAttribute(.foregroundColor, value: NSColor.textColor, range: range)
        content = mutableContent
        #else
        content = loadedContent
        #endif
        createdDate  = try container.decode(Date.self, forKey: .createdDate)
        modifiedDate = try container.decode(Date.self, forKey: .modifiedDate)
        // Safe: existing notes without this key decode as nil
        folderID     = try container.decodeIfPresent(UUID.self, forKey: .folderID)
    }"""
new_decode = """    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id    = try container.decode(UUID.self,   forKey: .id)
        title = try container.decode(String.self, forKey: .title)

        // Prefer HTML (new format). Fall back to RTF Data for migration of old caches.
        var loadedContent: NSAttributedString = NSAttributedString(string: "")
        if let htmlString = try? container.decodeIfPresent(String.self, forKey: .contentHTML),
           let html = htmlString,
           !html.isEmpty,
           let data = html.data(using: .utf8),
           let attr = try? NSAttributedString(
               data: data,
               options: [.documentType: NSAttributedString.DocumentType.html,
                         .characterEncoding: String.Encoding.utf8.rawValue],
               documentAttributes: nil) {
            loadedContent = attr
        } else if let contentData = try? container.decodeIfPresent(Data.self, forKey: .contentData),
                  let data = contentData,
                  let attr = try? NSAttributedString(
                      data: data,
                      options: [.documentType: NSAttributedString.DocumentType.rtf],
                      documentAttributes: nil) {
            // Legacy RTF cache — migrate on next save
            loadedContent = attr
        }

        // Ensure text colour adapts to dark/light mode
        #if os(macOS)
        let mutableContent = NSMutableAttributedString(attributedString: loadedContent)
        let range = NSRange(location: 0, length: mutableContent.length)
        mutableContent.addAttribute(.foregroundColor, value: NSColor.textColor, range: range)
        content = mutableContent
        #else
        content = loadedContent
        #endif
        createdDate  = try container.decode(Date.self, forKey: .createdDate)
        modifiedDate = try container.decode(Date.self, forKey: .modifiedDate)
        // Safe: existing notes without this key decode as nil
        folderID     = try container.decodeIfPresent(UUID.self, forKey: .folderID)
    }"""
src = src.replace(old_decode, new_decode, 1)

# Fix 3: encode(to:) — save as HTML string instead of RTF Data
old_encode = """    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id,    forKey: .id)
        try container.encode(title, forKey: .title)
        let contentData = try content.data(
            from: NSRange(location: 0, length: content.length),
            documentAttributes: [.documentType: NSAttributedString.DocumentType.rtf]
        )
        try container.encode(contentData,  forKey: .contentData)
        try container.encode(createdDate,  forKey: .createdDate)
        try container.encode(modifiedDate, forKey: .modifiedDate)
        try container.encodeIfPresent(folderID, forKey: .folderID)
    }"""
new_encode = """    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id,    forKey: .id)
        try container.encode(title, forKey: .title)
        // Store content as HTML — works on both macOS and iOS.
        // RTF encoding is macOS-only and fails silently on iOS.
        let htmlString: String
        if let htmlData = try? content.data(
            from: NSRange(location: 0, length: content.length),
            documentAttributes: [.documentType: NSAttributedString.DocumentType.html]
        ), let str = String(data: htmlData, encoding: .utf8) {
            htmlString = str
        } else {
            htmlString = content.string
        }
        try container.encode(htmlString,   forKey: .contentHTML)
        try container.encode(createdDate,  forKey: .createdDate)
        try container.encode(modifiedDate, forKey: .modifiedDate)
        try container.encodeIfPresent(folderID, forKey: .folderID)
    }"""
src = src.replace(old_encode, new_encode, 1)

with open(path, "w") as f:
    f.write(src)

# Verify
ok1 = "contentHTML" in src and "contentData" in src  # both keys present (migration)
ok2 = "NSAttributedString.DocumentType.html" in src and "NSAttributedString.DocumentType.rtf" in src
ok3 = 'forKey: .contentHTML' in src
print(("OK" if ok1 else "FAIL") + ": CodingKeys has both contentHTML and contentData")
print(("OK" if ok2 else "FAIL") + ": both HTML and RTF referenced (HTML primary, RTF fallback)")
print(("OK" if ok3 else "FAIL") + ": encode() saves to contentHTML")
