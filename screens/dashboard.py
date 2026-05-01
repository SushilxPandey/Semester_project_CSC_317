import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database as db
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.progressbar import ProgressBar
from datetime import datetime

class DashboardScreen(MDScreen):
    
    def on_enter(self):
        app = MDApp.get_running_app()
        user = app.current_user
        user_id = user['id']

        #getting first name 
        name = user['full_name'].split()[0]  # assuming the name is stored in the second column of the user table

        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        #formatting the date
        date_str = datetime.now().strftime("%A, %B %d")  # e.g. "Monday, January 1"

        #updating the labels with the greeting and date
        self.ids.greeting_label.text = f"{greeting}, {name}!"
        self.ids.date_label.text = date_str

        #setting the avatar text to the user's initials
        words = user['full_name'].split()
        initials = words[0][0].upper() + words[-1][0].upper()  # get first letter of first and last name
        self.ids.avatar.text = initials

        #Progress bar for tasks
        total, done = db.get_task_stats(user['id'])
        if total > 0:
            self.ids.progress_bar.value = (done / total) * 100
        else:
            self.ids.progress_bar.value = 0

        self.ids.progress_label.text = f"{done}/{total} Tasks Completed"

        self.ids.task_due_label.text = str(total - done) 

        #---Agenda---(tasks for today)
        tasks_today = db.get_tasks(user_id, 'today')
        events_today = db.get_events('today')
        upcoming_events = db.get_events('upcoming')
        total_events = len(events_today) + len(upcoming_events)
        self.ids.events_label.text = str(total_events)
        
        if tasks_today or events_today:
            agenda_text = ""
            for task in tasks_today[:3]:
                agenda_text += f"• {task[2]} - {task[4]} {task[5]}\n"

            for event in events_today[:2]:
                agenda_text += f"• {event[1]} - {event[4]}\n"
            self.ids.agenda_label.text = agenda_text

        else:
            self.ids.agenda_label.text = "No Tasks For Today!!"
