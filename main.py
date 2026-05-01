
#________ALL IMPORTS________
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition 
from kivy.core.window import Window
from database import setup


#________ALL SCREENS________

from screens.login import LoginScreen
from screens.signup import SignupScreen
from screens.dashboard import DashboardScreen
from screens.tasks import TasksScreen
from screens.new_task import NewTaskScreen
from screens.schedule import ScheduleScreen
from screens.events import EventsScreen
from screens.settings import SettingsScreen
from components.navbar import NavBar

#________ALL .KV FILES________
Builder.load_file("kv/navbar.kv")  #navbar is a common component used across multiple screens, so we load it separately
Builder.load_file('kv/login.kv')
Builder.load_file('kv/signup.kv')
Builder.load_file('kv/dashboard.kv')
Builder.load_file('kv/tasks.kv')
Builder.load_file('kv/new_task.kv')
Builder.load_file('kv/schedule.kv')
Builder.load_file('kv/events.kv')
Builder.load_file('kv/settings.kv')


#________SCREEN MANAGER________
class CollegeLifeManager(ScreenManager):
    pass

#APP CLASS
class CollegeLifeApp(MDApp):
    current_user = None #this will hold the current logged in user's data

    def build(self):
        setup()  #initialize the database
        Window.size = (420, 780)  #this is the window that we will work with

        from kivy.clock import Clock
        Clock.schedule_interval(self.check_notifications, 60)  #check for notifications every 60 seconds

        sm = CollegeLifeManager(transition = SlideTransition())  #creating an instance of the screen manager
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(TasksScreen(name='tasks'))
        sm.add_widget(NewTaskScreen(name='new_task'))
        sm.add_widget(ScheduleScreen(name='schedule'))
        sm.add_widget(EventsScreen(name='events'))
        sm.add_widget(SettingsScreen(name='settings'))

        sm.current = 'login'  #initial screen is login screen

        return sm
    
    #notification check function that runs every minute to check for upcoming tasks and send notifications
    def check_notifications(self, dt):
        from plyer import notification
        from datetime import datetime, timedelta
        import database as db

        if not self.current_user:
            return  # no user logged in, skip notification check
        
        settings = db.get_settings(self.current_user['id'])
        if not settings or not settings['notifications']:
            return  # notifications are disabled, skip check
        
        user_id = self.current_user['id']
        now = datetime.now()
        soon = (now + timedelta(minutes = 15)).strftime('%H:%M')
        today = now.strftime('%Y-%m-%d')

        tasks = db.get_tasks(user_id, 'today')

        for task in tasks:
            due_date = task[4]
            due_time = task[5]
            title    = task[2]
            status   = task[7]

            if due_date == today and due_time == soon and status != 'Completed':
                notification.notify(
                    title='CollegeLife Reminder',
                    message=f'"{title}" is due in 15 minutes!',
                    app_name='CollegeLife',
                    timeout=5
                )
    
#________RUN THE APP________
if __name__ == '__main__':
    CollegeLifeApp().run()