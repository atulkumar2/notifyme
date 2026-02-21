"""
Medicine management UI dialog for the NotifyMe application.

This module provides a tkinter-based GUI for managing medicines,
including adding, editing, and deleting medicine entries.
"""

import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable

from notifyme_app.constants import (
    ALL_MEDICINE_TIMES,
    COMMON_DISEASES,
    MedicineTimeLabels,
)
from notifyme_app.medicine import Medicine, MedicineManager


class MedicineDialog(tk.Toplevel):
    """Dialog for adding or editing a medicine entry."""

    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        medicine: Medicine | None = None,
        on_save: Callable[[Medicine], None] | None = None,
    ):
        """Initialize the medicine dialog.

        Args:
            parent: Parent window
            medicine: Medicine to edit (None for new medicine)
            on_save: Callback when medicine is saved
        """
        super().__init__(parent)
        self.title("Medicine Details")
        self.geometry("500x650")
        self.resizable(False, False)
        self.medicine = medicine
        self.on_save = on_save
        self.result = None

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        if medicine:
            self._populate_fields(medicine)

    def _create_widgets(self) -> None:
        """Create the dialog widgets."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Medicine Name
        ttk.Label(main_frame, text="Medicine Name:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # Dosage
        ttk.Label(main_frame, text="Dosage:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dosage_entry = ttk.Entry(main_frame, width=40)
        self.dosage_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        ttk.Label(
            main_frame, text="(e.g., '1 tablet', '5ml', '500mg')", font=("Arial", 9)
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Disease Type
        ttk.Label(main_frame, text="Disease Type:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.disease_var = tk.StringVar()
        disease_combo = ttk.Combobox(
            main_frame,
            textvariable=self.disease_var,
            values=COMMON_DISEASES,
            state="readonly",
            width=37,
        )
        disease_combo.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # Custom Disease (shown when "Other" is selected)
        ttk.Label(main_frame, text="Custom Disease:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.custom_disease_entry = ttk.Entry(main_frame, width=40)
        self.custom_disease_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # Binding to show/hide custom disease
        disease_combo.bind("<<ComboboxSelected>>", self._on_disease_selected)

        # Meal Times
        ttk.Label(main_frame, text="Take with meals:").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=(15, 5)
        )

        self.meal_time_vars = {}
        for idx, meal_time in enumerate(ALL_MEDICINE_TIMES):
            meal_label = MedicineTimeLabels.get(meal_time, meal_time.title())
            var = tk.BooleanVar()
            self.meal_time_vars[meal_time] = var
            check = ttk.Checkbutton(main_frame, text=meal_label, variable=var)
            check.grid(row=6 + idx, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Duration
        ttk.Label(main_frame, text="Duration:").grid(
            row=9, column=0, sticky=tk.W, pady=(15, 5)
        )
        ttk.Label(main_frame, text="Days (0 = continuous):").grid(
            row=10, column=0, sticky=tk.W, pady=5
        )
        self.duration_spinbox = ttk.Spinbox(main_frame, from_=0, to=3650, width=10)
        self.duration_spinbox.set(0)
        self.duration_spinbox.grid(row=10, column=1, sticky=tk.W, pady=5)

        # Start Date
        ttk.Label(main_frame, text="Start Date:").grid(
            row=11, column=0, sticky=tk.W, pady=5
        )
        self.date_entry = ttk.Entry(main_frame, width=40)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=11, column=1, sticky=tk.EW, pady=5)
        ttk.Label(main_frame, text="(YYYY-MM-DD)", font=("Arial", 9)).grid(
            row=12, column=0, columnspan=2, sticky=tk.W, pady=(0, 10)
        )

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, columnspan=2, sticky=tk.EW, pady=(20, 0))

        ttk.Button(button_frame, text="Save", command=self._save).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

        # Configure grid weight
        main_frame.columnconfigure(1, weight=1)

    def _on_disease_selected(self, _event=None) -> None:
        """Handle disease selection change."""
        disease = self.disease_var.get()
        if disease == "Other":
            self.custom_disease_entry.config(state=tk.NORMAL)
            self.custom_disease_entry.focus()
        else:
            self.custom_disease_entry.config(state=tk.DISABLED)
            self.custom_disease_entry.delete(0, tk.END)

    def _populate_fields(self, medicine: Medicine) -> None:
        """Populate fields with existing medicine data."""
        self.name_entry.insert(0, medicine.name)
        self.dosage_entry.insert(0, medicine.dosage)
        self.disease_var.set(medicine.disease)

        if medicine.disease == "Other" and medicine.custom_disease:
            self.custom_disease_entry.config(state=tk.NORMAL)
            self.custom_disease_entry.insert(0, medicine.custom_disease)
        else:
            self.custom_disease_entry.config(state=tk.DISABLED)

        for meal_time, var in self.meal_time_vars.items():
            var.set(meal_time in medicine.meal_times)

        self.duration_spinbox.delete(0, tk.END)
        self.duration_spinbox.insert(0, str(medicine.duration_days))
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, medicine.start_date)

    def _save(self) -> None:
        """Save and validate the medicine entry."""
        # Validate inputs
        name = self.name_entry.get().strip()
        dosage = self.dosage_entry.get().strip()
        disease = self.disease_var.get()
        custom_disease = (
            self.custom_disease_entry.get().strip() if disease == "Other" else None
        )

        if not name:
            messagebox.showwarning("Missing Field", "Please enter a medicine name.")
            return

        if not dosage:
            messagebox.showwarning("Missing Field", "Please enter the dosage.")
            return

        if not disease:
            messagebox.showwarning("Missing Field", "Please select a disease type.")
            return

        if disease == "Other" and not custom_disease:
            messagebox.showwarning(
                "Missing Field", "Please enter a custom disease name."
            )
            return

        # Get selected meal times
        meal_times = [mt for mt, var in self.meal_time_vars.items() if var.get()]
        if not meal_times:
            messagebox.showwarning(
                "Missing Selection", "Please select at least one meal time."
            )
            return

        # Validate date
        try:
            datetime.strptime(self.date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD format.")
            return

        # Validate duration
        try:
            duration = int(self.duration_spinbox.get())
            if duration < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Duration", "Duration must be a positive number."
            )
            return

        # Create medicine object
        medicine = Medicine(
            name=name,
            dosage=dosage,
            disease=disease,
            meal_times=meal_times,
            duration_days=duration,
            start_date=self.date_entry.get(),
            custom_disease=custom_disease,
        )

        self.result = medicine
        if self.on_save:
            self.on_save(medicine)

        self.destroy()


class MedicineManagementWindow(tk.Toplevel):
    """Main window for managing medicines."""

    def __init__(self, parent: tk.Tk | tk.Toplevel, medicine_manager: MedicineManager):
        """Initialize the medicine management window.

        Args:
            parent: Parent window
            medicine_manager: MedicineManager instance
        """
        super().__init__(parent)
        self.title("Medicine Management")
        self.geometry("800x500")
        self.resizable(True, True)
        self.medicine_manager = medicine_manager

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._refresh_list()

    def _create_widgets(self) -> None:
        """Create the window widgets."""
        # Top frame for buttons
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill=tk.X, side=tk.TOP)

        ttk.Button(
            button_frame, text="➕ Add Medicine", command=self._add_medicine
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Edit", command=self._edit_medicine).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="🗑️ Delete", command=self._delete_medicine).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # Treeview for medicines
        tree_frame = ttk.Frame(self, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview
        columns = ("Name", "Dosage", "Disease", "Meals", "Duration", "Status")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, height=15, show="headings"
        )

        # Define headings and widths
        self.tree.heading("Name", text="Medicine Name")
        self.tree.heading("Dosage", text="Dosage")
        self.tree.heading("Disease", text="Disease/Condition")
        self.tree.heading("Meals", text="Meal Times")
        self.tree.heading("Duration", text="Duration")
        self.tree.heading("Status", text="Status")

        self.tree.column("Name", width=120)
        self.tree.column("Dosage", width=80)
        self.tree.column("Disease", width=120)
        self.tree.column("Meals", width=100)
        self.tree.column("Duration", width=80)
        self.tree.column("Status", width=80)

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

    def _refresh_list(self) -> None:
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
                    status,
                ),
            )

    def _add_medicine(self) -> None:
        """Open dialog to add a new medicine."""
        dialog = MedicineDialog(self, on_save=self._on_medicine_saved)
        self.wait_window(dialog)

    def _edit_medicine(self) -> None:
        """Edit the selected medicine."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a medicine to edit.")
            return

        item_id = selection[0]
        medicine = self.medicine_manager.medicines[int(item_id)]

        dialog = MedicineDialog(
            self, medicine=medicine, on_save=self._on_medicine_saved
        )
        self.wait_window(dialog)

    def _delete_medicine(self) -> None:
        """Delete the selected medicine."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection", "Please select a medicine to delete."
            )
            return

        item_id = selection[0]
        medicine = self.medicine_manager.medicines[int(item_id)]

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{medicine.name}'?\n\nThis action cannot be undone.",
        ):
            self.medicine_manager.remove_medicine(int(item_id))
            self._refresh_list()
            messagebox.showinfo("Success", f"'{medicine.name}' has been deleted.")

    def _on_medicine_saved(self, medicine: Medicine) -> None:
        """Handle medicine save event."""
        selection = self.tree.selection()

        if selection:
            # Editing existing medicine
            item_id = selection[0]
            existing = self.medicine_manager.medicines[int(item_id)]
            idx = self.medicine_manager.medicines.index(existing)
            self.medicine_manager.medicines[idx] = medicine
            messagebox.showinfo("Success", f"'{medicine.name}' has been updated.")
        else:
            # Adding new medicine
            self.medicine_manager.add_medicine(medicine)
            messagebox.showinfo("Success", f"'{medicine.name}' has been added.")

        self._refresh_list()
        logging.info("Medicine saved: %s", medicine.name)


def open_medicine_management(
    parent: tk.Tk | tk.Toplevel, medicine_manager: MedicineManager
) -> None:
    """Open the medicine management window.

    Args:
        parent: Parent window
        medicine_manager: MedicineManager instance
    """
    try:
        MedicineManagementWindow(parent, medicine_manager)
        logging.info("Opened medicine management window")
    except Exception as e:
        logging.error("Failed to open medicine management: %s", e)
        messagebox.showerror("Error", f"Failed to open medicine management:\n{e}")
