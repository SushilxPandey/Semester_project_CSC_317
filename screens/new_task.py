import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#  Kivy / KivyMD imports 
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex

#  App logic imports 
import database as db
from datetime import datetime


class NewTaskScreen(MDScreen):

    # Called every time the screen is opened
    def on_enter(self):
        # Reset priority to default
        self.selected_priority = "Medium"
        self.ids.error_label.text = ""
        self.set_priority("Medium")

    # Navigate back to task list screen
    def go_back(self):
        self.manager.current = 'tasks'

    # Toggle AM ↔ PM when button is pressed
    def toggle_am_pm(self):
        current = self.ids.am_pm_btn.text
        self.ids.am_pm_btn.text = "PM" if current == "AM" else "AM"

    # Handle priority selection
    def set_priority(self, priority):
        # Store selected priority internally
        self.selected_priority = priority

        # Default (unselected) color
        default_color = get_color_from_hex("#aaaaaa")

        # Selected (highlight) color
        selected_color = get_color_from_hex("#b37a05")

        # Reset all buttons to default color
        self.ids.btn_low.md_bg_color = default_color
        self.ids.btn_medium.md_bg_color = default_color
        self.ids.btn_high.md_bg_color = default_color

        # Highlight the selected button
        if priority == "Low":
            self.ids.btn_low.md_bg_color = selected_color
        elif priority == "Medium":
            self.ids.btn_medium.md_bg_color = selected_color
        else:
            self.ids.btn_high.md_bg_color = selected_color

    # Main function: validates input and saves task
    def save_item(self):
        # Get current logged-in user
        app = MDApp.get_running_app()
        user_id = app.current_user['id']

        #  Collect input values 
        title = self.ids.task_body.text.strip()
        description = self.ids.description_box.text.strip()
        due_date = self.ids.due_date_field.text.strip()
        reminder = self.ids.reminder_checkbox.active

        #  Validate Title 
        if not title:
            self.ids.error_label.text = "Task Title is required."
            return

        #  Validate Date 
        # Expected format: YYYY-MM-DD
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except:
                self.ids.error_label.text = "Date format must be YYYY-MM-DD"
                return

        #  Validate & Convert Time 
        # User enters: HH:MM + AM/PM
        # We convert it into 24-hour format for storage
        due_time_input = self.ids.due_time_field.text.strip()
        am_pm = self.ids.am_pm_btn.text

        if due_time_input:
            try:
                # Parse 12-hour format (e.g., 09:30)
                dt = datetime.strptime(due_time_input, "%I:%M")

                hour = dt.hour
                minute = dt.minute

                # Convert to 24-hour format manually
                if am_pm == "PM" and hour != 12:
                    hour += 12
                elif am_pm == "AM" and hour == 12:
                    hour = 0

                # Final formatted time string (HH:MM)
                due_time = f"{hour:02d}:{minute:02d}"

            except:
                self.ids.error_label.text = "Time must be HH:MM"
                return
        else:
            # If no time entered, store empty string
            due_time = ""

        #  Save to Database 
        try:
            db.add_task(
                user_id,
                title,
                description,
                due_date,
                due_time,
                self.selected_priority,
                reminder
            )
        except Exception as e:
            # Catch database errors to prevent app crash
            self.ids.error_label.text = "Failed to save task."
            print("Database Error:", e)
            return

        #  Reset Form After Saving 
        self.ids.task_body.text = ""
        self.ids.description_box.text = ""
        self.ids.due_date_field.text = ""
        self.ids.due_time_field.text = ""
        self.ids.reminder_checkbox.active = False

        # Reset AM/PM toggle
        self.ids.am_pm_btn.text = "AM"

        # Reset priority selection
        self.set_priority("Medium")

        # Show success message briefly
        self.ids.error_label.text = "Task saved!"

        # Navigate back to task list
        self.manager.current = 'tasks'