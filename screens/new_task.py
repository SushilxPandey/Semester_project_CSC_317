import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# All Kivy imports
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex

import database as db
from datetime import datetime

class NewTaskScreen(MDScreen):
    
    selected_priority = "Medium"  #this is default priority we sit back on .kv file

    def go_back(self):
        self.manager.current = 'tasks'
    
    def on_enter(self):
        self.ids.error_label.text = ""
    
    def toggle_am_pm(self):
        current = self.ids.am_pm_btn.text
        self.ids.am_pm_btn.text = "PM" if current == "AM" else "AM"

    
    def set_priority(self, priority):
        self.selected_priority = priority

        #now we reset all the options to grey
        self.ids.btn_low.md_bg_color        = get_color_from_hex("#aaaaaa")
        self.ids.btn_medium.md_bg_color     = get_color_from_hex("#aaaaaa")
        self.ids.btn_high.md_bg_color       = get_color_from_hex("#aaaaaa")

        #then highlight the selected with amber color
        amber = get_color_from_hex("#b37a05")
        if priority == "Low":
            self.ids.btn_low.md_bg_color = amber
        elif priority == "Medium":
            self.ids.btn_medium.md_bg_color = amber
        elif priority == "High":
            self.ids.btn_high.md_bg_color = amber

    def save_item(self):
        app = MDApp.get_running_app()
        user_id = app.current_user['id']

        title    = self.ids.task_body.text.strip()
        desc     = self.ids.description_box.text.strip()
        due_date = self.ids.due_date_field.text.strip()
        due_time = self.ids.due_time_field.text.strip()
        reminder = self.ids.reminder_checkbox.active

        #Validaiting Title
        if not title:
            self.ids.error_label.text = "Task Title is required."
            return
        
        #Validating the date format
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except:
                self.ids.error_label.text = "Date format must be YYYY-MM-DD"
                return
        
        hour_str = self.ids.due_time_field.text.strip()
        am_pm = self.ids.am_pm_btn.text

        if hour_str:
            hour = int(hour_str)
            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0
            due_time = f"{hour:02d}:00"
        else:  
            due_time = ""

        # Now we save it to the database
        db.add_task(user_id, title, desc, due_date, due_time, self.selected_priority, reminder)

        #clear the feilds after saving
        self.ids.task_body.text = ""
        self.ids.description_box.text = ""
        self.ids.due_date_field.text = ""
        self.ids.due_time_field.text = ""
        self.ids.error_label.text = ""
        self.ids.reminder_checkbox.active = False
        
        #go back to the tasks page
        self.manager.current = 'tasks'

