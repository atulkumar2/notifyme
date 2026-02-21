# Medicine Management UI Dialog

## Overview

A complete tkinter-based GUI for managing medicines with full CRUD operations (Create, Read, Update, Delete). The UI provides an intuitive interface for adding, editing, and deleting medicines with comprehensive field validation.

## Components

### 1. MedicineDialog Class (`medicine_ui.py`)

A modal dialog for adding or editing individual medicine entries.

#### Features:

- **Medicine Name**: Text input field
- **Dosage**: Text input with examples (e.g., "1 tablet", "5ml", "500mg")
- **Disease Type**: Dropdown with 13+ common diseases + custom option
- **Custom Disease**: Text field that enables when "Other" is selected
- **Meal Times**: Checkboxes for Breakfast, Lunch, Dinner (multi-select)
- **Duration**: Numeric spinbox (0-3650 days, 0 = continuous)
- **Start Date**: Date picker with YYYY-MM-DD format validation

#### Validation:

- All fields are required
- Disease validation (must select type)
- Custom disease required if "Other" selected
- At least one meal time required
- Date format validation (YYYY-MM-DD)
- Duration must be non-negative

#### Callbacks:

- `on_save`: Called when medicine is saved
- Returns `Medicine` object

#### Example Usage:

```python
dialog = MedicineDialog(
    parent=root_window,
    medicine=existing_medicine,  # None for new
    on_save=callback_function
)
```

### 2. MedicineManagementWindow Class (`medicine_ui.py`)

Main window for viewing and managing all medicines.

#### Features:

- **Medicine List**: Treeview showing all medicines with columns:
  - Medicine Name
  - Dosage
  - Disease/Condition
  - Meal Times
  - Duration
  - Status (Active/Expired)

- **Buttons**:
  - ➕ Add Medicine
  - ✏️ Edit
  - 🗑️ Delete
  - Close

#### Interactions:

- Double-click to select
- Edit selected medicine
- Delete with confirmation
- Auto-refresh after changes

#### Example Usage:

```python
window = MedicineManagementWindow(
    parent=root_window,
    medicine_manager=manager_instance
)
```

### 3. open_medicine_management() Function

Helper function to open the UI in a separate thread.

```python
from notifyme_app.medicine_ui import open_medicine_management

open_medicine_management(parent_window, medicine_manager)
```

## Field Details

### Medicine Name

- **Type**: Free text
- **Required**: Yes
- **Example**: "Metformin", "Aspirin", "Vitamin D3"

### Dosage

- **Type**: Free text
- **Required**: Yes
- **Examples**:
  - "1 tablet"
  - "5ml"
  - "500mg"
  - "2 tablets of 250mg"

### Disease Type

- **Type**: Dropdown (predefined + custom)
- **Required**: Yes
- **Predefined Options**:
  - Diabetes
  - Hypertension
  - Thyroid
  - Heart Disease
  - Asthma
  - Arthritis
  - Cholesterol
  - Acid Reflux
  - Allergy
  - Vitamin Deficiency
  - Pain Relief
  - Antibiotic
  - Other

### Custom Disease

- **Type**: Text input
- **Required**: Only if "Other" selected
- **Example**: "PCOS", "Migraine", "Vitamin B12 deficiency"

### Meal Times

- **Type**: Checkbox (multi-select)
- **Required**: At least one
- **Options**: Breakfast, Lunch, Dinner
- **Purpose**: Specify when medicine should be taken

### Duration

- **Type**: Numeric spinbox
- **Range**: 0-3650 days
- **Default**: 0 (continuous)
- **Special Values**:
  - 0 = Continuous (no end date)
  - 1-30 = Short-term medication
  - 30+ = Long-term medication

### Start Date

- **Type**: Date input (YYYY-MM-DD)
- **Default**: Today's date
- **Format**: Must be YYYY-MM-DD
- **Validation**: Checks date validity

## Workflows

### Adding a New Medicine

1. User clicks "⚙️ Manage Medicines" in menu
2. MedicineManagementWindow opens
3. User clicks "➕ Add Medicine"
4. MedicineDialog opens (empty form)
5. User fills in:
   - Name: "Metformin"
   - Dosage: "500mg"
   - Disease: "Diabetes"
   - Meals: Breakfast, Lunch, Dinner (checked)
   - Duration: 90 (days)
   - Start Date: 2026-02-21
6. User clicks "Save"
7. Medicine added to manager
8. Confirmation shown: "'Metformin' has been added."
9. List refreshes automatically

### Editing Medicine

1. User selects medicine in list
2. Clicks "✏️ Edit"
3. MedicineDialog opens with current data
4. User modifies fields
5. Clicks "Save"
6. Medicine updated in manager
7. List refreshes

### Deleting Medicine

1. User selects medicine in list
2. Clicks "🗑️ Delete"
3. Confirmation dialog: "Are you sure you want to delete 'X'?"
4. If confirmed:
   - Medicine removed
   - Confirmation: "'X' has been deleted."
   - List refreshes
5. If cancelled:
   - Dialog closes
   - No changes

## Integration with App

The UI is triggered from the menu callback:

