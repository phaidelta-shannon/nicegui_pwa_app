# main.py
from nicegui import ui

ui.label('Hello! This is a PWA-enabled NiceGUI app.')
ui.button('Click Me', on_click=lambda: ui.notify('It works!'))

ui.run(
    title='NiceGUI PWA App',
    dark=True,
    show=False  # Do not auto open browser when deploying
)