#!/usr/bin/env python3
BASE = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus"

# Fix 1: Clipboard title alignment
clip_path = f"{BASE}/Views/iOS/Tabs/iOSClipboardHistoryView.swift"
with open(clip_path, "r") as f: clip = f.read()
clip = clip.replace('.navigationBarTitleDisplayMode(.inline)', '.navigationBarTitleDisplayMode(.large)', 1)
with open(clip_path, "w") as f: f.write(clip)
print("Clipboard patched")

# Fix 1: Account title alignment
acct_path = f"{BASE}/Views/iOS/Tabs/iOSAccountSettingsView.swift"
with open(acct_path, "r") as f: acct = f.read()
if '.navigationBarTitleDisplayMode' not in acct:
    acct = acct.replace('.navigationTitle("Account")', '.navigationTitle("Account")\n            .navigationBarTitleDisplayMode(.large)', 1)
else:
    acct = acct.replace('.navigationBarTitleDisplayMode(.inline)', '.navigationBarTitleDisplayMode(.large)', 1)
with open(acct_path, "w") as f: f.write(acct)
print("Account patched")

# Fix 2: System light theme = defaultLight
theme_path = f"{BASE}/Manager/AppTheme.swift"
with open(theme_path, "r") as f: theme = f.read()
old = '''        return AppTheme(
            id: "system", name: "System", isPro: false, group: .system,
            backgroundPrimary:   Color(UIColor.systemBackground),
            backgroundSecondary: Color(UIColor.secondarySystemBackground),
            modalBackground:     Color(UIColor.tertiarySystemBackground),
            inputBackground:     Color(UIColor.secondarySystemFill),
            cardBackground:      Color(UIColor.secondarySystemBackground),
            cardBorder:          Color(UIColor.separator).opacity(0.5),
            textPrimary:         Color(UIColor.label),
            textSecondary:       Color(UIColor.secondaryLabel),
            textTertiary:        Color(UIColor.tertiaryLabel),
            accent:              Color(UIColor.label),
            accentForeground:    Color(UIColor.systemBackground),
            divider:             Color(UIColor.separator),
            success: .green, warning: .orange, error: .red
        )'''
new = '''        return AppTheme(
            id: "system", name: "System", isPro: false, group: .system,
            backgroundPrimary:   Color(hex: "FFFFFF"),
            backgroundSecondary: Color(hex: "F5F5F5"),
            modalBackground:     Color(hex: "EFEFEF"),
            inputBackground:     Color(hex: "F0F0F0"),
            cardBackground:      Color(hex: "FFFFFF"),
            cardBorder:          Color(hex: "E5E5E5"),
            textPrimary:         Color(hex: "111111"),
            textSecondary:       Color(hex: "666666"),
            textTertiary:        Color(hex: "999999"),
            accent:              Color(hex: "111111"),
            accentForeground:    Color(hex: "FFFFFF"),
            divider:             Color(hex: "E5E5E5"),
            success: Color(hex: "16A34A"), warning: Color(hex: "D97706"), error: Color(hex: "DC2626")
        )'''
theme = theme.replace(old, new, 1)
with open(theme_path, "w") as f: f.write(theme)
print("AppTheme patched")

