#!/usr/bin/env python3
"""
Add a User-Agent header to EmailUpdateService.swift.
Resend's API is fronted by Cloudflare which blocks requests without a User-Agent
(returns 403 error code 1010). URLSession on Apple platforms doesn't add one by
default, so we set it explicitly.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/EmailUpdateService.swift"

with open(path, "r") as f:
    content = f.read()

# Insert the User-Agent header right after the Content-Type header line
old = '        request.setValue("application/json", forHTTPHeaderField: "Content-Type")'
new = ('        request.setValue("application/json",  forHTTPHeaderField: "Content-Type")\n'
       '        // Resend\'s API is fronted by Cloudflare, which blocks requests without a\n'
       '        // User-Agent header (returns 403 error code 1010). URLSession on Apple\n'
       '        // platforms doesn\'t add one by default, so we set it explicitly.\n'
       '        request.setValue("OneFocus/1.0 (Apple)", forHTTPHeaderField: "User-Agent")')

if old in content:
    content = content.replace(old, new, 1)
    print("User-Agent header added successfully")
else:
    print("Anchor not found — trying alternate whitespace...")
    # Try with double space (already in new version)
    old2 = '        request.setValue("application/json",  forHTTPHeaderField: "Content-Type")'
    if old2 in content:
        print("File already has the fix applied (double-space variant found)")
    else:
        # Show the actual line for debugging
        for i, line in enumerate(content.splitlines(), 1):
            if 'Content-Type' in line and 'setValue' in line:
                print(f"  Line {i}: {repr(line)}")

# Also improve error logging while we're here
old_log = ('            let (_, response) = try await URLSession.shared.data(for: request)\n'
           '            if let http = response as? HTTPURLResponse {\n'
           '                print("EmailUpdateService: upsert status \\(http.statusCode) for \\(email)")\n'
           '            }')
new_log = ('            let (responseData, response) = try await URLSession.shared.data(for: request)\n'
           '            if let http = response as? HTTPURLResponse {\n'
           '                print("EmailUpdateService: upsert status \\(http.statusCode) for \\(email)")\n'
           '                if http.statusCode >= 400,\n'
           '                   let body = String(data: responseData, encoding: .utf8) {\n'
           '                    print("EmailUpdateService: error body — \\(body)")\n'
           '                }\n'
           '            }')
if old_log in content:
    content = content.replace(old_log, new_log, 1)
    print("Error logging improved")

with open(path, "w") as f:
    f.write(content)
print("Done")
