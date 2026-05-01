import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# these are kivy imports
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import get_color_from_hex
from datetime import datetime, timedelta
import database as db

TIME_SLOTS_12 = [
    "7 AM", "8 AM", "9 AM", "10 AM", "11 AM", 
    "12 PM", "1 PM", "2 PM", "3 PM", "4 PM",
    "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", 
    "10 PM", "11 PM", "12 AM"
]

TIME_SLOT_24 = [
    "07:00", "08:00", "09:00", "10:00", "11:00",
    "12:00", "13:00", "14:00", "15:00", "16:00",
    "17:00", "18:00", "19:00", "20:00", "21:00",
    "22:00", "23:00", "00:00"
    ]

PRIORITY_COLORS = {
    "High": ("#ff5252"),
    "Medium": ("#ffca28"),
    "Low": ("#4caf50")
}

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

class ScheduleScreen(MDScreen):
    
    week_offset = 0  #this will help us navigate between weeks

    def on_enter(self):
        self.build_schedule()

        #Syncing the scrolling
        self.ids.grid_scroll.bind(
            scroll_y=self._sync_scroll_y,
            scroll_x=self._sync_scroll_x
        )
    
    def _sync_scroll_y(self, instance, value):
        self.ids.time_scroll.scroll_y = value

    def _sync_scroll_x(self, instance, value):
        self.ids.header_scroll.scroll_x = value

    def prev_week(self):
        self.week_offset -= 1
        self.build_schedule()
    
    def next_week(self):
        self.week_offset += 1
        self.build_schedule()
    
    def get_nearest_hour(self, time_str):
        """This converts '12:01' to 12:00 to the nearest hour for easier matching with time slots"""
        if not time_str:
            return None
        try:
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1])

            if minute >= 30:
                hour = (hour + 1) % 24
            
            hour = hour % 24  # ensure hour wraps around at 24

            return f"{hour:02d}:00"
        except:
            return time_str  # if parsing fails, return original string

    
    def build_schedule(self):
        self.ids.schedule_grid.clear_widgets()
        self.ids.day_header.clear_widgets()
        self.ids.time_column.clear_widgets()

        app = MDApp.get_running_app()
        user_id = app.current_user['id']
        tasks = db.get_tasks(user_id, 'all')
        events = db.get_events('all')

        today = datetime.now()
        days_since_sunday = today.weekday() + 1
        if today.weekday() == 6:
            days_since_sunday = 0
        sunday = today - timedelta(days=days_since_sunday) + timedelta(weeks=self.week_offset)

        for i in range(7):
            day_date = sunday + timedelta(days=i)
            is_today = (day_date.date() == today.date())

            day_col = MDBoxLayout(orientation='vertical', size_hint_x=None, width="108dp")
            day_name = MDLabel(
                text=DAYS[i],
                halign='center',
                font_style="Caption",
                theme_text_color="Secondary"
            )
            day_num = MDLabel(
                text=str(day_date.day),
                halign='center',
                font_style="Caption",
                bold=is_today,
                theme_text_color="Custom",
                text_color=get_color_from_hex("#2255cc") if is_today else get_color_from_hex("#333333")
            )
            day_col.add_widget(day_name)
            day_col.add_widget(day_num)
            self.ids.day_header.add_widget(day_col)

        #  Step 2: Building the grid with time slots and tasks
        for idx, time_slot in enumerate(TIME_SLOTS_12):
            time_24 = TIME_SLOT_24[idx]

            # Time label — first cell of each row
            self.ids.time_column.add_widget(MDLabel(
                text=time_slot,
                font_style="Caption",
                theme_text_color="Secondary",
                halign='right',
                size_hint_y=None,
                height="56dp"
                
            ))

            # 7 day cells for this time slot
            for i in range(7):
                day_date = sunday + timedelta(days=i)
                date_str = day_date.strftime("%Y-%m-%d")

                # Check if task exists at this slot
                cell_task = None
                for task in tasks:
                    task_time_rounded = self.get_nearest_hour(task[5])  # round task time to nearest hour
                    if task[4] == date_str and task_time_rounded == time_24:
                        cell_task = task
                        break
                
                # Check if event exists at this slot
                cell_event = None
                for event in events:
                    event_time_rounded = self.get_nearest_hour(event[4])
                    if event[3] == date_str and event_time_rounded == time_24:
                        cell_event = event
                        break

                if cell_task:
                    is_done = cell_task[7] == 'Completed'

                    if is_done:
                        color = get_color_from_hex("#43a047")
                    

                    else:
                        color = get_color_from_hex(PRIORITY_COLORS.get(
                            cell_task[6], "#aaaaaa"))

                    card = MDCard(
                        md_bg_color=color,
                        radius=[6],
                        padding="4dp",
                        orientation="horizontal"
                    )

                    if is_done:
                        from kivymd.uix.button import MDIconButton
                        tick = MDIconButton(
                            icon="check-circle",
                            theme_icon_color="Custom",
                            icon_color=(1, 1, 1, 1),
                            size_hint=(None, None),
                            size=("24dp", "24dp")
                        )
                        card.add_widget(tick)

                    card.add_widget(MDLabel(
                        text=cell_task[2],
                        font_style="Caption",
                        theme_text_color="Custom",
                        text_color=(1, 1, 1, 1),
                        halign="center"
                    ))
                    self.ids.schedule_grid.add_widget(card)

                elif cell_event:
                    card = MDCard(
                        md_bg_color = get_color_from_hex("#7b1fa2"),
                        radius = [6],
                        padding = "4dp",
                    )
                    card.add_widget(MDLabel(
                        text = cell_event[1],
                        font_style = "Caption",
                        theme_text_color = "Custom",
                        text_color = (1, 1, 1, 1),
                        halign = "center"
                ))
                    self.ids.schedule_grid.add_widget(card)
    
                else:
                    self.ids.schedule_grid.add_widget(
                        MDBoxLayout(md_bg_color=(0.95, 0.95, 0.95, 1))
                    )
            