```python
# In app.py manage_medicines() method
def manage_medicines(self) -> None:
    """Open the medicine management window."""
    root = tk.Tk()
    root.withdraw()  # Hide root window

    def open_ui() -> None:
        open_medicine_management(root, self.medicine_manager)
        root.mainloop()

    thread = threading.Thread(target=open_ui, daemon=True)
    thread.start()
```

**Why separate thread?**

- Prevents blocking the system tray
- Allows multiple windows independently
- System tray remains responsive

## Data Persistence

All changes are automatically saved to:

- `medicines.json`: Contains all medicine definitions

### Save Flow:

1. User adds/edits medicine in dialog
2. Calls `on_save()` callback
3. Callback either:
   - Calls `medicine_manager.add_medicine()`
   - Or updates existing medicine
4. Manager automatically saves to JSON

### Example JSON:

```json
[
  {
    "name": "Metformin",
    "dosage": "500mg",
    "disease": "Diabetes",
    "meal_times": ["breakfast", "lunch", "dinner"],
    "duration_days": 90,
    "start_date": "2026-02-21",
    "custom_disease": null
  },
  {
    "name": "Ibuprofen",
    "dosage": "1 tablet",
    "disease": "Other",
    "meal_times": ["lunch"],
    "duration_days": 7,
    "start_date": "2026-02-18",
    "custom_disease": "Headache"
  }
]
```

## Error Handling

### Validation Errors:

- Missing medicine name → "Please enter a medicine name."
- Missing dosage → "Please enter the dosage."
- No disease selected → "Please select a disease type."
- Missing custom disease → "Please enter a custom disease name."
- No meal times → "Please select at least one meal time."
- Invalid date → "Please use YYYY-MM-DD format."
- Invalid duration → "Duration must be a positive number."

### Database Errors:

- File I/O errors → Logged and displayed
- JSON parse errors → Graceful fallback

## UI Styling

- **Theme**: System default ttk theme
- **Font**: Default system font
- **Layout**: Grid-based for consistency
- **Colors**: Platform-native
- **Icons**: Unicode emoji for buttons

### Components:

- **Labels**: ttk.Label
- **Text Fields**: ttk.Entry
- **Dropdowns**: ttk.Combobox (read-only)
- **Checkboxes**: ttk.Checkbutton
- **Spinbox**: ttk.Spinbox
- **Buttons**: ttk.Button
- **List**: ttk.Treeview
- **Frames**: ttk.Frame
- **Separators**: ttk.Separator

## Threading Considerations

The UI runs in a separate daemon thread:

- **Advantages**:
  - System tray never blocked
  - Multiple windows can be open
  - Clean separation of concerns

- **Safeguards**:
  - tkinter runs its own event loop
  - Daemon thread exits when main exits
  - All data operations thread-safe (via MedicineManager)

## User Experience

### Responsive Design:

- Modal dialogs prevent accidental navigation
- Grab focus when open
- Clear error messages
- Confirmation dialogs for destructive actions

### Data Validation:

- Type checking
- Format validation
- Requirement validation
- User-friendly error messages

### Visual Feedback:

- Confirmation notifications
- Status indicators (Active/Expired)
- Dynamic form (Custom disease only shows when needed)
- Updated list after each change

## Future Enhancements

1. **Search/Filter**: Filter medicines by name or disease
2. **Sort Columns**: Click headers to sort list
3. **Export**: Save medicine list to CSV
4. **Import**: Load medicines from CSV
5. **Reminders**: Show upcoming medicine times
6. **History**: Track adherence/completion
7. **Interactions**: Check for drug interactions
8. **Alerts**: Visual warnings for expired medicines

## Architecture Diagram

```
System Tray Menu
       ↓
manage_medicines() callback
       ↓
Create & show tkinter root (hidden)
       ↓
Launch in separate thread
       ↓
MedicineManagementWindow
  ├── MedicineDialog (Add/Edit)
  ├── Treeview (List)
  └── Buttons (CRUD operations)
       ↓
MedicineManager
  ├── Load medicines from JSON
  ├── Validate data
  ├── Update in-memory list
  └── Save to JSON
```

## Testing

Unit tests needed for:

- `MedicineDialog` form validation
- `MedicineManagementWindow` CRUD operations
- Data persistence
- Error handling
- UI interactions

Example test:

```python
def test_medicine_dialog_validation():
    """Test that dialog validates required fields."""
    dialog = MedicineDialog(parent=root)
    dialog._save()  # Without filling fields
    # Should show warning: "Please enter a medicine name."
```

## Troubleshooting

### Dialog doesn't appear:

- Check if tkinter is installed
- Verify medicine_manager is initialized
- Check logs for exceptions

### Changes not saved:

- Verify medicines.json is writable
- Check file permissions
- Check AppData folder exists

### UI is frozen:

- Ensure dialog runs in separate thread
- Check for blocking operations
- Verify event loop is running

## Summary

The medicine management UI provides a complete, user-friendly interface for managing medicines with:

- ✅ Full CRUD operations
- ✅ Comprehensive validation
- ✅ Persistent storage
- ✅ Thread-safe operation
- ✅ Intuitive design
- ✅ Error handling
- ✅ Modal dialogs
- ✅ Auto-refresh
