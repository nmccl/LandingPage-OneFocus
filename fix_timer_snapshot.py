"""
Fix: Preserve focus session state when switching to break and back.

Strategy:
1. Add a SessionSnapshot struct to hold the paused state of a session.
2. Add a private dictionary [SessionType: SessionSnapshot] to store snapshots.
3. Rewrite switchToSession() to:
   - Snapshot the current session's remaining time + elapsedBeforePause + timerState
     (but stop the display timer and pause the wall-clock without calling stop())
   - Restore a snapshot if one exists for the target session type
   - Otherwise set up fresh time for the target session
4. When a session completes naturally (completeSession), clear its snapshot.
5. When stop() / reset is called, clear all snapshots.
"""
import sys

path = "/Users/noahmcclung/Development/Apple/Softwares/OneFocus/OneFocus/Manager/FocusTimerManager.swift"

with open(path) as f:
    content = f.read()

# ── 1. Add snapshot storage after the displayTimer property ──────────────────
OLD_PROPS = (
    "    // MARK: - Wall-clock Timing\n\n"
    "    private var sessionStartDate: Date?\n"
    "    private var elapsedBeforePause: TimeInterval = 0\n"
    "    private var displayTimer: Foundation.Timer?"
)

NEW_PROPS = (
    "    // MARK: - Wall-clock Timing\n\n"
    "    private var sessionStartDate: Date?\n"
    "    private var elapsedBeforePause: TimeInterval = 0\n"
    "    private var displayTimer: Foundation.Timer?\n"
    "\n"
    "    // MARK: - Session Snapshots\n"
    "    // Stores the paused state of each session type so switching away and back\n"
    "    // preserves the timer exactly where it was left.\n"
    "    private struct SessionSnapshot {\n"
    "        let timeRemaining: TimeInterval\n"
    "        let elapsedBeforePause: TimeInterval\n"
    "        let timerState: TimerState   // .idle or .paused (never .running)\n"
    "    }\n"
    "    private var snapshots: [SessionType: SessionSnapshot] = [:]"
)

if OLD_PROPS not in content:
    print("ERROR: Could not find wall-clock timing properties block")
    sys.exit(1)

content = content.replace(OLD_PROPS, NEW_PROPS, 1)
print("Step 1 (add snapshot storage): OK")

# ── 2. Rewrite switchToSession() ─────────────────────────────────────────────
OLD_SWITCH = (
    "    func switchToSession(_ type: SessionType) {\n"
    "        guard type != currentSessionType else { return }\n"
    "        // Only stop (and record a partial session) if the timer is actively\n"
    "        // running or paused. When idle, just switch the label and reset the\n"
    "        // display -- no need to tear down a session that never started.\n"
    "        if timerState != .idle {\n"
    "            stop()\n"
    "        }\n"
    "        currentSessionType = type\n"
    "        setupInitialTime(resetRemaining: true)\n"
    "    }"
)

