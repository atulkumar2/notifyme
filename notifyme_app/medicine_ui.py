"""
Medicine management UI dialog for the NotifyMe application.

This module provides a tkinter-based GUI for managing medicines,
including adding, editing, and deleting medicine entries.
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable

from notifyme_app.logger import get_logger

from notifyme_app.constants import (
    ALL_MEDICINE_TIMES,
    COMMON_DISEASES,
    DAYS_OF_WEEK_SHORT,
    DISEASE_OTHER,
    MEDICINE_FREQ_DAILY,
    MEDICINE_FREQ_HOURLY,
    APP_NAME,
    MedicineFields,
    MedicineTimeLabels,
)
from notifyme_app.medicine import Medicine, MedicineManager


class MedicineEditFrame(ttk.Frame):
    """Frame for adding or editing a medicine entry."""

    def __init__(
        self,
        parent: tk.Widget,
        medicine: Medicine | None = None,
        on_save: Callable[[Medicine], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Initialize the medicine edit frame.

        Args:
            parent: Parent widget
            medicine: Medicine to edit (None for new medicine)
            on_save: Callback when medicine is saved
            on_cancel: Callback when edit is cancelled
        """
        super().__init__(parent, padding="10")
        self.logger = get_logger(__name__)
        self.medicine = medicine
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Initialize UI components/variables to avoid linting warnings
        self.name_entry: ttk.Entry = None
        self.dosage_entry: ttk.Entry = None
        self.disease_var: tk.StringVar = None
        self.custom_disease_label: ttk.Label = None
        self.custom_disease_entry: ttk.Entry = None
        self.meal_time_vars: dict[str, tk.BooleanVar] = {}
        self.freq_var: tk.StringVar = None
        self.hourly_label: ttk.Label = None
        self.hourly_spinbox: ttk.Spinbox = None
        self.days_label: ttk.Label = None
        self.days_frame: ttk.Frame = None
        self.day_vars: list[tk.BooleanVar] = []
        self.duration_spinbox: ttk.Spinbox = None
        self.year_var: tk.StringVar = None
        self.year_combo: ttk.Combobox = None
        self.month_var: tk.StringVar = None
        self.month_combo: ttk.Combobox = None
        self.day_var: tk.StringVar = None
        self.day_combo: ttk.Combobox = None

        self._create_widgets()

        if medicine:
            self._populate_fields(medicine)

    def _create_widgets(self) -> None:
        """Create the frame widgets."""
        # Title
        title_label = ttk.Label(
            self,
            text=f"{APP_NAME} - Medicine Details",
            font=("Arial", 14, "bold"),
            padding=(0, 0, 0, 10),
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # Medicine Name
        ttk.Label(self, text="Medicine Name:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.name_entry = ttk.Entry(self, width=40)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # Dosage
        ttk.Label(self, text="Dosage:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.dosage_entry = ttk.Entry(self, width=40)
        self.dosage_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        ttk.Label(
            self, text="(e.g., '1 tablet', '5ml', '500mg')", font=("Arial", 9)
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Disease Type
        ttk.Label(self, text="Disease Type:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.disease_var = tk.StringVar()
        disease_combo = ttk.Combobox(
            self,
            textvariable=self.disease_var,
            values=COMMON_DISEASES,
            state="readonly",
            width=37,
        )
        disease_combo.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # custom disease (shown when DISEASE_OTHER is selected)
        self.custom_disease_label = ttk.Label(self, text="Custom Disease:")
        self.custom_disease_entry = ttk.Entry(self, width=40)
        # We don't grid them yet, will be done in _on_disease_selected

        # Binding to show/hide custom disease
        disease_combo.bind("<<ComboboxSelected>>", self._on_disease_selected)

        # Meal Times
        ttk.Label(self, text="Take with meals:").grid(
            row=6, column=0, sticky=tk.W, pady=(15, 5)
        )
        meal_frame = ttk.Frame(self)
        meal_frame.grid(row=6, column=1, sticky=tk.W, pady=(15, 5))

        self.meal_time_vars = {}
        for meal_time in ALL_MEDICINE_TIMES:
            meal_label = MedicineTimeLabels.get(meal_time, meal_time.title())
            var = tk.BooleanVar()
            self.meal_time_vars[meal_time] = var
            check = ttk.Checkbutton(meal_frame, text=meal_label, variable=var)
            check.pack(side=tk.LEFT, padx=(0, 15))

        # Scheduling Frequency
        ttk.Label(self, text="Frequency:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.freq_var = tk.StringVar(value=MEDICINE_FREQ_DAILY)
        freq_frame = ttk.Frame(self)
        freq_frame.grid(row=7, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(
            freq_frame,
            text="Daily",
            variable=self.freq_var,
            value=MEDICINE_FREQ_DAILY,
            command=self._on_freq_change,
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            freq_frame,
            text="Every X Hours",
            variable=self.freq_var,
            value=MEDICINE_FREQ_HOURLY,
            command=self._on_freq_change,
        ).pack(side=tk.LEFT)

        # Hourly Interval (Dynamic)
        self.hourly_label = ttk.Label(self, text="Every (hours):")
        self.hourly_spinbox = ttk.Spinbox(self, from_=1, to=24, width=5)
        self.hourly_spinbox.set(4)

        # Days of the Week (Daily only)
        self.days_label = ttk.Label(self, text="On Days:")
        self.days_frame = ttk.Frame(self)
        self.day_vars = []
        for day in DAYS_OF_WEEK_SHORT:
            var = tk.BooleanVar(value=True)
            self.day_vars.append(var)
            check = ttk.Checkbutton(self.days_frame, text=day, variable=var)
            check.pack(side=tk.LEFT, padx=(0, 5))

        # Grid scheduling options (initial state: daily)
        self.days_label.grid(row=8, column=0, sticky=tk.W, pady=5)
        self.days_frame.grid(row=8, column=1, sticky=tk.W, pady=5)

        # Duration
        ttk.Label(self, text="Duration:").grid(
            row=10, column=0, sticky=tk.W, pady=(15, 5)
        )
        duration_frame = ttk.Frame(self)
        duration_frame.grid(row=10, column=1, sticky=tk.W, pady=(15, 5))

        self.duration_spinbox = ttk.Spinbox(duration_frame, from_=0, to=3650, width=5)
        self.duration_spinbox.set(0)
        self.duration_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(duration_frame, text="Days (0 = continuous)").pack(side=tk.LEFT)

        # Start Date (Date Chooser fallback)
        ttk.Label(self, text="Start Date:").grid(row=12, column=0, sticky=tk.W, pady=5)
        self._create_date_chooser(row=12, col=1)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=14, column=0, columnspan=2, sticky=tk.EW, pady=(20, 0))

        ttk.Button(button_frame, text="Save", command=self._save).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(
            side=tk.LEFT, padx=5
        )

        # Configure grid weight
        self.columnconfigure(1, weight=1)

    def _create_date_chooser(self, row: int, col: int) -> None:
        """Create a custom date chooser using comboboxes."""
        date_frame = ttk.Frame(self)
        date_frame.grid(row=row, column=col, sticky=tk.W, pady=5)

        # Year
        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year, current_year + 11)]
        self.year_combo = ttk.Combobox(
            date_frame,
            textvariable=self.year_var,
            values=years,
            width=6,
            state="readonly",
        )
        self.year_combo.pack(side=tk.LEFT, padx=(0, 5))

        # Month
        self.month_var = tk.StringVar(value=datetime.now().strftime("%m"))
        months = [f"{m:02d}" for m in range(1, 13)]
        self.month_combo = ttk.Combobox(
            date_frame,
            textvariable=self.month_var,
            values=months,
            width=4,
            state="readonly",
        )
        self.month_combo.pack(side=tk.LEFT, padx=(0, 5))

        # Day
        self.day_var = tk.StringVar(value=datetime.now().strftime("%d"))
        days = [f"{d:02d}" for d in range(1, 32)]
        self.day_combo = ttk.Combobox(
            date_frame,
            textvariable=self.day_var,
            values=days,
            width=4,
            state="readonly",
        )
        self.day_combo.pack(side=tk.LEFT)

    def _on_freq_change(self) -> None:
        """Handle frequency type change."""
        freq = self.freq_var.get()
        if freq == MEDICINE_FREQ_HOURLY:
            self.days_label.grid_forget()
            self.days_frame.grid_forget()
            self.hourly_label.grid(row=8, column=0, sticky=tk.W, pady=5)
            self.hourly_spinbox.grid(row=8, column=1, sticky=tk.W, pady=5)
        else:
            self.hourly_label.grid_forget()
            self.hourly_spinbox.grid_forget()
            self.days_label.grid(row=8, column=0, sticky=tk.W, pady=5)
            self.days_frame.grid(row=8, column=1, sticky=tk.W, pady=5)

        # Force resize
        if hasattr(self.master.master, "geometry"):
            self.master.master.geometry("")

    def _on_disease_selected(self, _event=None) -> None:
        """Handle disease selection change."""
        disease = self.disease_var.get()
        if disease == DISEASE_OTHER:
            self.custom_disease_label.grid(row=5, column=0, sticky=tk.W, pady=5)
            self.custom_disease_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)
            self.custom_disease_entry.config(state=tk.NORMAL)
            self.custom_disease_entry.focus()
        else:
            self.custom_disease_label.grid_forget()
            self.custom_disease_entry.grid_forget()
            self.custom_disease_entry.config(state=tk.DISABLED)
            self.custom_disease_entry.delete(0, tk.END)

        # Force resize
        if hasattr(self.master.master, "geometry"):
            self.master.master.geometry("")

    def _populate_fields(self, medicine: Medicine) -> None:
        """Populate fields with existing medicine data."""
        self.name_entry.insert(0, medicine.name)
        self.dosage_entry.insert(0, medicine.dosage)
        self.disease_var.set(medicine.disease)

        if medicine.disease == DISEASE_OTHER and medicine.custom_disease:
            self.custom_disease_label.grid(row=5, column=0, sticky=tk.W, pady=5)
            self.custom_disease_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)
            self.custom_disease_entry.config(state=tk.NORMAL)
            self.custom_disease_entry.insert(0, medicine.custom_disease)
        else:
            self.custom_disease_label.grid_forget()
            self.custom_disease_entry.grid_forget()
            self.custom_disease_entry.config(state=tk.DISABLED)

        for meal_time, var in self.meal_time_vars.items():
            var.set(meal_time in medicine.meal_times)

        # Scheduling fields
        self.freq_var.set(medicine.frequency)
        if medicine.frequency == MEDICINE_FREQ_HOURLY:
            self.hourly_spinbox.set(str(medicine.hourly_interval or 4))
        else:
            # Populate day checkboxes
            for i, var in enumerate(self.day_vars):
                var.set(i in medicine.days_of_week)
        self._on_freq_change()

        self.duration_spinbox.delete(0, tk.END)
        self.duration_spinbox.set(str(medicine.duration_days))

        # Populate date chooser
        if medicine.start_date:
            try:
                dt = datetime.strptime(medicine.start_date, "%Y-%m-%d")
                self.year_var.set(str(dt.year))
                self.month_var.set(f"{dt.month:02d}")
                self.day_var.set(f"{dt.day:02d}")
            except ValueError:
                pass

    def _cancel(self) -> None:
        """Cancel the edit and return to the list."""
        if self.on_cancel:
            self.on_cancel()

    def _save(self) -> None:
        """Save and validate the medicine entry."""
        # Validate inputs
        name = self.name_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        disease = self.disease_var.get()
        custom_disease = (
            self.custom_disease_entry.get().strip()
            if disease == DISEASE_OTHER
            else None
        )

        if not name:
            messagebox.showwarning(
                f"{APP_NAME} - Missing Field", "Please enter a medicine name."
            )
            return

        if not dosage:
            messagebox.showwarning(
                f"{APP_NAME} - Missing Field", "Please enter the dosage."
            )
            return

        if not disease:
            messagebox.showwarning(
                f"{APP_NAME} - Missing Field", "Please select a disease type."
            )
            return

        if disease == DISEASE_OTHER and not custom_disease:
            messagebox.showwarning(
                f"{APP_NAME} - Missing Field", "Please enter a custom disease name."
            )
            return

        # Get selected meal times
        meal_times = [mt for mt, var in self.meal_time_vars.items() if var.get()]
        # Meal times are optional now if frequency is hourly, but ideally user picks something.
        # However, let's stick to the user's need for hourly.

        frequency = self.freq_var.get()
        hourly_interval = None
        days_of_week = None

        if frequency == MEDICINE_FREQ_HOURLY:
            try:
                hourly_interval = int(self.hourly_spinbox.get())
            except ValueError:
                messagebox.showerror(
                    f"{APP_NAME} - Invalid Interval",
                    "Please enter a valid hourly interval.",
                )
                return
        else:
            days_of_week = [i for i, var in enumerate(self.day_vars) if var.get()]
            if not days_of_week:
                messagebox.showwarning(
                    f"{APP_NAME} - No Days", "Please select at least one day."
                )
                return

        # Validate date from chooser
        start_date = (
            f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"
        )
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                f"{APP_NAME} - Invalid Date", "The selected date is invalid."
            )
            return

        # Validate duration
        try:
            duration = int(self.duration_spinbox.get())
            if duration < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                f"{APP_NAME} - Invalid Duration", "Duration must be a positive number."
            )
            return

        # Create medicine object
        medicine = Medicine(
            name=name,
            dosage=dosage,
            disease=disease,
            meal_times=meal_times,
            duration_days=duration,
            start_date=start_date,
            custom_disease=custom_disease,
            frequency=frequency,
            hourly_interval=hourly_interval,
            days_of_week=days_of_week,
        )

        if self.on_save:
            self.on_save(medicine)