# Fix 3: iOSFocusView rewrite
focus_path = f"{BASE}/Views/iOS/Tabs/iOSFocusView.swift"
new_focus = r'''//
//  iOSFocusView.swift
//  OneFocus
//
//  iOS Focus tab — identical layout to macOS FocusView.
//
#if os(iOS)
import SwiftUI
struct iOSFocusView: View {
    @EnvironmentObject private var focusTimer:     FocusTimerManager
    @EnvironmentObject private var userSettings:   UserSettings
    @EnvironmentObject private var historyManager: HistoryManager
    @EnvironmentObject private var proAccess:      ProAccessManager
    @EnvironmentObject private var themeManager:   ThemeManager
    @State private var showingSessionCapAlert = false
    @State private var showingUpgradeSheet    = false
    private var sessionsCompletedToday: Int {
        let start = Calendar.current.startOfDay(for: Date())
        return historyManager.historyItems.filter { $0.type == .focusSession && $0.date >= start }.count
    }
    private var dailyCapReached: Bool {
        !proAccess.isProUser && sessionsCompletedToday >= FreeTierLimit.dailyFocusSessions
    }
    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            GeometryReader { geometry in
                AppConstants.Colors.backgroundPrimary.ignoresSafeArea()
                VStack(spacing: 0) {
                    Spacer()
                    Text(focusTimer.currentSessionType.title)
                        .font(.system(size: 22, weight: .regular))
                        .foregroundColor(AppConstants.Colors.textSecondary)
                        .padding(.bottom, geometry.size.height * 0.04)
                    timerRing(geometry: geometry)
                        .padding(.bottom, geometry.size.height * 0.04)
                    controlButtons
                    sessionTypePicker
                        .padding(.bottom, 22)
                    sessionDots
                    sessionUsageIndicator
                        .padding(.top, 8)
                    if dailyCapReached { capBanner.padding(.top, 8) }
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .alert("Daily Limit Reached", isPresented: $showingSessionCapAlert) {
                Button("Upgrade to Pro") { showingUpgradeSheet = true }
                Button("Cancel", role: .cancel) {}
            } message: {
                Text("Free users can complete up to \(FreeTierLimit.dailyFocusSessions) focus sessions per day. Upgrade to Pro for unlimited sessions.")
            }
            .sheet(isPresented: $showingUpgradeSheet) {
                UpgradePromptView().environmentObject(proAccess)
            }
            if !proAccess.isProUser {
                ProBadgeButton()
                    .padding(.trailing, AppConstants.Spacing.lg)
                    .padding(.bottom, AppConstants.Spacing.sm)
            }
        }
        .id(themeManager.current.id)
    }
    private func timerRing(geometry: GeometryProxy) -> some View {
        let availableHeight = geometry.size.height * 0.45
        let availableWidth  = geometry.size.width  * 0.7
        let circleSize      = min(max(min(availableHeight, availableWidth), 180), 340)
        return ZStack {
            Circle()
                .stroke(AppConstants.Colors.divider, lineWidth: 2)
                .frame(width: circleSize, height: circleSize)
            Circle()
                .trim(from: 0, to: focusTimer.progress)
                .stroke(AppConstants.Colors.textPrimary, style: StrokeStyle(lineWidth: 2, lineCap: .round))
                .frame(width: circleSize, height: circleSize)
                .rotationEffect(.degrees(-90))
                .animation(.linear(duration: 1), value: focusTimer.progress)
            Text(focusTimer.timeString)
                .font(.system(size: circleSize * 0.22, weight: .thin))
                .foregroundColor(AppConstants.Colors.textPrimary)
                .monospacedDigit()
        }
    }
    private var controlButtons: some View {
        HStack(spacing: AppConstants.Spacing.xl) {
            Button {
                focusTimer.skip()
                if userSettings.hapticEnabled { HapticManager.impact(.light) }
            } label: {
                Text("Skip")
                    .font(.system(size: 20, weight: .regular))
                    .foregroundColor(AppConstants.Colors.textPrimary)
            }
            .buttonStyle(.plain)
            Button {
                if dailyCapReached && focusTimer.currentSessionType == .focus && focusTimer.timerState == .idle {
                    showingSessionCapAlert = true; return
                }
                switch focusTimer.timerState {
                case .running: focusTimer.pause()
                default:       focusTimer.start()
                }
                if userSettings.hapticEnabled { HapticManager.impact(.medium) }
            } label: {
                Text(focusTimer.timerState == .running ? "Pause" : "Start")
                    .font(.system(size: 28, weight: .regular))
                    .foregroundColor(
                        dailyCapReached && focusTimer.currentSessionType == .focus && focusTimer.timerState == .idle
                            ? AppConstants.Colors.textTertiary
                            : AppConstants.Colors.textPrimary
                    )
            }
            .buttonStyle(.plain)
            Button {
                focusTimer.stop()
                if userSettings.hapticEnabled { HapticManager.impact(.medium) }
            } label: {
                Text("Reset")
                    .font(.system(size: 20, weight: .regular))
                    .foregroundColor(AppConstants.Colors.textPrimary)
            }
            .buttonStyle(.plain)
        }
        .padding(.bottom, 20)
    }
    private var sessionTypePicker: some View {
        HStack(spacing: AppConstants.Spacing.md) {
            sessionTypeButton(.focus,      "Focus")
            sessionTypeButton(.shortBreak, "Break")
            sessionTypeButton(.longBreak,  "Long Break")
        }
    }
    private func sessionTypeButton(_ type: FocusTimerManager.SessionType, _ label: String) -> some View {
        Button {
            focusTimer.switchToSession(type)
            if userSettings.hapticEnabled { HapticManager.impact(.light) }
        } label: {
            Text(label)
                .font(.system(size: AppConstants.FontSize.subheadline,
                              weight: focusTimer.currentSessionType == type ? .medium : .regular))
                .foregroundColor(focusTimer.currentSessionType == type
                    ? AppConstants.Colors.textPrimary
                    : AppConstants.Colors.textSecondary)
                .padding(.horizontal, AppConstants.Spacing.md)
                .padding(.vertical, AppConstants.Spacing.sm)
                .background(focusTimer.currentSessionType == type
                    ? AppConstants.Colors.backgroundTertiary
                    : Color.clear)
                .cornerRadius(AppConstants.CornerRadius.medium)
        }
        .buttonStyle(.plain)
    }
    private var sessionDots: some View {
        let dotCount = proAccess.isProUser
            ? max(1, userSettings.sessionsBeforeLongBreak)
            : FreeTierLimit.dailyFocusSessions
        let filled = proAccess.isProUser
            ? focusTimer.completedSessions % max(1, userSettings.sessionsBeforeLongBreak)
            : min(sessionsCompletedToday, FreeTierLimit.dailyFocusSessions)
        return HStack(spacing: 16) {
            ForEach(0..<dotCount, id: \.self) { index in
                Circle()
                    .fill(index < filled ? AppConstants.Colors.textPrimary : Color.clear)
                    .frame(width: 10, height: 10)
                    .overlay(Circle().stroke(AppConstants.Colors.textPrimary, lineWidth: 1.5))
                    .animation(.easeInOut(duration: AppConstants.Animation.fast), value: filled)
            }
        }
    }
    @ViewBuilder
    private var sessionUsageIndicator: some View {
        if !proAccess.isProUser {
            let remaining = max(0, FreeTierLimit.dailyFocusSessions - sessionsCompletedToday)
            Text("\(sessionsCompletedToday) of \(FreeTierLimit.dailyFocusSessions) sessions today")
                .font(.system(size: AppConstants.FontSize.caption))
                .foregroundColor(remaining == 0 ? AppConstants.Colors.primaryAccent : AppConstants.Colors.textTertiary)
        }
    }
    private var capBanner: some View {
        HStack(spacing: AppConstants.Spacing.sm) {
            Text("\(FreeTierLimit.dailyFocusSessions) / \(FreeTierLimit.dailyFocusSessions) sessions today")
                .font(.system(size: AppConstants.FontSize.caption))
                .foregroundColor(AppConstants.Colors.textSecondary)
            Spacer()
            Button("Upgrade to Pro") { showingUpgradeSheet = true }
                .font(.system(size: AppConstants.FontSize.caption, weight: .semibold))
                .foregroundColor(AppConstants.Colors.primaryAccent)
                .buttonStyle(.plain)
        }
        .padding(.horizontal, AppConstants.Spacing.lg)
        .padding(.vertical, AppConstants.Spacing.sm)
        .background(AppConstants.Colors.cardBackground)
        .cornerRadius(AppConstants.CornerRadius.medium)
        .overlay(RoundedRectangle(cornerRadius: AppConstants.CornerRadius.medium)
            .stroke(AppConstants.Colors.cardBorder, lineWidth: 0.5))
        .padding(.horizontal, AppConstants.Spacing.lg)
    }
}
#endif
'''
with open(focus_path, "w") as f: f.write(new_focus)
print("iOSFocusView.swift rewritten")

