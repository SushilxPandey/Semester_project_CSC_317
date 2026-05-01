import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
import database as db

class TasksScreen(MDScreen):
    
    def on_enter(self):
        self.filter_tasks("all")  # Load all tasks when the screen is entered
    
    def go_to_new_task(self):
        self.manager.current = 'new_task'

    def filter_tasks(self, filter_type):

        #reset all buttons to grey
        self.ids.btn_all.md_bg_color = get_color_from_hex("#888888")
        self.ids.btn_today.md_bg_color = get_color_from_hex("#888888")
        self.ids.btn_week.md_bg_color = get_color_from_hex("#888888")
        self.ids.btn_done.md_bg_color = get_color_from_hex("#888888")

        #highlight the active button
        active_color = get_color_from_hex("#b37a05")
        if filter_type == "all":
            self.ids.btn_all.md_bg_color = active_color
        elif filter_type == "today":
            self.ids.btn_today.md_bg_color = active_color
        elif filter_type == "week":
            self.ids.btn_week.md_bg_color = active_color
        elif filter_type == "done":
            self.ids.btn_done.md_bg_color = active_color

        self.load_tasks(filter_type)

    def load_tasks(self, filter_type):
        
        self.ids.task_list.clear_widgets()  # Clear existing tasks

        app = MDApp.get_running_app()
        user_id = app.current_user['id']

        if filter_type == "all":
            overdue = db.get_overdue_tasks(user_id)
            if overdue:
                self.ids.task_list.add_widget(MDLabel(
                    text = "Overdue Tasks",
                    font_style = "Caption",
                    bold = True,
                    theme_text_color = "Custom",
                    text_color = (1, 0, 0, 1),  # Red color
                    size_hint_y = None,
                    height = "24dp"
                ))
                for task in overdue:
                    card = self.create_task_card(task, overdue=True)
                    self.ids.task_list.add_widget(card)

                from kivymd.uix.boxlayout import MDBoxLayout
                self.ids.task_list.add_widget(MDBoxLayout(
                    size_hint_y = None,
                    height = "1dp",
                    md_bg_color = get_color_from_hex("#CCCCCC")
                ))

        tasks = db.get_tasks(user_id, filter_type)

        if filter_type == "all":
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            tasks = [t for t in tasks if not(
                t[4] and t[4] < today and t[7] != 'Completed'  # due_date < today and not completed
            )]

        # If no tasks are found, display a message
        if not tasks:
            self.ids.task_list.add_widget(
                MDLabel(
                    text="No tasks found.", 
                    halign="center", 
                    size_hint_y = None,
                    height = "40dp"
                    )
            )
            return

        #Cards for each task
        for task in tasks:
            task_card = self.create_task_card(task)
            self.ids.task_list.add_widget(task_card)
        
    
    def create_task_card(self, task, overdue=False):

        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivy.metrics import dp

        is_done = task[7] == 'Completed' 

        card = MDCard(
            orientation='horizontal',
            size_hint_y = None,
            height = '64dp',
            radius = [10],
            padding = '10dp',
            spacing = '10dp',
            elevation = 1,
            md_bg_color =get_color_from_hex("#FF7575") if  overdue else (1, 1, 1, 1),
            on_release = lambda x, t=task: self.show_task_details(t)
        )

        #checkbox to mark task as done
        from kivymd.uix.button import MDIconButton
        check = MDIconButton(
            icon = 'check-circle' if is_done else 'checkbox-blank-circle-outline',
            theme_icon_color = 'Custom',
            icon_color = (0.2, 0.7, 0.4, 1) if is_done else (0.8, 0.8, 0.8, 1),
            size_hint = (None, None),
            size = ('40dp', '40dp'),
            on_release = lambda x, tid = task[0], done=is_done: self.toggle_task_done(tid, done)
        )

        #text column
        text_col = MDBoxLayout(orientation='vertical')
        title = MDLabel(
            text = task[2],  # Assuming the 'title' field is at index 2
            font_style = 'Body2',
            bold = not is_done  # Bold if not done
        )

        subtitle = MDLabel(
            text=f"Due: {task[4]} {task[5]} · {task[6]}",  # due_date · priority
            font_style='Caption',
            theme_text_color='Secondary'
        )
 
        text_col.add_widget(title)
        text_col.add_widget(subtitle)

        card.add_widget(check)
        card.add_widget(text_col)

        return card
    
    def show_task_details(self, task):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.boxlayout import MDBoxLayout

        content = MDBoxLayout(
            orientation = "vertical",
            spacing = "8dp",
            size_hint_y = None,
            height = "120dp"
        )
        content.add_widget(MDLabel(
            text = f"Due: {task[4]} at {task[5]}",
            font_style = "Body2",
        ))
        content.add_widget(MDLabel(
            text = f"Priority: {task[6]}",
            font_style = "Body2",
        ))
        content.add_widget(MDLabel(
            text = f"Description: \n{task[3] if task[3] else 'No description provided.'}",
            font_style = "Caption",
            theme_text_color = "Secondary"
        ))

        self.dialog = MDDialog(
            title = task[2],
            type = "custom",
            content_cls = content,
            buttons = [
                MDFlatButton(
                    text = "Close",
                    on_release = lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def toggle_task_done(self, task_id, is_done):
        if is_done:
            db.mark_task_pending(task_id)
        else:
            db.mark_task_done(task_id)
        self.load_tasks("all")
    
