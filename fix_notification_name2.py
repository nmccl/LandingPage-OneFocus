path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/OneFocusApp.swift"

with open(path, 'r') as f:
    content = f.read()

old = "            NotificationCenter.default.post(name: .noteEditorShouldFlush, object: nil)"
new = "            NotificationCenter.default.post(name: Notification.Name(\"noteEditorShouldFlush\"), object: nil)"

count = content.count(old)
if count > 0:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print(f"SUCCESS: Fixed {count} occurrence(s)")
else:
    idx = content.find(".noteEditorShouldFlush")
    if idx != -1:
        print(f"Found at index {idx}, context:")
        print(repr(content[idx-80:idx+80]))
    else:
        print("Not found")
