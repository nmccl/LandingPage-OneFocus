"""
Add .task { checkTrialEligibility } to macOS PaywallPage in OnboardingView.swift
"""
import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Auth/OnboardingView.swift"

with open(path) as f:
    content = f.read()

if "checkTrialEligibility" in content:
    print("Already applied.")
    sys.exit(0)

old = (
    "        .onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n"
    "        }\n"
    "    }\n\n"
    "    // MARK: - Plan Column"
)
new = (
    "        .onAppear {\n"
    "            withAnimation(.easeOut(duration: 0.4).delay(0.05)) { appeared = true }\n"
    "        }\n"
    "        .task {\n"
    "            isEligibleForTrial = await storeKit.checkTrialEligibility()\n"
    "        }\n"
    "    }\n\n"
    "    // MARK: - Plan Column"
)

if old not in content:
    print("ERROR: anchor not found")
    idx = content.find("// MARK: - Plan Column")
    print(repr(content[idx-200:idx+50]))
    sys.exit(1)

content = content.replace(old, new, 1)
with open(path, "w") as f:
    f.write(content)
print("Done. .task added to macOS PaywallPage.")
