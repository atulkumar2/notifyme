# Medicine Reminder - Menu Integration Guide

## Menu Structure

The medicine reminders submenu is integrated into the main system tray menu with the following structure:

```
💊 Medicine Reminders
├── ⚙️ Manage Medicines (Opens management dialog - UI to be implemented)
├── [Separator]
├── ✓ Enable Medicine Reminders (Toggle checkbox)
├── [Separator]
├── ☑️ Mark Breakfast Complete (if not already marked)
│   or ✅ Breakfast (Completed) (if already marked today)
├── ☑️ Mark Lunch Complete (if not already marked)
│   or ✅ Lunch (Completed) (if already marked today)
└── ☑️ Mark Dinner Complete (if not already marked)
    or ✅ Dinner (Completed) (if already marked today)
```

## Components Implemented

### 1. Menu Constants (`notifyme_app/constants.py`)

Added MenuCallbacks for medicine functionality:

```python
class MenuCallbacks:
    MANAGE_MEDICINES = "manage_medicines"
    MARK_BREAKFAST_COMPLETED = "mark_breakfast_completed"
    MARK_LUNCH_COMPLETED = "mark_lunch_completed"
    MARK_DINNER_COMPLETED = "mark_dinner_completed"
    TOGGLE_MEDICINE_ENABLED = "toggle_medicine_enabled"
```

### 2. Menu Manager Updates (`notifyme_app/menu.py`)

#### Modified `create_menu()` signature

- Added `medicine_enabled: bool` parameter
- Added `medicine_completions: dict` parameter (tracks which meals were completed today)

#### New `_create_medicine_menu()` method

- Creates the medicine submenu with dynamic items
- Shows "Mark Completed" for incomplete meals
- Shows "✅ Completed" for already-marked meals
- Includes toggle for enable/disable medicine reminders
- Includes "Manage Medicines" button (placeholder for UI implementation)

### 3. App Integration (`notifyme_app/app.py`)

#### Menu callback registration

Added callbacks in `_get_menu_callbacks()`:

```python
MenuCallbacks.MANAGE_MEDICINES: self.manage_medicines,
MenuCallbacks.MARK_BREAKFAST_COMPLETED: lambda *_, **__: self.mark_medicine_completed(MEDICINE_BREAKFAST),
MenuCallbacks.MARK_LUNCH_COMPLETED: lambda *_, **__: self.mark_medicine_completed(MEDICINE_LUNCH),
MenuCallbacks.MARK_DINNER_COMPLETED: lambda *_, **__: self.mark_medicine_completed(MEDICINE_DINNER),
MenuCallbacks.TOGGLE_MEDICINE_ENABLED: self.toggle_medicine_enabled,
```

#### New methods

**`manage_medicines()`**

- Currently shows placeholder notification
- TODO: Will open full medicine management UI dialog
- Allows add/edit/delete medicines
- Configure disease types and medicine details

**`mark_medicine_completed(meal_time)`**

- Calls `medicine_manager.mark_completed(meal_time)`
- Shows confirmation notification
- Updates menu to show "✅ Completed" status
- Prevents duplicate reminders for the marked meal today

**`toggle_medicine_enabled()`**

- Toggles `config.medicine_enabled`
- Shows confirmation notification
- Updates menu to reflect new state

#### Menu updates

- Modified `update_menu()` to pass medicine completion status
- Passes `medicine_enabled` state and today's completions to menu creation
- Gets today's date and retrieves completion tracking from MedicineManager

## Workflow Examples

### Mark Breakfast as Completed

1. User opens system tray menu
2. Selects "💊 Medicine Reminders"
3. Clicks "☑️ Mark Breakfast Complete"
4. Notification shown: "✅ Breakfast Medicine Completed - Marked Breakfast medicine as taken for today."
5. Menu updates to show "✅ Breakfast (Completed)" instead
6. No more breakfast reminders appear today (until tomorrow)

### Toggle Medicine Reminders

1. User opens system tray menu
2. Selects "💊 Medicine Reminders"
3. Clicks "✓ Enable Medicine Reminders" to toggle
4. Notification shows: "💊 Medicine Reminders - Medicine reminders have been [enabled/disabled]."
5. Medicine timers start/stop based on toggle state

### Open Medicine Management

1. User opens system tray menu
2. Selects "💊 Medicine Reminders"
3. Clicks "⚙️ Manage Medicines"
4. Placeholder dialog shown (UI to be implemented)

## Data Flow

