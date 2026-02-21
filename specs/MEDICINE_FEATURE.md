# Medicine Reminder Feature

## Overview

Added comprehensive medicine reminder functionality to NotifyMe application with time-window based reminders for Breakfast, Lunch, and Dinner.

## Components Implemented

### 1. Core Data Structures (`notifyme_app/medicine.py`)

#### Medicine Class

- **Properties**: name, dosage, disease, meal_times, duration_days, start_date, custom_disease
- **Methods**:
  - `is_active()`: Check if medicine is still within duration
  - `get_display_disease()`: Get disease name (custom if "Other")
  - `to_dict()`/`from_dict()`: Serialization support

#### MedicineManager Class

- **Storage**: JSON files in AppData
  - `medicines.json`: Medicine definitions
  - `medicine_completion.json`: Daily completion tracking
- **Key Methods**:
  - `add_medicine()`, `remove_medicine()`: CRUD operations
  - `get_active_medicines()`: Filter by date/duration
  - `get_medicines_for_meal_time()`: Get medicines for specific meal
  - `mark_completed()`: Mark meal time as completed for today
  - `is_completed_today()`: Check completion status
  - `should_remind()`: Check if reminder should show (time window + not completed + has medicines)

### 2. Constants Added (`notifyme_app/constants.py`)

```python
# Reminder types
REMINDER_MEDICINE = "medicine"

# Medicine meal times
MEDICINE_BREAKFAST = "breakfast"
MEDICINE_LUNCH = "lunch"
MEDICINE_DINNER = "dinner"

# Time windows (24-hour format)
DEFAULT_MEDICINE_TIME_WINDOWS = {
    MEDICINE_BREAKFAST: {"start": "07:00", "end": "09:00"},
    MEDICINE_LUNCH: {"start": "12:00", "end": "14:00"},
    MEDICINE_DINNER: {"start": "19:00", "end": "21:00"},
}

# Default reminder interval: 20 minutes
DEFAULT_MEDICINE_REMINDER_INTERVAL = 20

# Common diseases for dropdown
COMMON_DISEASES = [
    "Diabetes", "Hypertension", "Thyroid", "Heart Disease",
    "Asthma", "Arthritis", "Cholesterol", "Acid Reflux",
    "Allergy", "Vitamin Deficiency", "Pain Relief",
    "Antibiotic", "Other"
]
```

### 3. Configuration Support (`notifyme_app/config.py`)

Added global config properties:

- `medicine_enabled`: Enable/disable medicine reminders (default: True)
- `medicine_reminder_interval`: Reminder interval in minutes (default: 20)

### 4. Integration (`notifyme_app/app.py`)

#### Initialization

- Added `MedicineManager` instance
- Added `last_medicine_reminder_at` tracking dict
- Added `_setup_medicine_timers()` method

#### Timer Setup

- Creates timer for each meal time: `medicine_breakfast`, `medicine_lunch`, `medicine_dinner`
- Handlers check time windows and completion status
- Only shows reminders during active time window

#### Notification

- `_show_medicine_notification()`: Shows notification with medicine list
- Includes "Mark Completed" action button
- TTS support for medicine reminders

## How It Works

### Time-Window Based Reminders

1. **Timer Creation**: Each meal time gets its own timer (e.g., `medicine_breakfast`)
2. **Handler Logic**:

   ```python
   def handler():
       if medicine_enabled and should_remind(meal_time):
           show_notification()
   ```

3. **should_remind() checks**:
   - Not completed today? ✓
   - Has active medicines for this meal? ✓
   - Current time within window? ✓

### Example Flow (Breakfast)

```sh
Time: 07:00 AM - 09:00 AM
Medicines:
  - Metformin (500mg) for Diabetes
  - Aspirin (1 tablet) for Heart Disease

07:00 → Reminder shown
07:20 → Reminder shown (if not completed)
07:40 → Reminder shown (if not completed)
08:00 → User marks completed → No more reminders today
09:01 → Outside window → No reminders
```

## Next Steps

### TODO: Medicine Management UI

Need to create GUI components:

1. **Medicine List Dialog**
   - Show all medicines with edit/delete
   - Add new medicine button

2. **Add/Edit Medicine Dialog**
   - Medicine name (text input)
   - Dosage (text input)
   - Disease (dropdown with COMMON_DISEASES + custom)
   - Meal times (checkboxes: Breakfast, Lunch, Dinner)
   - Duration (number input in days, 0 = continuous)
   - Start date (date picker, default today)

3. **Menu Integration**
   - Add "Medicines" submenu
   - "Manage Medicines" → Opens list dialog
   - "Mark Breakfast Complete", "Mark Lunch Complete", "Mark Dinner Complete"
   - Toggle medicine reminders on/off

### TODO: Mark as Completed Handler

The notification includes an action button that launches `medicine_completed:{meal_time}`. Need to:

1. Handle notification action callbacks in app
2. Call `medicine_manager.mark_completed(meal_time)`
3. Stop showing reminders for that meal time today

### TODO: Tests

Create `tests/test_medicine.py`:

- Test Medicine class (serialization, is_active)
- Test MedicineManager (add/remove, completion tracking, should_remind)
- Test time window logic
- Test integration with app timers

## Usage (Once UI is complete)

1. **Add Medicine**: Right-click tray icon → Medicines → Manage Medicines → Add
2. **Set Time Windows**: Configure in settings (future)
3. **Receive Reminders**: During meal time windows, get reminders every 20 mins
4. **Mark Complete**: Click notification action or menu item
5. **Edit/Remove**: Manage medicines dialog

## Data Storage

All data stored in `%APPDATA%\\NotifyMe\\`:

- `medicines.json`: Medicine definitions
- `medicine_completion.json`: Completion tracking (auto-cleans after 7 days)
- `config.json`: Medicine settings

## Configuration Example

```json
{
  "global": {
    "medicine_enabled": true,
    "medicine_reminder_interval": 20
  }
}
```

## Medicine Data Example

```json
[
  {
    "name": "Metformin",
    "dosage": "500mg",
    "disease": "Diabetes",
    "meal_times": ["breakfast", "dinner"],
    "duration_days": 0,
    "start_date": "2026-02-21",
    "custom_disease": null
  }
]
```

## Completion Data Example

```json
{
  "2026-02-21": {
    "breakfast": "08:15:30",
    "lunch": "13:45:22"
  }
}
```

## Technical Notes

- All times stored in 24-hour format (HH:MM)
- Dates stored in ISO format (YYYY-MM-DD)
- Time window check uses string comparison on formatted times
- Completion tracking includes timestamp for audit trail
- Auto-cleanup prevents completion file from growing indefinitely
