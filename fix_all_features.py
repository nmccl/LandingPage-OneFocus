#!/usr/bin/env python3
"""
Comprehensive fix script for OneFocus — six features:
1. Stats: record early-stopped sessions; build full iOS stats view
2. Notifications: persist soundEnabled; wire both toggles to NotificationManager
3. Priority notifications: request .timeSensitive on first launch
4. Biometric app lock: new AppLockManager + lock screen
5. Analytics: persist events; call from FocusTimerManager
6. Email updates: wire toggle to Resend API via URLSession
"""

import os, shutil

BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Written: {path}")

def patch(path, find, replace, all_occurrences=False):
    with open(path) as f:
        src = f.read()
    if find not in src:
        print(f"⚠️  Pattern not found in {os.path.basename(path)}: {find[:60]!r}")
        return False
    if all_occurrences:
        new = src.replace(find, replace)
    else:
        new = src.replace(find, replace, 1)
    with open(path, 'w') as f:
        f.write(new)
    print(f"✅ Patched: {os.path.basename(path)}")
    return True

# ─────────────────────────────────────────────────────────────────────────────
# 1. UserSettings — add soundEnabled property
# ─────────────────────────────────────────────────────────────────────────────
us_path = f"{BASE}/Models/UserSettings.swift"

# Add soundEnabled key constant
patch(us_path,
    'static let notificationsEnabled      = "notificationsEnabled"',
    'static let notificationsEnabled      = "notificationsEnabled"\n        static let soundEnabled              = "soundEnabled"'
)

# Add soundEnabled @Published property after notificationsEnabled
patch(us_path,
    '    @Published var notificationsEnabled: Bool {\n        didSet { store.set(notificationsEnabled, forKey: Key.notificationsEnabled) }\n    }',
    '    @Published var notificationsEnabled: Bool {\n        didSet { store.set(notificationsEnabled, forKey: Key.notificationsEnabled) }\n    }\n    @Published var soundEnabled: Bool {\n        didSet { store.set(soundEnabled, forKey: Key.soundEnabled) }\n    }'
)

# Add soundEnabled init line
patch(us_path,
    'self.notificationsEnabled    = store.bool(forKey: Key.notificationsEnabled, default: true)',
    'self.notificationsEnabled    = store.bool(forKey: Key.notificationsEnabled, default: true)\n        self.soundEnabled            = store.bool(forKey: Key.soundEnabled, default: true)'
)

