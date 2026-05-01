import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex
import database as db

class SettingsScreen(MDScreen):

    def on_enter(self):
        app = MDApp.get_running_app()
        user = app.current_user

        # Set user info
        words = user['full_name'].split()
        initials = words[0][0].upper() + words[-1][0].upper()
        self.ids.avatar_label.text = initials
        self.ids.name_label.text = user['full_name']
        self.ids.student_id_label.text = user['student_id']

        # Load saved settings
        settings = db.get_settings(user['id'])
        if settings:
            self.ids.theme_switch.active = (settings['theme'] == 'Dark')
            self.ids.font_btn.text = settings['font_size']
            self.ids.notif_switch.active = settings['notifications']
            self._apply_font_size(settings['font_size'])

    def toggle_theme(self, is_dark):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if is_dark else "Light"
        self.save_all_settings()

    def cycle_font_size(self):
        sizes = ["Small", "Medium", "Large"]
        current = self.ids.font_btn.text
        next_size = sizes[(sizes.index(current) + 1) % len(sizes)]
        self.ids.font_btn.text = next_size
        self.save_all_settings()
        self._apply_font_size(next_size)

    def _apply_font_size(self, size):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
    
        scale = {
            "Small":  0.85,
            "Medium": 1.0,
            "Large":  1.2
        }[size]

        # Update common font styles
        for style in ["Body1", "Body2", "Caption", "Subtitle1", "Subtitle2"]:
            app.theme_cls.font_styles[style][1] = int(
                app.theme_cls.font_styles[style][1] * scale
            )

    def save_notif_settings(self):
        self.save_all_settings()

    def save_all_settings(self):
        app = MDApp.get_running_app()
        user_id = app.current_user['id']
        theme = "Dark" if self.ids.theme_switch.active else "Light"
        db.save_settings(
            user_id,
            theme,
            self.ids.font_btn.text,
            self.ids.notif_switch.active
        )

    def reset_settings(self):
        # Reset all toggles to default
        self.ids.theme_switch.active = False    # False = Light mode
        self.ids.font_btn.text = "Medium"         # Medium
        self.ids.notif_switch.active = True    # Notifications on
        self.save_all_settings()

        # Reset app theme
        MDApp.get_running_app().theme_cls.theme_style = "Light"

    def logout(self):
        app = MDApp.get_running_app()
        app.current_user = None    # clear user
        self.manager.current = "login"  # go to login