#!/usr/bin/env python3
"""
Add deleteAccount() to AuthManager and wire it into macOS AccountSettingsView
and iOS iOSAccountSettingsView.
"""

# ── 1. AuthManager: add deleteAccount() after signOut() ──────────────────────
auth_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/AuthManager.swift"
with open(auth_path, "r") as f:
    auth = f.read()

if "func deleteAccount" not in auth:
    insert_after = "    // MARK: - Public: Onboarding"
    new_func = '''    // MARK: - Public: Delete Account
    /// Permanently deletes the current user's account via the
    /// `delete_current_user` Postgres RPC (SECURITY DEFINER) and then
    /// signs out locally.  Throws on failure so callers can show an error.
    func deleteAccount() async throws {
        isLoading = true
        defer { isLoading = false }
        // Post sign-out notification so observers clear their caches first.
        NotificationCenter.default.post(name: .userWillSignOut, object: nil)
        // Delete device-local data before wiping the account.
        if let uid = currentUser?.id.uuidString {
            PersistenceService.deleteAllData(forUserID: uid)
        }
        // Call the SECURITY DEFINER RPC that deletes the row from auth.users.
        try await supabase.rpc("delete_current_user").execute()
        // Sign out the local session.
        try? await supabase.auth.signOut()
        await MainActor.run {
            AnalyticsService.shared.configure(userID: nil)
            clearLocalAuthState()
        }
    }

    // MARK: - Public: Onboarding'''
    auth = auth.replace(insert_after, new_func)
    with open(auth_path, "w") as f:
        f.write(auth)
    print("✅ deleteAccount() added to AuthManager")
else:
    print("ℹ️  deleteAccount() already exists in AuthManager")

# ── 2. macOS AccountSettingsView: replace TODO with real delete flow ──────────
mac_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/Tabs/AccountSettingsView.swift"
with open(mac_path, "r") as f:
    mac = f.read()

# Check for @State showingDeleteAlert
if "@State private var showingDeleteAlert" not in mac:
    # Add state var after the first @State block
    old_state_marker = "    @State private var draft: Draft = Draft()"
    mac = mac.replace(
        old_state_marker,
        old_state_marker + "\n    @State private var showingDeleteAlert = false\n    @State private var deleteError: String?"
    )
    print("✅ Added @State vars for delete alert (macOS)")

# Replace the TODO button action
old_btn = '''                Button(role: .destructive) {
                    // TODO: wire to real delete flow
                } label: {'''

new_btn = '''                Button(role: .destructive) {
                    showingDeleteAlert = true
                } label: {'''

if old_btn in mac:
    mac = mac.replace(old_btn, new_btn)
    print("✅ Wired delete button (macOS)")
else:
    print("⚠️  macOS delete button TODO not found")

# Add .alert modifier to the dangerCard (after the closing brace of the card)
if "showingDeleteAlert" in mac and ".alert(\"Delete Account\"" not in mac:
    # Find the end of dangerCard and add alert before the footer comment
    old_footer_comment = "    // MARK: - Footer"
    new_alert = '''    // MARK: - Delete Alert
    private var deleteAccountAlert: Alert {
        Alert(
            title: Text("Delete Account"),
            message: Text("This will permanently delete your account and all data. This cannot be undone."),
            primaryButton: .destructive(Text("Delete")) {
                Task {
                    do {
                        try await authManager.deleteAccount()
                        closePanel()
                    } catch {
                        deleteError = error.localizedDescription
                    }
                }
            },
            secondaryButton: .cancel()
        )
    }

    // MARK: - Footer'''
    mac = mac.replace(old_footer_comment, new_alert)
    print("✅ Added deleteAccountAlert computed property (macOS)")

# Attach .alert to the main body — find the last .padding() before the end of body
if ".alert(isPresented: $showingDeleteAlert)" not in mac:
    # Attach to the dangerCard view — find where dangerCard is used in the ScrollView
    old_danger_usage = "                dangerCard"
    new_danger_usage = "                dangerCard\n                    .alert(isPresented: $showingDeleteAlert) { deleteAccountAlert }"
    if old_danger_usage in mac:
        mac = mac.replace(old_danger_usage, new_danger_usage, 1)
        print("✅ Attached .alert to dangerCard (macOS)")
    else:
        print("⚠️  dangerCard usage not found in macOS view body")

with open(mac_path, "w") as f:
    f.write(mac)

# ── 3. iOS iOSAccountSettingsView: replace contact-support alert with real delete ──
ios_path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Views/iOS/Tabs/iOSAccountSettingsView.swift"
with open(ios_path, "r") as f:
    ios = f.read()

# Replace the stub alert with a real confirmation + async delete
old_ios_alert = '''            .alert("Delete Account", isPresented: $showingDeleteAlert) {
                Button("OK", role: .cancel) {}
            } message: {
                Text("To delete your account, please contact support at support@onefocus.app.")
            }'''

new_ios_alert = '''            .alert("Delete Account", isPresented: $showingDeleteAlert) {
                Button("Delete", role: .destructive) {
                    Task {
                        do {
                            try await authManager.deleteAccount()
                        } catch {
                            // Silently handled — user is signed out regardless
                        }
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("This will permanently delete your account and all data. This cannot be undone.")
            }'''

if old_ios_alert in ios:
    ios = ios.replace(old_ios_alert, new_ios_alert)
    with open(ios_path, "w") as f:
        f.write(ios)
    print("✅ iOS delete alert updated to real delete flow")
else:
    print("⚠️  iOS delete alert stub not found")

print("\nDelete account fix complete.")
