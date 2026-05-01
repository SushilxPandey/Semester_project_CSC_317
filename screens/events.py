import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.utils import get_color_from_hex
import database as db

class EventsScreen(MDScreen):
    
    current_filter = "all"  # default filter is "all"

    def on_enter(self):
        self.filter_events("all")  # load all events when the screen is entered
    
    def search(self):
        search_text = self.ids.search_field.text.strip().lower()
        self.load_events(self.current_filter, search_text)
    
    def filter_events(self, filter_type):
        self.current_filter = filter_type
    
        # we reset all the the filter to grey
        self.ids.btn_all.md_bg_color = get_color_from_hex("#E0E0E0")
        self.ids.btn_upcoming.md_bg_color = get_color_from_hex("#E0E0E0")
        self.ids.btn_today.md_bg_color = get_color_from_hex("#E0E0E0")

        red = get_color_from_hex("#b71c1c")
        if filter_type == "all":
            self.ids.btn_all.md_bg_color = red
        elif filter_type == "upcoming":
            self.ids.btn_upcoming.md_bg_color = red
        elif filter_type == "today":
            self.ids.btn_today.md_bg_color = red
        
        self.load_events(filter_type, "")  # load events with the selected filter and no search text

    def load_events(self, filter_type, search_text):
        self.ids.event_list.clear_widgets() # clear existing events

        events = db.get_events(filter_type)

        #Apply search filter if search text is provided
        if search_text:
            events = [e for e in events if
                      search_text in e[1].lower() or         #title
                      search_text in (e[2] or "").lower()]   #description
        
        if not events:
            self.ids.event_list.add_widget(MDLabel(
                text = "No events found.",
                halign = "center",
                theme_text_color = "Custom",
                text_color = get_color_from_hex("#FF0000"),
                size_hint_y = None,
                height = "40dp"
            ))
            return
        
        for event in events:
            card = self.create_event_card(event)
            self.ids.event_list.add_widget(card)
        
    def create_event_card(self, event):
        
        card = MDCard(
            orientation = "vertical",
            size_hint_y = None,
            height = "120dp",
            radius= [10],
            padding = "12dp",
            elevation = 1,
            md_bg_color = get_color_from_hex("#FFFFFF")
        )

        #top row with title and date
        top_row = MDBoxLayout(
            orientation = "horizontal",
            size_hint_y = None,
            height = "24dp"
        )

        category_colors = {
            "Social": "#ff6f00",
            "Academic": "#1565c0"
        }
        cat_color = category_colors.get(event[6], "#E0E0E0")

        top_row.add_widget(MDLabel(
            text = f"{event[6]} - {event[4]}" ,   #category - time
            font_style = "Caption",
            theme_text_color = "Custom",
            text_color = get_color_from_hex(cat_color)
        ))
        top_row.add_widget(MDLabel(
            text = event[3],   #event date
            font_style = "Caption",
            halign = "right",
            theme_text_color = "Secondary"
        ))

        #title label
        title_label = MDLabel(
            text = event[1],   #event title
            font_style = "Body2",
            bold = True,
            size_hint_y = None,
            height = "24dp"
        )

        #bottom row with attending, description and location
        bottom_row = MDBoxLayout(
            orientation = "horizontal",
            size_hint_y = None,
            height = "32dp"
        )
        bottom_row.add_widget(MDLabel(
            text = f"{event[7]} Attending",   #attending count
            font_style = "Caption",
            theme_text_color = "Custom",
            text_color = get_color_from_hex(cat_color)
        ))
        bottom_row.add_widget(MDRaisedButton(
            text = "Add to Schedule",
            md_bg_color = get_color_from_hex("#FF0000"),
            size_hint_x = None,
            width = "130dp",
            height = "28dp",
            on_release = lambda x, e=event: self.add_to_schedule(e)
        ))
        card.add_widget(top_row)
        card.add_widget(title_label)
        card.add_widget(bottom_row)
        return card

    def add_to_schedule(self, event):
    
        # For now we will just show a message, but in a real app we would add this event to the user's schedule in the database
        print(f"Adding event '{event[1]}' to schedule...")