# Fix 4: Notes title bug
notes_path = f"{BASE}/Views/iOS/Tabs/iOSQuickNotesView.swift"
with open(notes_path, "r") as f: notes = f.read()

old_navlink = '''                    ForEach(filteredNotes) { note in
                        NavigationLink(
                            destination: iOSNoteEditorView(
                                note: note,
                                store: store,
                                folderManager: folderManager
                            )
                            .environmentObject(proAccess)
                        ) {
                            iOSNoteRow(
                                note: note,
                                folder: proAccess.isProUser ? folderManager.folder(for: note.folderID) : nil,
                                showFolder: proAccess.isProUser && selectedFolderID == nil
                            )
                        }
                        .listRowBackground(AppConstants.Colors.backgroundPrimary)
                        .listRowSeparatorTint(AppConstants.Colors.divider)
                    }'''

new_navlink = '''                    ForEach(filteredNotes) { note in
                        NavigationLink(
                            destination: iOSNoteEditorView(
                                noteID: note.id,
                                store: store,
                                folderManager: folderManager
                            )
                            .environmentObject(proAccess)
                        ) {
                            let liveNote = store.notes.first(where: { $0.id == note.id }) ?? note
                            iOSNoteRow(
                                note: liveNote,
                                folder: proAccess.isProUser ? folderManager.folder(for: liveNote.folderID) : nil,
                                showFolder: proAccess.isProUser && selectedFolderID == nil
                            )
                        }
                        .listRowBackground(AppConstants.Colors.backgroundPrimary)
                        .listRowSeparatorTint(AppConstants.Colors.divider)
                    }'''

notes = notes.replace(old_navlink, new_navlink, 1)

old_editor = '''struct iOSNoteEditorView: View {
    let note:          Note
    let store:         NotesStore
    let folderManager: NoteFolderManager
    @EnvironmentObject private var proAccess: ProAccessManager
    @State private var titleDraft:       String             = ""
    @State private var attrContent:      NSAttributedString = NSAttributedString(string: "")
    @State private var selectedFolderID: UUID?
    @State private var isDirty           = false
    @State private var showingFolderPicker = false'''

new_editor = '''struct iOSNoteEditorView: View {
    let noteID:        UUID
    let store:         NotesStore
    let folderManager: NoteFolderManager
    @EnvironmentObject private var proAccess: ProAccessManager
    private var note: Note { store.notes.first(where: { $0.id == noteID }) ?? Note(title: "", content: NSAttributedString(string: "")) }
    @State private var titleDraft:       String             = ""
    @State private var attrContent:      NSAttributedString = NSAttributedString(string: "")
    @State private var selectedFolderID: UUID?
    @State private var isDirty           = false
    @State private var showingFolderPicker = false'''

notes = notes.replace(old_editor, new_editor, 1)
with open(notes_path, "w") as f: f.write(notes)
print("iOSQuickNotesView.swift patched (notes title fix)")
