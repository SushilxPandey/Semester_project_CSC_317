#______________________________IMPORTS___________________________
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#________ALL KIVY IMPORTS________
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivy.properties import StringProperty

#________NAVBAR COMPONENT________
class NavBar(MDBoxLayout):
    
    active_screen = StringProperty('dashboard')

    def go_to(self, screen_name):
        app = MDApp.get_running_app()
        app.root.current = screen_name
        