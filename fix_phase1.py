#!/usr/bin/env python3
"""
Phase 1 fixes:
1. Replace fatalError in TasksView binding(for:) with a graceful no-op
2. Add configure(userID:) and clearEvents() call in AuthManager sign-out
   so analytics are user-scoped and cleared on sign-out
"""
import re

# ── Fix 1: fatalError in TasksView ──────────────────────────────────────────
tv_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/TasksView.swift"
with open(tv_path, "r") as f:
    tv = f.read()

old_binding = '''    private func binding(for task: Task) -> Binding<Task> {
        guard let index = tasksViewModel.tasks.firstIndex(where: { $0.id == task.id }) else {
            fatalError("Task not found")
        }
        return $tasksViewModel.tasks[index]
    }'''

new_binding = '''    private func binding(for task: Task) -> Binding<Task> {
        // Return a safe fallback binding if the task is no longer in the array
        // (e.g. deleted while the row is still animating out).
        if let index = tasksViewModel.tasks.firstIndex(where: { $0.id == task.id }) {
            return $tasksViewModel.tasks[index]
        }
        // Provide a read-only snapshot so the view degrades gracefully instead of crashing.
        var snapshot = task
        return Binding(
            get: { snapshot },
            set: { snapshot = $0 }
        )
    }'''

if old_binding in tv:
    tv = tv.replace(old_binding, new_binding)
    with open(tv_path, "w") as f:
        f.write(tv)
    print("✅ Fix 1: fatalError in TasksView replaced with graceful fallback")
else:
    print("⚠️  Fix 1: fatalError pattern not found — may already be fixed")

# ── Fix 2: AnalyticsService — add configure(userID:) and user-scoped key ────
analytics_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/AnalyticsService.swift"
with open(analytics_path, "r") as f:
    analytics = f.read()

# Replace the hardcoded UserDefaults.standard key with a user-scoped key
old_save = '''    private func saveEvent(_ event: AnalyticsEvent) {
        // Persist all events to UserDefaults (capped at 1 000 to avoid bloat)
        let capped = Array(events.suffix(1_000))
        if let data = try? JSONEncoder().encode(capped) {
            UserDefaults.standard.set(data, forKey: "analytics.events")
        }
    }
    private func loadEvents() {
        if let data   = UserDefaults.standard.data(forKey: "analytics.events"),
           let loaded = try? JSONDecoder().decode([AnalyticsEvent].self, from: data) {
            events = loaded
        }
    }
    func clearEvents() {
        events.removeAll()
    }'''

new_save = '''    // MARK: - Configuration
    /// Scopes analytics storage to the signed-in user.
    /// Call after sign-in and on sign-out (pass nil to clear).
    func configure(userID: String?) {
        self.userID = userID
        if userID != nil {
            loadEvents()
        } else {
            events.removeAll()
        }
    }
    private func saveEvent(_ event: AnalyticsEvent) {
        // Persist all events to UserDefaults under a user-scoped key (capped at 1 000)
        let capped = Array(events.suffix(1_000))
        if let data = try? JSONEncoder().encode(capped) {
            UserDefaults.standard.set(data, forKey: storageKey)
        }
    }
    private func loadEvents() {
        if let data   = UserDefaults.standard.data(forKey: storageKey),
           let loaded = try? JSONDecoder().decode([AnalyticsEvent].self, from: data) {
            events = loaded
        }
    }
    func clearEvents() {
        events.removeAll()
        UserDefaults.standard.removeObject(forKey: storageKey)
    }'''

# Add userID property and storageKey after the `@Published var events` line
old_props = '''    // MARK: - Published Properties
    @Published var events: [AnalyticsEvent] = []
    // MARK: - Private Properties
    private let persistenceService = PersistenceService.shared
    // MARK: - Initializer
    private init() {
        loadEvents()
    }'''

new_props = '''    // MARK: - Published Properties
    @Published var events: [AnalyticsEvent] = []
    // MARK: - Private Properties
    private let persistenceService = PersistenceService.shared
    /// Current signed-in user ID — used to scope the analytics storage key.
    private var userID: String?
    private var storageKey: String {
        userID.map { "u_\($0)_analytics.events" } ?? "analytics.events"
    }
    // MARK: - Initializer
    private init() {
        // Events are loaded lazily via configure(userID:) after sign-in.
        // This prevents cross-account data bleed on shared devices.
    }'''

changed = False
if old_props in analytics:
    analytics = analytics.replace(old_props, new_props)
    changed = True
    print("✅ Fix 2a: AnalyticsService userID + storageKey added")
else:
    print("⚠️  Fix 2a: AnalyticsService props pattern not found")

if old_save in analytics:
    analytics = analytics.replace(old_save, new_save)
    changed = True
    print("✅ Fix 2b: AnalyticsService save/load/clear updated to user-scoped key")
else:
    print("⚠️  Fix 2b: AnalyticsService save pattern not found")

if changed:
    with open(analytics_path, "w") as f:
        f.write(analytics)

# ── Fix 3: AuthManager — call AnalyticsService.shared.configure on sign-in/out ──
auth_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/AuthManager.swift"
with open(auth_path, "r") as f:
    auth = f.read()

# Wire configure(userID:) into signOut
old_signout_body = '''            // Delete device-local user data BEFORE clearing currentUser
            if let uid = self.currentUser?.id.uuidString {
                PersistenceService.deleteAllData(forUserID: uid)
            }
            try? await supabase.auth.signOut()
            self.clearLocalAuthState()'''

new_signout_body = '''            // Delete device-local user data BEFORE clearing currentUser
            if let uid = self.currentUser?.id.uuidString {
                PersistenceService.deleteAllData(forUserID: uid)
            }
            try? await supabase.auth.signOut()
            await MainActor.run { AnalyticsService.shared.configure(userID: nil) }
            self.clearLocalAuthState()'''

if old_signout_body in auth:
    auth = auth.replace(old_signout_body, new_signout_body)
    print("✅ Fix 3a: AnalyticsService.configure(nil) wired into signOut")
else:
    print("⚠️  Fix 3a: signOut body pattern not found")

# Wire configure(userID:) into finishSignIn
old_finish = '''    private func finishSignIn(user: User) async {'''
new_finish = '''    private func finishSignIn(user: User) async {
        AnalyticsService.shared.configure(userID: user.id.uuidString)'''

if old_finish in auth and "AnalyticsService.shared.configure" not in auth:
    auth = auth.replace(old_finish, new_finish, 1)
    print("✅ Fix 3b: AnalyticsService.configure(userID:) wired into finishSignIn")
else:
    print("⚠️  Fix 3b: finishSignIn pattern not found or already patched")

with open(auth_path, "w") as f:
    f.write(auth)

print("\nPhase 1 complete.")
