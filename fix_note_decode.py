"""
Line-based replacement of Note.init(from:) to use HTML instead of RTF.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Models/Note.swift"
with open(path) as f:
    lines = f.readlines()

# Find init(from decoder: Decoder) throws {
start = None
for i, line in enumerate(lines):
    if "init(from decoder: Decoder) throws {" in line:
        start = i
        break

if start is None:
    print("FAIL: could not find init(from decoder:)")
    exit(1)

# Find closing brace
depth = 0
end = None
for i in range(start, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if depth == 0 and i > start:
        end = i
        break

print(f"Found init(from:) at lines {start+1}-{end+1}")

new_init = """    init(from decoder: Decoder) throws {
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
        } else if let rtfData = try? container.decodeIfPresent(Data.self, forKey: .contentData),
                  let data = rtfData,
                  let attr = try? NSAttributedString(
                      data: data,
                      options: [.documentType: NSAttributedString.DocumentType.rtf],
                      documentAttributes: nil) {
            // Legacy RTF cache — will be re-saved as HTML on next write
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
    }
"""

lines[start:end+1] = [new_init]
with open(path, "w") as f:
    f.writelines(lines)

# Verify
with open(path) as f:
    result = f.read()

ok1 = "decodeIfPresent(String.self, forKey: .contentHTML)" in result
ok2 = "decodeIfPresent(Data.self, forKey: .contentData)" in result
ok3 = "forKey: .contentHTML" in result and "forKey: .contentData" in result
print(("OK" if ok1 else "FAIL") + ": init(from:) reads contentHTML first")
print(("OK" if ok2 else "FAIL") + ": init(from:) falls back to contentData (RTF)")
print(("OK" if ok3 else "FAIL") + ": both keys referenced")
