#!/usr/bin/env python3
"""
Remove the soundEnabled computed-property shim from TimeBehaviorCompat.swift
now that soundEnabled is a real @Published stored property on UserSettings.
"""

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Helpers/TimeBehaviorCompat.swift"

with open(path) as f:
    src = f.read()

# Remove the soundEnabled shim block (comment + computed property)
old = '''    // soundEnabled is not yet a persisted setting in UserSettings.
    // This shim lets SettingsWorkingCopy read/write it without a full migration.
    var soundEnabled: Bool {
        get { (UserDefaults.standard.object(forKey: "soundEnabled") as? Bool) ?? true }
        set { UserDefaults.standard.set(newValue, forKey: "soundEnabled") }
    }'''

if old in src:
    new_src = src.replace(old, '', 1)
    with open(path, 'w') as f:
        f.write(new_src)
    print("✅ Removed soundEnabled shim from TimeBehaviorCompat.swift")
else:
    # Try a looser match — find the block by key lines
    lines = src.split('\n')
    start = None
    end = None
    for i, line in enumerate(lines):
        if 'soundEnabled is not yet a persisted' in line:
            start = i
        if start is not None and line.strip() == '}' and i > start + 2:
            end = i
            break
    if start is not None and end is not None:
        del lines[start:end+1]
        # Remove any trailing blank line left behind
        if start < len(lines) and lines[start].strip() == '':
            del lines[start]
        with open(path, 'w') as f:
            f.write('\n'.join(lines))
        print("✅ Removed soundEnabled shim (loose match) from TimeBehaviorCompat.swift")
    else:
        print("⚠️  Could not find soundEnabled shim — printing file:")
        print(src)
