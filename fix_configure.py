path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/ProAccessManager.swift"
with open(path, 'r') as f:
    content = f.read()

# Remove the misplaced block that was inserted outside the function
bad = (
    '    }\n'
    '        // Always evaluate immediately so a subscription active on another device\n'
    '        // is reflected as soon as the user signs in, without waiting for the next\n'
    '        // hasActiveSubscription publisher emission.\n'
    '        AsyncTask { await self.evaluateProStatus() }\n'
    '    // MARK: - Pro Status Evaluation'
)
good = (
    '        // Always evaluate immediately so a subscription active on another device\n'
    '        // is reflected as soon as the user signs in, without waiting for the next\n'
    '        // hasActiveSubscription publisher emission.\n'
    '        AsyncTask { await self.evaluateProStatus() }\n'
    '    }\n'
    '    // MARK: - Pro Status Evaluation'
)

assert bad in content, "Bad block not found — check manually"
content = content.replace(bad, good, 1)

with open(path, 'w') as f:
    f.write(content)
print("done")