```
Menu Creation Flow:
-------------------
1. update_menu() called
2. Get today's date: "2026-02-21"
3. Get completions: medicine_manager.completions["2026-02-21"]
4. Call menu_manager.create_menu(..., medicine_completions={...})
5. Menu renders with dynamic completion status

Menu Item Selection Flow:
------------------------
1. User clicks "Mark Breakfast Complete"
2. Callback: mark_medicine_completed(MEDICINE_BREAKFAST)
3. medicine_manager.mark_completed("breakfast")
4. Entry added to completions: {"2026-02-21": {"breakfast": "08:15:30"}}
5. Show confirmation notification
6. Call update_menu() to refresh
7. Menu re-renders with "✅ Breakfast (Completed)"

Timer Flow:
-----------
1. Medicine timer triggers for breakfast
2. Handler calls: should_remind("breakfast")
3. Check: is_completed_today("breakfast") → False initially
4. Check: within time window (07:00-09:00) → True
5. Check: has active medicines → True
6. Result: Show reminder notification
7. User marks complete via menu
8. Next timer trigger: is_completed_today("breakfast") → True
9. Result: Skip notification
```

## Configuration Integration

Medicine settings stored in `config.json`:

```json
{
  "global": {
    "medicine_enabled": true,
    "medicine_reminder_interval": 20
  }
}
```

## Completion Tracking

Daily completion tracking with auto-cleanup:

```json
{
  "2026-02-21": {
    "breakfast": "08:15:30",
    "lunch": "13:45:22"
  },
  "2026-02-20": {
    "breakfast": "07:55:10",
    "lunch": "12:30:45",
    "dinner": "19:15:33"
  }
}
```

- Entries older than 7 days auto-deleted
- Includes timestamp for audit trail
- Resets daily at midnight

## State Management

Menu reflects three states per meal:

1. **Not Started**: Shows "☑️ Mark [Meal] Complete"
   - Allows user to mark as completed

2. **Completed**: Shows "✅ [Meal] (Completed)"
   - Disabled menu item (not clickable)
   - Visual indication of completion

3. **Past Time Window**: (Between windows)
   - Still shows completion status
   - Menu grayed out if already completed

## Testing

Current test coverage:

- All 50 existing tests pass
- Menu creation tested
- Callback routing verified
- State transitions working

Additional test recommendations:

- `test_mark_medicine_completed()`
- `test_toggle_medicine_enabled()`
- `test_medicine_menu_structure()`
- `test_completion_status_display()`
- `test_medicine_notification_content()`

## Next Steps

### 1. Medicine Management UI (High Priority)

Create a dialog window with:

- **Add Medicine Button**
  - Medicine name input
  - Dosage input (e.g., "1 tablet", "5ml")
  - Disease dropdown (with custom option)
  - Meal time checkboxes (Breakfast, Lunch, Dinner)
  - Duration input (days, 0 = continuous)
  - Start date picker (default: today)

- **Medicine List**
  - Show all medicines with details
  - Edit button for each
  - Delete button for each
  - Yellow warning if expired

- **Time Window Configuration**
  - Current: 7-9 AM (Breakfast)
  - Current: 12-2 PM (Lunch)
  - Current: 7-9 PM (Dinner)
  - Allow customization per meal

### 2. Notification Action Handling

- Handle notification action buttons
- When user clicks "Mark Completed" in notification
- Should trigger completion without opening menu
- Implement Windows notification actions

### 3. Enhanced UI Features

- Show count of active medicines in menu
- Visual indicators (icons) for medicine status
- Medicine list in tooltip/title
- Desktop reminder service integration

## API Reference

### mark_medicine_completed(meal_time: str) → None

Mark a meal time as completed for today.

- Updates completion tracking
- Shows confirmation notification
- Refreshes menu

### manage_medicines() → None

Open the medicine management dialog.

- Shows placeholder notification
- TODO: Implement full UI

### toggle_medicine_enabled() → None

Toggle medicine reminders on/off globally.

- Updates config
- Shows status notification
- Updates menu

## Implementation Notes

- All medicine menu items are dynamically generated
- Completion status checked at menu creation time
- No database required - uses JSON files
- Auto-cleanup prevents data bloat
- Time windows configurable (currently hardcoded defaults)
- TTS/Sound settings inherited from global config

## Known Limitations

1. Medicine management UI not yet implemented
2. Time windows currently hardcoded (not configurable from UI)
3. Notification action buttons not yet handled
4. No disease/medicine database - custom entry only
5. No medicine history/analytics yet

## Future Enhancements

- Medicine history with adherence tracking
- Export to CSV for doctor visits
- Smart reminders based on meal times
- Medicine interactions checker
- Multi-user support
- Cloud sync backup
