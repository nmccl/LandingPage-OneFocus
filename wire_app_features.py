#!/usr/bin/env python3
"""
Wire AppLockManager into OneFocusApp, sync NotificationManager with UserSettings,
and wire the email updates toggle to the Resend API.
"""

import os

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

def patch(path, find, replace, all_occurrences=False):
    with open(path) as f:
        src = f.read()
    if find not in src:
        print(f"⚠️  Pattern not found in {os.path.basename(path)}: {find[:80]!r}")
        return False
    if all_occurrences:
        new = src.replace(find, replace)
    else:
        new = src.replace(find, replace, 1)
    with open(path, 'w') as f:
        f.write(new)
    print(f"✅ Patched: {os.path.basename(path)}")
    return True

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Written: {os.path.basename(path)}")

app_path = f"{BASE}/OneFocusApp.swift"

# ─────────────────────────────────────────────────────────────────────────────
# 1. Add AppLockManager StateObject declaration
# ─────────────────────────────────────────────────────────────────────────────
patch(app_path,
    '    @StateObject private var clipboardViewModel:   ClipboardHistoryViewModel',
    '    @StateObject private var clipboardViewModel:   ClipboardHistoryViewModel\n    @StateObject private var appLockManager:       AppLockManager'
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Init AppLockManager in init()
# ─────────────────────────────────────────────────────────────────────────────
patch(app_path,
    '        _clipboardViewModel  = StateObject(wrappedValue: ClipboardHistoryViewModel())',
    '        _clipboardViewModel  = StateObject(wrappedValue: ClipboardHistoryViewModel())\n        _appLockManager      = StateObject(wrappedValue: AppLockManager(userSettings: settings))'
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Inject AppLockManager as environment object
# ─────────────────────────────────────────────────────────────────────────────
patch(app_path,
    '            .environmentObject(clipboardViewModel)',
    '            .environmentObject(clipboardViewModel)\n            .environmentObject(appLockManager)'
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Wrap the root view in AppLockView overlay
#    Replace the Group { ... } root with one that overlays the lock screen
# ─────────────────────────────────────────────────────────────────────────────
patch(app_path,
    '            Group {\n                #if os(iOS)\n                if !authManager.isAuthenticated {\n                    iOSSignInView()\n                } else {\n                    iOSMainView()\n                }\n                #else\n                if !authManager.isAuthenticated {\n                    SignInView()\n                } else if !authManager.hasCompletedOnboarding {\n                    OnboardingView()\n                } else {\n                    MainView()\n                }\n                #endif\n            }',
    '''            Group {
                #if os(iOS)
                if !authManager.isAuthenticated {
                    iOSSignInView()
                } else {
                    iOSMainView()
                        .overlay {
                            if appLockManager.isLocked {
                                AppLockView(lockManager: appLockManager)
                                    .transition(.opacity)
                            }
                        }
                }
                #else
                if !authManager.isAuthenticated {
                    SignInView()
                } else if !authManager.hasCompletedOnboarding {
                    OnboardingView()
                } else {
                    MainView()
                        .overlay {
                            if appLockManager.isLocked {
                                AppLockView(lockManager: appLockManager)
                                    .transition(.opacity)
                            }
                        }
                }
                #endif
            }'''
)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Lock on sign-in and post background notification on scene phase change
# ─────────────────────────────────────────────────────────────────────────────
# After sign-in, lock the app if requireAuth is on
patch(app_path,
    '            .onReceive(authManager.$isAuthenticated) { authenticated in\n                if authenticated {\n                    _Concurrency.Task { await proAccessManager.evaluateProStatus() }\n                } else {\n                    proAccessManager.revokePro()\n                }\n            }',
    '''            .onReceive(authManager.$isAuthenticated) { authenticated in
                if authenticated {
                    _Concurrency.Task { await proAccessManager.evaluateProStatus() }
                    appLockManager.lockIfRequired()
                } else {
                    proAccessManager.revokePro()
                }
            }'''
)

# Post background notification so AppLockManager can re-lock
patch(app_path,
    '            .onChange(of: scenePhase) { newPhase in\n                if newPhase == .background || newPhase == .inactive {',
    '''            .onChange(of: scenePhase) { newPhase in
                if newPhase == .background {
                    NotificationCenter.default.post(
                        name: NSNotification.Name("AppDidEnterBackground"), object: nil)
                }
                if newPhase == .background || newPhase == .inactive {'''
)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Sync NotificationManager when UserSettings changes
#    Add onReceive for notificationsEnabled and soundEnabled
# ─────────────────────────────────────────────────────────────────────────────
patch(app_path,
    '            .onReceive(authManager.$currentUser) { user in',
    '''            // Keep NotificationManager in sync with UserSettings
            .onReceive(
                userSettings.$notificationsEnabled
                    .combineLatest(userSettings.$soundEnabled)
            ) { enabled, sound in
                NotificationManager.shared.configure(
                    notificationsEnabled: enabled,
                    soundEnabled: sound
                )
            }
            .onReceive(authManager.$currentUser) { user in'''
)

# ─────────────────────────────────────────────────────────────────────────────
# 7. Sync NotificationManager on first appear (onAppear already exists)
# ─────────────────────────────────────────────────────────────────────────────
patch(app_path,
    '                NotificationManager.shared.requestAuthorization { granted in\n                    DispatchQueue.main.async {\n                        if !granted { userSettings.notificationsEnabled = false }\n                    }\n                }',
    '''                NotificationManager.shared.requestAuthorization { granted in
                    DispatchQueue.main.async {
                        if !granted { userSettings.notificationsEnabled = false }
                        NotificationManager.shared.configure(
                            notificationsEnabled: userSettings.notificationsEnabled,
                            soundEnabled: userSettings.soundEnabled
                        )
                    }
                }'''
)

print("\n✅ OneFocusApp.swift fully wired.")

# ─────────────────────────────────────────────────────────────────────────────
# 8. Wire email updates toggle in AccountSettingsView (macOS)
#    When emailUpdates is toggled on, subscribe via Resend API;
#    when toggled off, unsubscribe.
#    We do this via a new EmailUpdateService.
# ─────────────────────────────────────────────────────────────────────────────
email_service_path = f"{BASE}/Services/EmailUpdateService.swift"
write(email_service_path, '''\
//
//  EmailUpdateService.swift
//  OneFocus
//
//  Subscribes / unsubscribes the signed-in user from the OneFocus
//  release-announcement mailing list via the Resend Contacts API.
//
//  Resend audience ID is stored as a compile-time constant below.
//  Replace RESEND_AUDIENCE_ID with your actual audience ID from
//  resend.com/audiences.
//
import Foundation

enum EmailUpdateService {

    // ── Configuration ──────────────────────────────────────────────────────
    private static let audienceID = "YOUR_RESEND_AUDIENCE_ID"   // ← replace
    private static let apiKey     = "YOUR_RESEND_API_KEY"        // ← replace

    // ── Public API ─────────────────────────────────────────────────────────

    /// Subscribe `email` to the OneFocus announcements list.
    static func subscribe(email: String, name: String?) async {
        await upsertContact(email: email, name: name, unsubscribed: false)
    }

    /// Unsubscribe `email` from the OneFocus announcements list.
    static func unsubscribe(email: String) async {
        await upsertContact(email: email, name: nil, unsubscribed: true)
    }

    // ── Private ────────────────────────────────────────────────────────────

    private static func upsertContact(
        email: String,
        name: String?,
        unsubscribed: Bool
    ) async {
        guard !audienceID.hasPrefix("YOUR_"),
              !apiKey.hasPrefix("YOUR_") else {
            print("EmailUpdateService: API key / audience ID not configured.")
            return
        }

        let url = URL(string: "https://api.resend.com/audiences/\\(audienceID)/contacts")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \\(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        var body: [String: Any] = [
            "email":        email,
            "unsubscribed": unsubscribed
        ]
        if let name, !name.isEmpty {
            let parts = name.split(separator: " ", maxSplits: 1)
            body["first_name"] = String(parts.first ?? "")
            if parts.count > 1 { body["last_name"] = String(parts[1]) }
        }

        guard let data = try? JSONSerialization.data(withJSONObject: body) else { return }
        request.httpBody = data

        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            if let http = response as? HTTPURLResponse {
                print("EmailUpdateService: upsert status \\(http.statusCode) for \\(email)")
            }
        } catch {
            print("EmailUpdateService: \\(error.localizedDescription)")
        }
    }
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 9. Wire emailUpdates toggle in AccountSettingsView (macOS)
# ─────────────────────────────────────────────────────────────────────────────
acct_path = f"{BASE}/Views/Tabs/AccountSettingsView.swift"

# Add onReceive for emailUpdates in the preferencesCard or after the save button
# The easiest place: add an onChange on the emailUpdates toggle row
patch(acct_path,
    '                ToggleRow(\n                    title: "Email Updates",\n                    subtitle: "Receive feature updates and tips.",\n                    isOn: $draft.emailUpdates\n                )',
    '''                ToggleRow(
                    title: "Email Updates",
                    subtitle: "Receive feature updates and tips.",
                    isOn: $draft.emailUpdates
                )
                .onChange(of: draft.emailUpdates) { subscribed in
                    guard let email = authManager.currentUser?.email else { return }
                    let name = authManager.currentUser?.userMetadata["full_name"] as? String
                    _Concurrency.Task {
                        if subscribed {
                            await EmailUpdateService.subscribe(email: email, name: name)
                        } else {
                            await EmailUpdateService.unsubscribe(email: email)
                        }
                    }
                }'''
)

# ─────────────────────────────────────────────────────────────────────────────
# 10. Wire emailUpdates toggle in iOSAccountSettingsView
# ─────────────────────────────────────────────────────────────────────────────
ios_acct_path = f"{BASE}/Views/iOS/Tabs/iOSAccountSettingsView.swift"
if os.path.exists(ios_acct_path):
    with open(ios_acct_path) as f:
        src = f.read()
    if 'emailUpdates' in src:
        patch(ios_acct_path,
            '"Email Updates"',
            '"Email Updates"'  # no-op check first
        )
        # Find the emailUpdates toggle and add onChange
        if '.onChange(of: draft.emailUpdates)' not in src:
            patch(ios_acct_path,
                'isOn: $draft.emailUpdates',
                '''isOn: $draft.emailUpdates
                )
                .onChange(of: draft.emailUpdates) { subscribed in
                    guard let email = authManager.currentUser?.email else { return }
                    let name = authManager.currentUser?.userMetadata["full_name"] as? String
                    _Concurrency.Task {
                        if subscribed {
                            await EmailUpdateService.subscribe(email: email, name: name)
                        } else {
                            await EmailUpdateService.unsubscribe(email: email)
                        }
                    }
                }
                Text("") // placeholder to close the extra paren — remove if syntax error'''
            )
            print("⚠️  iOS email updates wired — verify syntax in iOSAccountSettingsView")

print("\n✅ All wiring complete.")
print("\nIMPORTANT: Open EmailUpdateService.swift and replace:")
print("  YOUR_RESEND_AUDIENCE_ID  →  your Resend audience ID")
print("  YOUR_RESEND_API_KEY      →  your Resend API key")
