path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/OneFocusApp.swift"

with open(path, 'r') as f:
    content = f.read()

# The issue: the code uses .noteEditorShouldFlush as shorthand, which resolves
# to NSNotification.Name on macOS but fails on iOS because the extension is on
# Notification.Name. Use the explicit Notification.Name(...) form which works
# on both platforms without needing the dot-shorthand type inference.

old = "                        name: .noteEditorShouldFlush, object: nil)"
new = "                        name: Notification.Name(\"noteEditorShouldFlush\"), object: nil)"

count = content.count(old)
if count > 0:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print(f"SUCCESS: Fixed {count} occurrence(s) of noteEditorShouldFlush in OneFocusApp.swift")
else:
    # Try to find the actual usage for debugging
    idx = content.find("noteEditorShouldFlush")
    if idx != -1:
        print(f"Found at index {idx}, context:")
        print(repr(content[idx-60:idx+80]))
    else:
        print("noteEditorShouldFlush not found in OneFocusApp.swift")