class MedicineListFrame(ttk.Frame):
    """Frame for managing medicines list."""

    def __init__(
        self,
        parent: tk.Widget,
        medicine_manager: MedicineManager,
        on_add: Callable[[], None],
        on_edit: Callable[[Medicine, int], None],
    ):
        """Initialize the medicine list frame.

        Args:
            parent: Parent widget
            medicine_manager: MedicineManager instance
            on_add: Callback to show add frame
            on_edit: Callback to show edit frame
        """
        super().__init__(parent, padding="10")
        self.logger = get_logger(__name__)
        self.medicine_manager = medicine_manager
        self.on_add = on_add
        self.on_edit = on_edit

        self.tree: ttk.Treeview = None

        self._create_widgets()
        self.refresh()

    def _create_widgets(self) -> None:
        """Create the window widgets."""
        # Top frame for buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        ttk.Button(button_frame, text="➕ Add Medicine", command=self.on_add).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="✏️ Edit", command=self._on_edit_click).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="🗑️ Delete", command=self._delete_medicine).pack(
            side=tk.LEFT, padx=5
        )

        # Treeview for medicines
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = (
            MedicineFields.NAME,
            MedicineFields.DOSAGE,
            MedicineFields.DISEASE,
            MedicineFields.MEAL_TIMES,
            MedicineFields.DURATION_DAYS,
            MedicineFields.FREQUENCY,
            MedicineFields.STATUS,
        )
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, height=15, show="headings"
        )

        # Define headings and widths
        self.tree.heading(MedicineFields.NAME, text="Medicine Name")
        self.tree.heading(MedicineFields.DOSAGE, text="Dosage")
        self.tree.heading(MedicineFields.DISEASE, text="Disease/Condition")
        self.tree.heading(MedicineFields.MEAL_TIMES, text="Meal Times")
        self.tree.heading(MedicineFields.DURATION_DAYS, text="Duration")
        self.tree.heading(MedicineFields.FREQUENCY, text="Frequency")
        self.tree.heading(MedicineFields.STATUS, text="Status")

        self.tree.column(MedicineFields.NAME, width=120)
        self.tree.column(MedicineFields.DOSAGE, width=80)
        self.tree.column(MedicineFields.DISEASE, width=120)
        self.tree.column(MedicineFields.MEAL_TIMES, width=100)
        self.tree.column(MedicineFields.DURATION_DAYS, width=80)
        self.tree.column(MedicineFields.FREQUENCY, width=100)
        self.tree.column(MedicineFields.STATUS, width=70)

        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

    def refresh(self) -> None:
        """Refresh the medicine list."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add medicines
        for idx, medicine in enumerate(self.medicine_manager.medicines):
            status = "Active" if medicine.is_active() else "Expired"

            meal_str = ", ".join(
                [MedicineTimeLabels.get(mt, mt.title()) for mt in medicine.meal_times]
            )

            duration_str = (
                "Continuous"
                if medicine.duration_days == 0
                else f"{medicine.duration_days} days"
            )

            freq_str = (
                "Daily"
                if medicine.frequency == MEDICINE_FREQ_DAILY
                else f"Every {medicine.hourly_interval}h"
            )
            if (
                medicine.frequency == MEDICINE_FREQ_DAILY
                and len(medicine.days_of_week) < 7
            ):
                days_str = ", ".join(
                    [DAYS_OF_WEEK_SHORT[i] for i in medicine.days_of_week]
                )
                freq_str = f"Daily ({days_str})"

            self.tree.insert(
                "",
                tk.END,
                iid=idx,
                values=(
                    medicine.name,
                    medicine.dosage,
                    medicine.get_display_disease(),
                    meal_str,
                    duration_str,
                    freq_str,
                    status,
                ),
            )

    def _on_edit_click(self) -> None:
        """Handle edit button click."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                f"{APP_NAME} - No Selection", "Please select a medicine to edit."
            )
            return

        item_id = int(selection[0])
        medicine = self.medicine_manager.medicines[item_id]
        self.on_edit(medicine, item_id)

    def _delete_medicine(self) -> None:
        """Delete the selected medicine."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                f"{APP_NAME} - No Selection", "Please select a medicine to delete."
            )
            return

        item_id = int(selection[0])
        medicine = self.medicine_manager.medicines[item_id]

        if messagebox.askyesno(
            f"{APP_NAME} - Confirm Delete",
            f"Are you sure you want to delete '{medicine.name}'?\n\nThis action cannot be undone.",
        ):
            self.medicine_manager.remove_medicine(item_id)
            self.refresh()
            messagebox.showinfo(
                f"{APP_NAME} - Success", f"'{medicine.name}' has been deleted."
            )


class MedicineMainApplication(tk.Tk):
    """Main application class for Medicine Management."""

    def __init__(self, medicine_manager: MedicineManager, add_only: bool = False):
        """Initialize the medicine application."""
        super().__init__()
        self.logger = get_logger(__name__)
        self.medicine_manager = medicine_manager
        self.add_only = add_only

        self.title(f"{APP_NAME} - Medicine Management")
        self.geometry("800x600")
        self.minsize(600, 450)

        # Container for screens
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.current_frame: ttk.Frame | None = None

        if add_only:
            self.show_edit()
        else:
            self.show_list()

    def show_list(self) -> None:
        """Show the medicine list screen."""
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = MedicineListFrame(
            self.container,
            self.medicine_manager,
            on_add=self.show_edit,
            on_edit=self.show_edit,
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)
        self.title(f"{APP_NAME} - Medicine List")

    def show_edit(
        self, medicine: Medicine | None = None, index: int | None = None
    ) -> None:
        """Show the medicine edit/add screen."""
        if self.current_frame:
            self.current_frame.destroy()

        def on_save(new_medicine: Medicine) -> None:
            if index is not None:
                # Update existing
                self.medicine_manager.medicines[index] = new_medicine
                self.medicine_manager.save_medicines()
                messagebox.showinfo(
                    f"{APP_NAME} - Success", f"'{new_medicine.name}' updated."
                )
            else:
                # Add new
                self.medicine_manager.add_medicine(new_medicine)
                messagebox.showinfo(
                    f"{APP_NAME} - Success", f"'{new_medicine.name}' added."
                )

            if self.add_only:
                self.destroy()
            else:
                self.show_list()

        def on_cancel() -> None:
            if self.add_only:
                self.destroy()
            else:
                self.show_list()

        self.current_frame = MedicineEditFrame(
            self.container, medicine=medicine, on_save=on_save, on_cancel=on_cancel
        )
        # Don't expand vertically to avoid large empty space at bottom
        self.current_frame.pack(fill=tk.X, side=tk.TOP, anchor=tk.N)

        # Force window to shrink to fit content
        self.update_idletasks()
        self.geometry("")

        mode = "Edit" if medicine else "Add"
        self.title(f"{APP_NAME} - {mode} Medicine")


def run_medicine_ui(add_only: bool = False) -> None:
    """Entry point to run the medicine management UI."""
    logger = get_logger(__name__)
    logger.info("Starting medicine UI (add_only=%s)", add_only)
    try:
        logger.debug("Initializing MedicineManager")
        medicine_manager = MedicineManager()
        logger.debug("MedicineManager initialized")

        logger.debug("Initializing MedicineMainApplication")
        app = MedicineMainApplication(medicine_manager, add_only=add_only)
        logger.debug("MedicineMainApplication initialized, starting mainloop")
        app.mainloop()
        logger.info("Medicine UI mainloop exited")
    except Exception as e:
        logger.error("Failed to run medicine UI: %s", e, exc_info=True)
        messagebox.showerror(f"{APP_NAME} - Error", f"Failed to run medicine UI:\n{e}")
