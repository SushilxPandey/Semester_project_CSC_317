# CollegeLife — Your Campus Companion
> Developed by **HubSeaTea** | CSC 317 Foundations of Software Development

---

## About

CollegeLife is a desktop application built to help college students manage their academic and social lives in one place. It combines task management, a weekly schedule, campus events, and smart reminders — all in a clean, intuitive interface.

---

## Team Members

| Name                   | Student ID |
|----------------------- |------------|
| Al Amin                | w10194269  |
| Hamza Muhammad Imran   | w10213865  |
| Muhammad Hashim Sohail | w10215965  |
| Sushil Pandey          | w10191662  |

---

## Features

- **Authentication** — Register and login securely with hashed passwords
- **Dashboard** — Daily greeting, task stats, today's agenda and events at a glance
- **Task Manager** — Add, filter, complete and delete tasks with priority levels and due times
- **Schedule** — Weekly grid view (Sun–Sat) with tasks and events displayed by time slot
- **Events** — Browse and search campus events with attendance counts
- **Notifications** — Desktop reminders 15 minutes before any task is due
- **Settings** — Toggle dark/light mode, adjust font size, enable/disable notifications

---

## Requirements

- Python 3.10+
- Kivy 2.3.1
- KivyMD 1.2.0
- plyer

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com && cd Semester_project_CSC_317
```

**2. Install dependencies**
```bash
python -m pip install kivy
python -m pip install kivymd
python -m pip install plyer
```

**3. Run the app**
```bash
python main.py
```

---

## First Time Setup

When you run the app for the first time:
- The database (`collegelife.db`) is created automatically
- Sample campus events are seeded into the events table
- Register a new account to get started

---

## Project Structure

```
collegelife/
├── main.py               # App entry point and notification system
├── database.py           # SQLite database and all CRUD operations
├── screens/
│   ├── login.py
│   ├── signup.py
│   ├── dashboard.py
│   ├── tasks.py
│   ├── new_task.py
│   ├── schedule.py
│   ├── events.py
│   └── settings.py
├── components/
│   └── navbar.py         # Reusable bottom navigation bar
├── kv/
│   ├── navbar.kv
│   ├── login.kv
│   ├── signup.kv
│   ├── dashboard.kv
│   ├── tasks.kv
│   ├── new_task.kv
│   ├── schedule.kv
│   ├── events.kv
│   └── settings.kv
└── .gitignore
```

---

## Known Limitations

- KivyMD 1.2.0 is used — some newer Material Design features require upgrading to 2.0.0
- Date/time picker is text-based (YYYY-MM-DD and hour + AM/PM) due to KivyMD version constraints
- Notifications require the `plyer` library and may not appear on all Windows configurations

---

## License

This project was developed for educational purposes as part of CSC 317.
