#!/usr/bin/env python3
"""Fix AnalyticsService: user-scoped storage key + configure(userID:) method"""

analytics_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Services/AnalyticsService.swift"
with open(analytics_path, "r") as f:
    src = f.read()

# 1. Add userID property and storageKey after persistenceService declaration
old_props = """    // MARK: - Private Properties
    private let persistenceService = PersistenceService.shared
    // MARK: - Initializer
    private init() {
        loadEvents()
    }"""

new_props = """    // MARK: - Private Properties
    private let persistenceService = PersistenceService.shared
    /// Current signed-in user ID — scopes the analytics storage key.
    private var userID: String?
    private var storageKey: String {
        userID.map { "u_\\($0)_analytics.events" } ?? "analytics.events"
    }
    // MARK: - Initializer
    private init() {
        // Events loaded lazily via configure(userID:) after sign-in.
    }
    // MARK: - Configuration
    /// Scopes analytics storage to the signed-in user.
    /// Pass nil on sign-out to clear in-memory events.
    func configure(userID: String?) {
        self.userID = userID
        if userID != nil {
            loadEvents()
        } else {
            events.removeAll()
        }
    }"""

if old_props in src:
    src = src.replace(old_props, new_props)
    print("✅ Added userID, storageKey, configure(userID:)")
else:
    print("⚠️  Props block not found")

# 2. Replace save/load/clearEvents to use storageKey
old_data = """    // MARK: - Data Management
    private func saveEvent(_ event: AnalyticsEvent) {
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
    }"""

new_data = """    // MARK: - Data Management
    private func saveEvent(_ event: AnalyticsEvent) {
        // Persist all events under the user-scoped key (capped at 1 000 to avoid bloat)
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
    }"""

if old_data in src:
    src = src.replace(old_data, new_data)
    print("✅ save/load/clearEvents updated to user-scoped storageKey")
else:
    print("⚠️  Data management block not found")

with open(analytics_path, "w") as f:
    f.write(src)

# 3. Wire configure(userID:) into AuthManager finishSignIn
auth_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/AuthManager.swift"
with open(auth_path, "r") as f:
    auth = f.read()

old_finish = "    private func finishSignIn(user: User) async {"
new_finish = """    private func finishSignIn(user: User) async {
        await MainActor.run { AnalyticsService.shared.configure(userID: user.id.uuidString) }"""

if old_finish in auth and "AnalyticsService.shared.configure(userID:" not in auth:
    auth = auth.replace(old_finish, new_finish, 1)
    with open(auth_path, "w") as f:
        f.write(auth)
    print("✅ AnalyticsService.configure(userID:) wired into finishSignIn")
else:
    print("⚠️  finishSignIn not found or already patched")

print("\nAnalytics fix complete.")
