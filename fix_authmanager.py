import re

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/iOSOnboardingView.swift"
with open(path) as f:
    content = f.read()

# Add authManager EnvironmentObject to iOSPaywallPage using regex
match = re.search(
    r'(@EnvironmentObject private var proAccess[^\n]+\n\s*@EnvironmentObject private var storeKit[^\n]+\n\s*let onComplete)',
    content
)
if match:
    old2 = match.group(0)
    new2 = old2.replace("let onComplete", "@EnvironmentObject private var authManager: AuthManager\n    let onComplete")
    content = content.replace(old2, new2, 1)
    print("Added authManager to iOSPaywallPage")
else:
    print("ERROR: Could not find the block")

# Remove .environmentObject(authManager) from the sheet — iOSSignInView gets it from the environment chain
content = re.sub(
    r'(\.sheet\(isPresented: \$showingSignIn\) \{\s*iOSSignInView\(\)\s*)\.environmentObject\(authManager\)\s*(\})',
    r'\1\2',
    content
)
print("Cleaned up sheet modifier")

with open(path, 'w') as f:
    f.write(content)
print("Done")
