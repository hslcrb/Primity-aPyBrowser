import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView

class IMEManager(QObject):
    toggled = Signal(bool)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.active = False

    def toggle(self, state=None):
        if state is None:
            self.active = not self.active
        else:
            self.active = state
        
        self.apply_to_all_tabs()
        return self.active

    def apply_to_all_tabs(self):
        curr_layout = self.main_window.settings.value("kbd_layout", "dubeol")
        script = f"window.dispatchEvent(new CustomEvent('PRIMITY_TOGGLE_IME', {{ detail: {{ active: {str(self.active).lower()}, layout: '{curr_layout}' }} }}));"
        
        for i in range(self.main_window.tabs.count()):
            widget = self.main_window.tabs.widget(i)
            if isinstance(widget, QWebEngineView):
                widget.page().runJavaScript(script)

    def inject_script(self, browser_widget):
        ime_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'hangul_ime.js')
        if os.path.exists(ime_path):
            with open(ime_path, 'r', encoding='utf-8') as f:
                ime_js = f.read()
            browser_widget.loadFinished.connect(lambda _, b=browser_widget: b.page().runJavaScript(ime_js))