NEW_SWITCH = (
    "    func switchToSession(_ type: SessionType) {\n"
    "        guard type != currentSessionType else { return }\n"
    "\n"
    "        // ── Snapshot the current session ────────────────────────────────\n"
    "        // Freeze the display timer so the wall-clock stops advancing, then\n"
    "        // record how much time was left and how much had elapsed.\n"
    "        if timerState != .idle {\n"
    "            stopDisplayTimer()\n"
    "            // If still running, bank the elapsed time up to now.\n"
    "            if timerState == .running, let start = sessionStartDate {\n"
    "                elapsedBeforePause += Date().timeIntervalSince(start)\n"
    "                sessionStartDate = nil\n"
    "            }\n"
    "            // Save the snapshot for the session we're leaving.\n"
    "            snapshots[currentSessionType] = SessionSnapshot(\n"
    "                timeRemaining:     timeRemaining,\n"
    "                elapsedBeforePause: elapsedBeforePause,\n"
    "                timerState:        .paused\n"
    "            )\n"
    "            // Reset transient running state without recording a partial session.\n"
    "            elapsedBeforePause = 0\n"
    "            sessionStartDate   = nil\n"
    "            timerState         = .idle\n"
    "        }\n"
    "\n"
    "        // ── Switch to the target session ─────────────────────────────────\n"
    "        currentSessionType = type\n"
    "\n"
    "        if let snapshot = snapshots[type] {\n"
    "            // Restore the previously saved state for this session type.\n"
    "            totalTime          = {\n"
    "                switch type {\n"
    "                case .focus:      return userSettings.focusDuration\n"
    "                case .shortBreak: return userSettings.breakDuration\n"
    "                case .longBreak:  return userSettings.longBreakDuration\n"
    "                }\n"
    "            }()\n"
    "            timeRemaining      = snapshot.timeRemaining\n"
    "            elapsedBeforePause = snapshot.elapsedBeforePause\n"
    "            timerState         = snapshot.timerState   // .paused\n"
    "            // Leave the display timer stopped; user must tap play to resume.\n"
    "        } else {\n"
    "            // No prior state — start fresh for this session type.\n"
    "            setupInitialTime(resetRemaining: true)\n"
    "        }\n"
    "    }"
)

if OLD_SWITCH not in content:
    print("ERROR: Could not find old switchToSession() function")
    # Show what's there
    idx = content.find("func switchToSession")
    print(repr(content[idx:idx+400]))
    sys.exit(1)

content = content.replace(OLD_SWITCH, NEW_SWITCH, 1)
print("Step 2 (rewrite switchToSession): OK")

# ── 3. Clear snapshots in stop() ─────────────────────────────────────────────
# stop() already resets everything; we just need to clear the snapshots dict too.
OLD_STOP_END = (
    "        sessionStartDate = nil\n"
    "        elapsedBeforePause = 0\n"
    "        timerState = .idle\n"
    "        stopDisplayTimer()\n"
    "        setupInitialTime(resetRemaining: true)\n"
    "    }\n\n"
    "    func toggleStartPause()"
)

NEW_STOP_END = (
    "        sessionStartDate = nil\n"
    "        elapsedBeforePause = 0\n"
    "        timerState = .idle\n"
    "        stopDisplayTimer()\n"
    "        snapshots.removeAll()   // clear all saved session states on a full reset\n"
    "        setupInitialTime(resetRemaining: true)\n"
    "    }\n\n"
    "    func toggleStartPause()"
)

if OLD_STOP_END not in content:
    print("ERROR: Could not find stop() tail anchor")
    sys.exit(1)

content = content.replace(OLD_STOP_END, NEW_STOP_END, 1)
print("Step 3 (clear snapshots in stop): OK")

# ── 4. Clear the snapshot for a session when it completes naturally ───────────
# In completeSession(), after advanceSessionType(), clear the snapshot for the
# session that just completed so it starts fresh next time.
OLD_ADVANCE = (
    "        advanceSessionType()\n"
    "        setupInitialTime(resetRemaining: true)\n"
    "        timerState = .idle\n\n"
    "        if shouldAutoStart() { start() }"
)

NEW_ADVANCE = (
    "        // Clear the snapshot for the session that just completed so it\n"
    "        // starts fresh the next time the user manually selects it.\n"
    "        let completedType = currentSessionType\n"
    "        advanceSessionType()\n"
    "        snapshots.removeValue(forKey: completedType)\n"
    "        setupInitialTime(resetRemaining: true)\n"
    "        timerState = .idle\n\n"
    "        if shouldAutoStart() { start() }"
)

if OLD_ADVANCE not in content:
    print("ERROR: Could not find advanceSessionType() anchor in completeSession")
    sys.exit(1)

content = content.replace(OLD_ADVANCE, NEW_ADVANCE, 1)
print("Step 4 (clear snapshot on completion): OK")

with open(path, "w") as f:
    f.write(content)

print("\nAll steps complete. FocusTimerManager.swift updated.")
