path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/OneFocusApp.swift"

with open(path, 'r') as f:
    content = f.read()

old = """            .onChange(of: scenePhase) { newPhase in
                if newPhase == .background {
                    NotificationCenter.default.post(
                        name: NSNotification.Name("AppDidEnterBackground"), object: nil)
                }
                if newPhase == .background || newPhase == .inactive {
                    NotificationCenter.default.post(
                        name: .noteEditorShouldFlush, object: nil)
                    // NotesStore is @MainActor and onChange fires on the main
                    // thread, so we can call save() directly without a Task.
                    MainActor.assumeIsolated {
                        NotesStore.shared.save()
                    }
                }
            }"""

new = """            .onChange(of: scenePhase) {
                if scenePhase == .background {
                    NotificationCenter.default.post(
                        name: NSNotification.Name("AppDidEnterBackground"), object: nil)
                }
                if scenePhase == .background || scenePhase == .inactive {
                    NotificationCenter.default.post(
                        name: .noteEditorShouldFlush, object: nil)
                    // NotesStore is @MainActor and onChange fires on the main
                    // thread, so we can call save() directly without a Task.
                    MainActor.assumeIsolated {
                        NotesStore.shared.save()
                    }
                }
            }"""

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    print("SUCCESS: onChange(of: scenePhase) closure fixed")
else:
    # Try to find the actual text for debugging
    idx = content.find(".onChange(of: scenePhase)")
    if idx != -1:
        print(f"Found onChange at index {idx}, context:")
        print(repr(content[idx:idx+400]))
    else:
        print("onChange(of: scenePhase) not found")