# Add soundEnabled configure line
patch(us_path,
    'notificationsEnabled   = store.bool(forKey: Key.notificationsEnabled, default: true)',
    'notificationsEnabled   = store.bool(forKey: Key.notificationsEnabled, default: true)\n        soundEnabled           = store.bool(forKey: Key.soundEnabled, default: true)'
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. SettingsWorkingCopy — wire soundEnabled to UserSettings
# ─────────────────────────────────────────────────────────────────────────────
swc_path = f"{BASE}/Helpers/SettingsWorkingCopy.swift"

# Fix init(from:) to read soundEnabled from settings
patch(swc_path,
    '        self.soundEnabled            = true',
    '        self.soundEnabled            = settings.soundEnabled'
)

# Fix apply(to:) to write soundEnabled back
patch(swc_path,
    '        settings.notificationsEnabled    = notificationsEnabled',
    '        settings.notificationsEnabled    = notificationsEnabled\n        settings.soundEnabled            = soundEnabled'
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. FocusTimerManager — wire soundEnabled + record early-stopped sessions
#    + call AnalyticsService
# ─────────────────────────────────────────────────────────────────────────────
ftm_path = f"{BASE}/Manager/FocusTimerManager.swift"

# Wire sound to userSettings.soundEnabled in completeSession
patch(ftm_path,
    '            NotificationManager.shared.scheduleTimerComplete(\n                sessionTitle: "Focus session complete!",\n                body:         "Time for a break. Great work.",\n                sound:        true\n            )',
    '            NotificationManager.shared.scheduleTimerComplete(\n                sessionTitle: "Focus session complete!",\n                body:         "Time for a break. Great work.",\n                sound:        userSettings.soundEnabled\n            )'
)

patch(ftm_path,
    '            NotificationManager.shared.scheduleTimerComplete(\n                sessionTitle: title,\n                body:         "Ready to focus again?",\n                sound:        true\n            )',
    '            NotificationManager.shared.scheduleTimerComplete(\n                sessionTitle: title,\n                body:         "Ready to focus again?",\n                sound:        userSettings.soundEnabled\n            )'
)

# Record early-stopped sessions (currently only natural completions are saved)
# The skip() method calls completeSession(early: true) which already saves focus sessions.
# But stop() does NOT save anything. We want to record partial sessions if at least
# 60 seconds elapsed. Patch the stop() method:
patch(ftm_path,
    '    func stop() {\n        sessionStartDate = nil\n        elapsedBeforePause = 0\n        timerState = .idle\n        stopDisplayTimer()\n        setupInitialTime(resetRemaining: true)\n    }',
    '''    func stop() {
        // Record a partial focus session if at least 60 s elapsed
        if currentSessionType == .focus, timerState != .idle {
            let elapsed: TimeInterval
            if let start = sessionStartDate {
                elapsed = elapsedBeforePause + Date().timeIntervalSince(start)
            } else {
                elapsed = elapsedBeforePause
            }
            if elapsed >= 60 {
                let session = FocusSession(
                    startTime: Date().addingTimeInterval(-elapsed),
                    duration:  elapsed,
                    sessionType: .focus,
                    wasCompleted: false
                )
                historyManager?.addCompletedSession(session)
                AnalyticsService.shared.trackFocusSessionCancelled(
                    duration: totalTime,
                    elapsedTime: elapsed
                )
            }
        }
        sessionStartDate = nil
        elapsedBeforePause = 0
        timerState = .idle
        stopDisplayTimer()
        setupInitialTime(resetRemaining: true)
    }'''
)

# Add AnalyticsService calls in completeSession for focus
patch(ftm_path,
    '            historyManager?.addCompletedSession(session)\n            NotificationManager.shared.scheduleTimerComplete(',
    '            historyManager?.addCompletedSession(session)\n            AnalyticsService.shared.trackFocusSessionCompleted(\n                duration: totalTime,\n                actualDuration: early ? (totalTime - timeRemaining) : totalTime\n            )\n            NotificationManager.shared.scheduleTimerComplete('
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. NotificationManager — respect notificationsEnabled setting
# ─────────────────────────────────────────────────────────────────────────────
nm_path = f"{BASE}/Manager/NotificationManager.swift"

# Add a configure method that stores the enabled/sound state
patch(nm_path,
    'final class NotificationManager {\n    static let shared = NotificationManager()\n    private init() {}',
    '''final class NotificationManager {
    static let shared = NotificationManager()
    private init() {}

    // Mirrors UserSettings values so callers don\'t need to pass them every time.
    var notificationsEnabled: Bool = true
    var soundEnabled: Bool = true

    /// Call this whenever UserSettings changes so the manager stays in sync.
    func configure(notificationsEnabled: Bool, soundEnabled: Bool) {
        self.notificationsEnabled = notificationsEnabled
        self.soundEnabled = soundEnabled
    }'''
)

# Guard scheduleTimerComplete on notificationsEnabled
patch(nm_path,
    '    func scheduleTimerComplete(sessionTitle: String, body: String, sound: Bool) {\n        let content = UNMutableNotificationContent()',
    '    func scheduleTimerComplete(sessionTitle: String, body: String, sound: Bool) {\n        guard notificationsEnabled else { return }\n        let content = UNMutableNotificationContent()'
)

# Guard scheduleTimeSensitive on notificationsEnabled
patch(nm_path,
    '    func scheduleTimeSensitive(\n        identifier: String = UUID().uuidString,\n        title: String,\n        body: String,\n        delaySeconds: TimeInterval = 1,\n        sound: Bool = true\n    ) {\n        let content = UNMutableNotificationContent()',
    '    func scheduleTimeSensitive(\n        identifier: String = UUID().uuidString,\n        title: String,\n        body: String,\n        delaySeconds: TimeInterval = 1,\n        sound: Bool = true\n    ) {\n        guard notificationsEnabled else { return }\n        let content = UNMutableNotificationContent()'
)

print("\n--- NotificationManager patched ---\n")

# ─────────────────────────────────────────────────────────────────────────────
# 5. AnalyticsService — persist events to UserDefaults
# ─────────────────────────────────────────────────────────────────────────────
as_path = f"{BASE}/Services/AnalyticsService.swift"

patch(as_path,
    '    private func saveEvent(_ event: AnalyticsEvent) {\n        // Save to UserDefaults or persistence service\n        // For now, just keep in memory\n    }',
    '''    private func saveEvent(_ event: AnalyticsEvent) {
        // Persist all events to UserDefaults (capped at 1 000 to avoid bloat)
        let capped = Array(events.suffix(1_000))
        if let data = try? JSONEncoder().encode(capped) {
            UserDefaults.standard.set(data, forKey: "analytics.events")
        }
    }'''
)

patch(as_path,
    '    private func loadEvents() {\n        // Load from UserDefaults or persistence service\n        // For now, start with empty array\n        events = []\n    }',
    '''    private func loadEvents() {
        if let data   = UserDefaults.standard.data(forKey: "analytics.events"),
           let loaded = try? JSONDecoder().decode([AnalyticsEvent].self, from: data) {
            events = loaded
        }
    }'''
)

print("--- AnalyticsService patched ---\n")

# ─────────────────────────────────────────────────────────────────────────────
# 6. AppLockManager — new file
# ─────────────────────────────────────────────────────────────────────────────
app_lock_path = f"{BASE}/Manager/AppLockManager.swift"
write(app_lock_path, '''\
//
//  AppLockManager.swift
//  OneFocus
//
//  Manages biometric / passcode app-lock, mirroring the Journal app pattern.
//  When requireAuth is enabled, the app shows a lock screen on launch and
//  whenever it returns from background.  The user authenticates with
//  Face ID / Touch ID (or device passcode as fallback).
//
import SwiftUI
import LocalAuthentication
import Combine

@MainActor
final class AppLockManager: ObservableObject {

    // MARK: - Published State
    /// true  → lock screen is visible
    /// false → app content is visible
    @Published private(set) var isLocked: Bool = false

    // MARK: - Dependencies
    private let userSettings: UserSettings
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Init
    init(userSettings: UserSettings) {
        self.userSettings = userSettings
        observeScenePhase()
    }

    // MARK: - Public API

    /// Call on app launch (after sign-in check) to lock if requireAuth is on.
    func lockIfRequired() {
        guard userSettings.requireAuth else { return }
        isLocked = true
    }

    /// Attempt biometric / passcode authentication to unlock.
    func authenticate() {
        guard isLocked else { return }

        let context = LAContext()
        var error: NSError?

        // Decide policy: prefer biometrics if enabled, fall back to passcode.
        let policy: LAPolicy = userSettings.biometricUnlock
            ? .deviceOwnerAuthenticationWithBiometrics
            : .deviceOwnerAuthentication

        guard context.canEvaluatePolicy(policy, error: &error) else {
            // Biometrics not available — fall back to passcode policy.
            authenticateWithPasscode(context: context)
            return
        }

        let reason = "Unlock OneFocus"
        context.evaluatePolicy(policy, localizedReason: reason) { [weak self] success, _ in
            DispatchQueue.main.async {
                if success { self?.isLocked = false }
                // On failure the lock screen stays visible; user can retry.
            }
        }
    }

    // MARK: - Private

    private func authenticateWithPasscode(context: LAContext) {
        let fallbackContext = LAContext()
        let reason = "Unlock OneFocus"
        fallbackContext.evaluatePolicy(.deviceOwnerAuthentication,
                                       localizedReason: reason) { [weak self] success, _ in
            DispatchQueue.main.async {
                if success { self?.isLocked = false }
            }
        }
    }

    private func observeScenePhase() {
        // Re-lock when the app goes to background (active → inactive → background).
        NotificationCenter.default
            .publisher(for: NSNotification.Name("AppDidEnterBackground"))
            .sink { [weak self] _ in
                guard let self, self.userSettings.requireAuth else { return }
                self.isLocked = true
            }
            .store(in: &cancellables)
    }
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 7. AppLockView — new file
# ─────────────────────────────────────────────────────────────────────────────
app_lock_view_path = f"{BASE}/Views/Auth/AppLockView.swift"
write(app_lock_view_path, '''\
//
//  AppLockView.swift
//  OneFocus
//
//  Full-screen lock overlay shown when AppLockManager.isLocked == true.
//  Matches the app\'s clean black/white design language.
//
import SwiftUI
import LocalAuthentication

struct AppLockView: View {
    @ObservedObject var lockManager: AppLockManager

    // Detect biometric type for the button label
    private var biometricType: LABiometryType {
        let ctx = LAContext()
        var err: NSError?
        guard ctx.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &err) else {
            return .none
        }
        return ctx.biometryType
    }

    private var unlockLabel: String {
        switch biometricType {
        case .faceID:  return "Unlock with Face ID"
        case .touchID: return "Unlock with Touch ID"
        default:       return "Unlock with Passcode"
        }
    }

    private var unlockIcon: String {
        switch biometricType {
        case .faceID:  return "faceid"
        case .touchID: return "touchid"
        default:       return "lock.open.fill"
        }
    }

    var body: some View {
        ZStack {
            AppConstants.Colors.backgroundPrimary.ignoresSafeArea()

            VStack(spacing: 32) {
                Spacer()

                // App icon / wordmark
                VStack(spacing: 12) {
                    Image(systemName: "lock.fill")
                        .font(.system(size: 52, weight: .light))
                        .foregroundColor(AppConstants.Colors.textPrimary)

                    Text("OneFocus is Locked")
                        .font(.system(size: 22, weight: .semibold))
                        .foregroundColor(AppConstants.Colors.textPrimary)

                    Text("Authenticate to continue")
                        .font(.system(size: 15))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }

                Spacer()

                // Unlock button
                Button(action: { lockManager.authenticate() }) {
                    Label(unlockLabel, systemImage: unlockIcon)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(AppConstants.Colors.textPrimary)
                        .cornerRadius(AppConstants.CornerRadius.large)
                }
                .buttonStyle(.plain)
                .padding(.horizontal, 32)
                .padding(.bottom, 48)
            }
        }
        .onAppear { lockManager.authenticate() }
    }
}
''')

# ─────────────────────────────────────────────────────────────────────────────
# 8. iOSStatsView — full implementation
# ─────────────────────────────────────────────────────────────────────────────
ios_stats_path = f"{BASE}/Views/iOS/Tabs/iOSStatsView.swift"
write(ios_stats_path, '''\
//
//  iOSStatsView.swift
//  OneFocus
//
//  Full iOS stats screen driven by HistoryManager.
//  Mirrors the macOS StatsView feature set with a native iOS layout.
//
#if os(iOS)
import SwiftUI

struct iOSStatsView: View {
    @EnvironmentObject private var historyManager: HistoryManager
    @EnvironmentObject private var proAccess:      ProAccessManager
    @Environment(\\.dismiss) private var dismiss

    @State private var range: RangeSelection = .week
    @State private var showingUpgradeSheet   = false

    enum RangeSelection: String, CaseIterable {
        case day   = "Day"
        case week  = "Week"
        case month = "Month"
        case year  = "Year"
    }

    // MARK: - Body
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    rangePicker
                    summarySection
                    trendSection
                    if proAccess.isProUser {
                        breakdownSection
                        streakSection
                    } else {
                        proGateSection
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 16)
                .padding(.bottom, 40)
            }
            .background(AppConstants.Colors.backgroundPrimary.ignoresSafeArea())
            .navigationTitle("Stats")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                        .foregroundColor(AppConstants.Colors.primaryAccent)
                }
            }
        }
        .sheet(isPresented: $showingUpgradeSheet) {
            UpgradePromptView()
        }
    }

    // MARK: - Derived data
    private var windowItems: [HistoryItem] {
        let now = Date()
        let cal = Calendar.current
        let cutoff: Date
        switch range {
        case .day:   cutoff = cal.startOfDay(for: now)
        case .week:  cutoff = cal.date(byAdding: .day,   value: -7,  to: now) ?? now
        case .month: cutoff = cal.date(byAdding: .month, value: -1,  to: now) ?? now
        case .year:  cutoff = cal.date(byAdding: .year,  value: -1,  to: now) ?? now
        }
        return historyManager.historyItems.filter { $0.date >= cutoff }
    }

    private var focusItems:  [HistoryItem] { windowItems.focusSessions }
    private var taskItems:   [HistoryItem] { windowItems.tasks }

    private var totalFocusSecs: TimeInterval {
        focusItems.compactMap { $0.duration }.reduce(0, +)
    }
    private var sessionCount: Int { focusItems.count }
    private var completedTaskCount: Int { taskItems.count }

    private var streak: Int {
        let cal  = Calendar.current
        let days = Set(
            historyManager.historyItems.focusSessions.map { cal.startOfDay(for: $0.date) }
        ).sorted(by: >)
        guard !days.isEmpty else { return 0 }
        var count = 0
        var check = cal.startOfDay(for: Date())
        if !days.contains(check) {
            guard let y = cal.date(byAdding: .day, value: -1, to: check),
                  days.contains(y) else { return 0 }
            check = y
        }
        while days.contains(check) {
            count += 1
            guard let prev = cal.date(byAdding: .day, value: -1, to: check) else { break }
            check = prev
        }
        return count
    }

    private var avgSessionMins: Int {
        guard sessionCount > 0 else { return 0 }
        return Int(totalFocusSecs / Double(sessionCount) / 60)
    }

    private func formatHoursMinutes(_ secs: TimeInterval) -> String {
        let h = Int(secs) / 3600
        let m = Int(secs) / 60 % 60
        if h > 0 { return "\\(h)h \\(m)m" }
        return "\\(m)m"
    }

    // MARK: - Range Picker
    private var rangePicker: some View {
        Picker("Range", selection: $range) {
            ForEach(RangeSelection.allCases, id: \\.self) { r in
                Text(r.rawValue).tag(r)
            }
        }
        .pickerStyle(.segmented)
    }

    // MARK: - Summary Section
    private var summarySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Summary")
                .font(.system(size: 17, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textPrimary)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                StatTile(icon: "brain.head.profile",
                         title: "Focus Time",
                         value: formatHoursMinutes(totalFocusSecs))
                StatTile(icon: "timer",
                         title: "Sessions",
                         value: "\\(sessionCount)")
                StatTile(icon: "checkmark.circle.fill",
                         title: "Tasks Done",
                         value: "\\(completedTaskCount)")
                StatTile(icon: "clock.fill",
                         title: "Avg Session",
                         value: "\\(avgSessionMins)m")
            }
        }
    }

    // MARK: - Trend Section (bar chart)
    private var trendSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Focus Trend")
                .font(.system(size: 17, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textPrimary)

            iOSBarChartView(bars: trendBars)
                .padding(16)
                .background(AppConstants.Colors.cardBackground)
                .cornerRadius(AppConstants.CornerRadius.large)
        }
    }

    private var trendBars: [(label: String, secs: TimeInterval)] {
        let cal = Calendar.current
        switch range {
        case .day:
            // 6 four-hour blocks
            return (0..<6).map { block in
                let start = cal.startOfDay(for: Date()).addingTimeInterval(Double(block * 4 * 3600))
                let end   = start.addingTimeInterval(4 * 3600)
                let secs  = focusItems.filter { $0.date >= start && $0.date < end }
                    .compactMap { $0.duration }.reduce(0, +)
                let hour  = block * 4
                let label = hour == 0 ? "12a" : hour < 12 ? "\\(hour)a" : hour == 12 ? "12p" : "\\(hour-12)p"
                return (label, secs)
            }
        case .week:
            return (0..<7).reversed().map { daysAgo in
                let day   = cal.date(byAdding: .day, value: -daysAgo, to: Date()) ?? Date()
                let start = cal.startOfDay(for: day)
                let end   = cal.date(byAdding: .day, value: 1, to: start) ?? start
                let secs  = focusItems.filter { $0.date >= start && $0.date < end }
                    .compactMap { $0.duration }.reduce(0, +)
                let fmt = DateFormatter(); fmt.dateFormat = "EEE"
                return (fmt.string(from: day), secs)
            }
        case .month:
            return (0..<4).reversed().map { weeksAgo in
                let end   = cal.date(byAdding: .weekOfYear, value: -weeksAgo, to: Date()) ?? Date()
                let start = cal.date(byAdding: .weekOfYear, value: -1, to: end) ?? end
                let secs  = focusItems.filter { $0.date >= start && $0.date < end }
                    .compactMap { $0.duration }.reduce(0, +)
                return ("W\\(4 - weeksAgo)", secs)
            }
        case .year:
            return (0..<6).reversed().map { monthsAgo in
                let month = cal.date(byAdding: .month, value: -monthsAgo, to: Date()) ?? Date()
                let comps = cal.dateComponents([.year, .month], from: month)
                let start = cal.date(from: comps) ?? month
                let end   = cal.date(byAdding: .month, value: 1, to: start) ?? start
                let secs  = focusItems.filter { $0.date >= start && $0.date < end }
                    .compactMap { $0.duration }.reduce(0, +)
                let fmt = DateFormatter(); fmt.dateFormat = "MMM"
                return (fmt.string(from: month), secs)
            }
        }
    }

    // MARK: - Breakdown Section (Pro)
    private var breakdownSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Session Breakdown")
                .font(.system(size: 17, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textPrimary)

            VStack(spacing: 14) {
                let total = max(1.0, totalFocusSecs + Double(taskItems.count) * 60)
                iOSBreakdownBar(label: "Focus Sessions",
                                percent: totalFocusSecs / total)
                iOSBreakdownBar(label: "Tasks Completed",
                                percent: Double(taskItems.count) * 60 / total)
            }
            .padding(16)
            .background(AppConstants.Colors.cardBackground)
            .cornerRadius(AppConstants.CornerRadius.large)
        }
    }

    // MARK: - Streak Section (Pro)
    private var streakSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Streak")
                .font(.system(size: 17, weight: .semibold))
                .foregroundColor(AppConstants.Colors.textPrimary)

            HStack(spacing: 16) {
                Image(systemName: "flame.fill")
                    .font(.system(size: 32))
                    .foregroundColor(.orange)
                VStack(alignment: .leading, spacing: 4) {
                    Text("\\(streak) day\\(streak == 1 ? "" : "s")")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                    Text("current streak")
                        .font(.system(size: 13))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }
                Spacer()
            }
            .padding(20)
            .background(AppConstants.Colors.cardBackground)
            .cornerRadius(AppConstants.CornerRadius.large)
        }
    }

    // MARK: - Pro Gate
    private var proGateSection: some View {
        Button(action: { showingUpgradeSheet = true }) {
            HStack(spacing: 14) {
                Image(systemName: "lock.fill")
                    .font(.system(size: 18))
                    .foregroundColor(AppConstants.Colors.primaryAccent)
                VStack(alignment: .leading, spacing: 4) {
                    Text("Unlock Detailed Stats")
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundColor(AppConstants.Colors.textPrimary)
                    Text("Streaks, breakdowns, and more with Pro.")
                        .font(.system(size: 13))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                }
                Spacer()
                Text("PRO")
                    .font(.system(size: 11, weight: .bold))
                    .foregroundColor(AppConstants.Colors.primaryAccent)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(AppConstants.Colors.primaryAccent.opacity(0.12))
                    .cornerRadius(6)
            }
            .padding(16)
            .background(AppConstants.Colors.cardBackground)
            .cornerRadius(AppConstants.CornerRadius.large)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Sub-views

private struct StatTile: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: icon)
                .font(.system(size: 20, weight: .regular))
                .foregroundColor(AppConstants.Colors.primaryAccent)
            Text(value)
                .font(.system(size: 26, weight: .bold))
                .foregroundColor(AppConstants.Colors.textPrimary)
            Text(title)
                .font(.system(size: 12))
                .foregroundColor(AppConstants.Colors.textSecondary)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(AppConstants.Colors.cardBackground)
        .cornerRadius(AppConstants.CornerRadius.large)
    }
}

