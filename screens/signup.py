from kivymd.uix.screen import MDScreen
import database as db

class SignupScreen(MDScreen):
    def on_enter(self):
        from kivymd.app import MDApp
        MDApp.get_running_app().theme_cls.theme_style = "Light"  # Ensure we start with light theme

        self.ids.full_name_field.text = ""
        self.ids.email_field.text = ""
        self.ids.student_id_field.text = ""
        self.ids.password_field.text = ""
        self.ids.error_label.text = ""
    
    #function to go back to the login screen
    def go_back(self):
        self.manager.current = 'login'
    
    #function to handle the signup process
    def on_register(self):

        name               = self.ids.full_name_field.text.strip()
        email              = self.ids.email_field.text.strip()
        student_id         = self.ids.student_id_field.text.strip()
        password           = self.ids.password_field.text.strip()
        
        # Validating input
        if not name or not email or not student_id or not password:
            self.ids.error_label.text = "Please fill in all fields."
            return
        #checking if the email is legit
        if '@' not in email or '.' not in email:
            self.ids.error_label.text = "Please enter a valid email address."
            return
        
        #Validating password strength
        if len(password) < 8:
            self.ids.error_label.text = "Password must be at least 8 characters long."
            return
        
        #calling db to register the user
        success, message = db.register_user(name, email, student_id, password)
        if success:
            self.manager.current = 'login'  #go back to login screen after successful registration
        else:
            self.ids.error_label.text = message  #display error message if registration fails


    def toggle_password(self, is_active):
        self.ids.password_field.password = not is_active  #toggle the visibility of the password field