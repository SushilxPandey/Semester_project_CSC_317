from kivymd.uix.screen import MDScreen
import database as db

class LoginScreen(MDScreen):
    def on_enter(self):

        from kivymd.app import MDApp
        MDApp.get_running_app().theme_cls.theme_style = "Light"  # Ensure we start with light theme

        self.ids.email_field.text = ""
        self.ids.password_field.text = ""
        self.ids.error_label.text = ""
        

    def on_login(self):
        
        email = self.ids.email_field.text.strip()
        password = self.ids.password_field.text.strip()

        if not email or not password:
            self.ids.error_label.text = "Please enter both email and password."
            self.ids.error_label.opacity = 1
            return

        #success is a boolean that indicates whether the login was successful, and result contains either the user data or an error message
        success, result = db.login_user(email, password)
        
        if success:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            app.current_user = result #store user data globally

            settings = db.get_settings(result['id'])
            if settings:
                 app.theme_cls.theme_style = settings['theme']
            
            self.manager.current = 'dashboard'
        
        else:
            self.ids.error_label.text = result
            self.ids.error_label.opacity = 1
        
    def go_to_signup(self):
        self.manager.current = 'signup'

    def toggle_password(self, is_active):
                self.ids.password_field.password = not is_active  #toggle the visibility of the password field