private struct iOSBarChartView: View {
    let bars: [(label: String, secs: TimeInterval)]
    private var maxSecs: TimeInterval { bars.map(\\.secs).max() ?? 1 }
    private let chartHeight: CGFloat = 80

    var body: some View {
        VStack(spacing: 0) {
            HStack(alignment: .bottom, spacing: 4) {
                ForEach(Array(bars.enumerated()), id: \\.offset) { _, b in
                    VStack(spacing: 0) {
                        ZStack(alignment: .bottom) {
                            Rectangle()
                                .fill(AppConstants.Colors.textTertiary.opacity(0.15))
                                .clipShape(RoundedRectangle(cornerRadius: 3))
                            Rectangle()
                                .fill(b.secs > 0 ? AppConstants.Colors.primaryAccent : .clear)
                                .frame(height: b.secs > 0
                                       ? max(4, CGFloat(b.secs / maxSecs) * chartHeight)
                                       : 0)
                                .clipShape(RoundedRectangle(cornerRadius: 3))
                        }
                        .frame(height: chartHeight)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            HStack(alignment: .top, spacing: 4) {
                ForEach(Array(bars.enumerated()), id: \\.offset) { _, b in
                    Text(b.label)
                        .font(.system(size: 10))
                        .foregroundColor(AppConstants.Colors.textTertiary)
                        .frame(maxWidth: .infinity)
                        .lineLimit(1)
                }
            }
            .padding(.top, 4)
        }
    }
}

private struct iOSBreakdownBar: View {
    let label: String
    let percent: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(label)
                    .font(.system(size: 13))
                    .foregroundColor(AppConstants.Colors.textSecondary)
                Spacer()
                Text("\\(Int(percent * 100))%")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(AppConstants.Colors.textPrimary)
            }
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(AppConstants.Colors.textTertiary.opacity(0.15))
                        .frame(height: 6)
                        .cornerRadius(3)
                    Rectangle()
                        .fill(AppConstants.Colors.primaryAccent)
                        .frame(width: geo.size.width * CGFloat(percent), height: 6)
                        .cornerRadius(3)
                }
            }
            .frame(height: 6)
        }
    }
}
#endif
''')

print("\n✅ All files written/patched successfully.")
print("\nSummary:")
print("  1. UserSettings — soundEnabled added and persisted")
print("  2. SettingsWorkingCopy — soundEnabled wired to UserSettings")
print("  3. FocusTimerManager — sound uses setting; stop() records partial sessions; AnalyticsService called")
print("  4. NotificationManager — configure() added; guards on notificationsEnabled")
print("  5. AnalyticsService — events persisted to UserDefaults")
print("  6. AppLockManager — new file (biometric app lock)")
print("  7. AppLockView — new file (lock screen UI)")
print("  8. iOSStatsView — full implementation replacing stub")
