//  SettingsWorkingCopy.swift
//  OneFocus
//
import Foundation
#if os(macOS)
import Carbon
#endif

/// A value-type snapshot of `UserSettings` used as the backing store for
/// settings panels.  The view edits a `@State var draft: SettingsWorkingCopy`
/// and only commits changes back to `UserSettings` when the user explicitly
/// saves, preventing partial / unsaved mutations from leaking into live state.
struct SettingsWorkingCopy: Equatable {
    // MARK: - Stored Properties

    // Appearance
    var appearanceMode: UserSettings.AppearanceMode

    // Timer
    var focusMinutes: Int
    var breakMinutes: Int          // maps to UserSettings.shortBreakMinutes
    var longBreakMinutes: Int
    var sessionsBeforeLongBreak: Int

    // Behavior
    var autoStartBreaks: Bool
    var autoStartFocus: Bool
    var hapticEnabled: Bool

    // Notifications
    var notificationsEnabled: Bool
    var soundEnabled: Bool

    // Quick Notes Hotkey (macOS)
    var quickNoteHotkeyEnabled: Bool
    var quickNoteHotkeyKeyCode: UInt32
    var quickNoteHotkeyModifiers: UInt32

    // Menu Bar Mode (macOS, Pro only)
    var menuBarModeEnabled: Bool

    // Security / App Lock
    var requireAuth: Bool
    var biometricUnlock: Bool

    // Preferences
    var emailUpdates: Bool
    var analytics: Bool

    // MARK: - Memberwise init
    init(
        appearanceMode: UserSettings.AppearanceMode,
        focusMinutes: Int,
        breakMinutes: Int,
        longBreakMinutes: Int,
        sessionsBeforeLongBreak: Int,
        autoStartBreaks: Bool,
        autoStartFocus: Bool,
        hapticEnabled: Bool,
        notificationsEnabled: Bool,
        soundEnabled: Bool,
        quickNoteHotkeyEnabled: Bool,
        quickNoteHotkeyKeyCode: UInt32,
        quickNoteHotkeyModifiers: UInt32,
        menuBarModeEnabled: Bool,
        requireAuth: Bool,
        biometricUnlock: Bool,
        emailUpdates: Bool,
        analytics: Bool
    ) {
        self.appearanceMode           = appearanceMode
        self.focusMinutes             = focusMinutes
        self.breakMinutes             = breakMinutes
        self.longBreakMinutes         = longBreakMinutes
        self.sessionsBeforeLongBreak  = sessionsBeforeLongBreak
        self.autoStartBreaks          = autoStartBreaks
        self.autoStartFocus           = autoStartFocus
        self.hapticEnabled            = hapticEnabled
        self.notificationsEnabled     = notificationsEnabled
        self.soundEnabled             = soundEnabled
        self.quickNoteHotkeyEnabled   = quickNoteHotkeyEnabled
        self.quickNoteHotkeyKeyCode   = quickNoteHotkeyKeyCode
        self.quickNoteHotkeyModifiers = quickNoteHotkeyModifiers
        self.menuBarModeEnabled       = menuBarModeEnabled
        self.requireAuth              = requireAuth
        self.biometricUnlock          = biometricUnlock
        self.emailUpdates             = emailUpdates
        self.analytics                = analytics
    }

    // MARK: - Defaults
    static let defaults: SettingsWorkingCopy = {
#if os(macOS)
        let defaultModifiers = UInt32(cmdKey) | UInt32(optionKey)
#else
        let defaultModifiers: UInt32 = 0
#endif
        return SettingsWorkingCopy(
            appearanceMode:           UserSettings.AppearanceMode.system,
            focusMinutes:             25,
            breakMinutes:             5,
            longBreakMinutes:         15,
            sessionsBeforeLongBreak:  4,
            autoStartBreaks:          false,
            autoStartFocus:           false,
            hapticEnabled:            true,
            notificationsEnabled:     true,
            soundEnabled:             true,
            quickNoteHotkeyEnabled:   false,
            quickNoteHotkeyKeyCode:   0,
            quickNoteHotkeyModifiers: defaultModifiers,
            menuBarModeEnabled:       false,
            requireAuth:              false,
            biometricUnlock:          false,
            emailUpdates:             false,
            analytics:                true
        )
    }()

    // MARK: - Load from live settings
    init(from settings: UserSettings) {
        self.appearanceMode          = settings.appearanceMode
        self.focusMinutes            = settings.focusMinutes
        self.breakMinutes            = settings.shortBreakMinutes
        self.longBreakMinutes        = settings.longBreakMinutes
        self.sessionsBeforeLongBreak = settings.sessionsBeforeLongBreak
        self.autoStartBreaks         = settings.autoStartBreaks
        self.autoStartFocus          = settings.autoStartFocus
        self.hapticEnabled           = settings.hapticEnabled
        self.notificationsEnabled    = settings.notificationsEnabled
        self.soundEnabled            = settings.soundEnabled
        self.menuBarModeEnabled      = settings.menuBarModeEnabled
        self.requireAuth             = settings.requireAuth
        self.biometricUnlock         = settings.biometricUnlock
        self.emailUpdates            = settings.emailUpdates
        self.analytics               = settings.analytics
#if os(macOS)
        self.quickNoteHotkeyEnabled   = settings.quickNoteHotkeyEnabled
        self.quickNoteHotkeyKeyCode   = settings.quickNoteHotkeyKeyCode
        self.quickNoteHotkeyModifiers = settings.quickNoteHotkeyModifiers
#else
        self.quickNoteHotkeyEnabled   = false
        self.quickNoteHotkeyKeyCode   = 0
        self.quickNoteHotkeyModifiers = 0
#endif
    }

    // MARK: - Apply back to live settings
    func apply(to settings: UserSettings) {
        settings.appearanceMode          = appearanceMode
        settings.focusMinutes            = focusMinutes
        settings.shortBreakMinutes       = breakMinutes
        settings.longBreakMinutes        = longBreakMinutes
        settings.sessionsBeforeLongBreak = sessionsBeforeLongBreak
        settings.autoStartBreaks         = autoStartBreaks
        settings.autoStartFocus          = autoStartFocus
        settings.hapticEnabled           = hapticEnabled
        settings.notificationsEnabled    = notificationsEnabled
        settings.soundEnabled            = soundEnabled
        settings.menuBarModeEnabled      = menuBarModeEnabled
        settings.requireAuth             = requireAuth
        settings.biometricUnlock         = biometricUnlock
        settings.emailUpdates            = emailUpdates
        settings.analytics               = analytics
#if os(macOS)
        settings.quickNoteHotkeyEnabled   = quickNoteHotkeyEnabled
        settings.quickNoteHotkeyKeyCode   = quickNoteHotkeyKeyCode
        settings.quickNoteHotkeyModifiers = quickNoteHotkeyModifiers
#endif
    }

    mutating func resetToDefaults() {
        self = .defaults
    }
}
