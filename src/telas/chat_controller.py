from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.clock import Clock
from tinydb import TinyDB, Query


class ChatController:
    """Controller que encapsula a lógica de carregar mensagens, criar bolhas
    e reagir ao redimensionamento da janela. Mantém referências aos widgets
    `messages_layout` (GridLayout) e `messages_scroll` (ScrollView).
    """

    def __init__(self, messages_layout, messages_scroll, nome_ip, db_path='superbanco.json'):
        self.messages_layout = messages_layout
        self.messages_scroll = messages_scroll
        self.nome_ip = nome_ip
        self.db_path = db_path
        self._bubble_items = []

        try:
            self.db = TinyDB(self.db_path)
        except Exception:
            self.db = None

        # Reflow ao redimensionar
        Window.bind(size=lambda *a: Clock.schedule_once(self._reflow_bubbles, 0))

    def carregar_mensagens(self):
        self.messages_layout.clear_widgets()
        self._bubble_items = []

        if not self.db:
            return

        messages_table = self.db.table('messages')
        q = Query()
        try:
            msgs = messages_table.search((q.chat == self.nome_ip) | (q.chat_ip == self.nome_ip) | (q.ip == self.nome_ip))
        except Exception:
            msgs = []

        try:
            msgs = sorted(msgs, key=lambda m: m.get('timestamp', 0))
        except Exception:
            pass

        for m in msgs:
            sender = m.get('sender', '')
            text = m.get('text', '')
            self.display_message(text, sender=sender)

    def display_message(self, text, sender=None):
        is_me = False
        if sender:
            is_me = str(sender).lower() in ('me', 'eu', 'local')

        container = BoxLayout(size_hint_y=None, padding=5)
        max_bubble_width = int(Window.width * 0.7)

        bubble = BoxLayout(size_hint=(None, None), padding=(8, 6))
        with bubble.canvas.before:
            if is_me:
                Color(*get_color_from_hex('#2EE6A6'))
            else:
                Color(*get_color_from_hex('#1F1F29'))
            bubble.bg_rect = Rectangle(size=bubble.size, pos=bubble.pos)

        def _update_bubble_rect(instance, value):
            bubble.bg_rect.pos = instance.pos
            bubble.bg_rect.size = instance.size
        bubble.bind(pos=_update_bubble_rect, size=_update_bubble_rect)

        lbl = Label(text=text, size_hint=(None, None), halign='left', valign='middle', color=(0,0,0,1) if is_me else (1,1,1,1))
        lbl.text_size = (max_bubble_width, None)

        def _resize_from_texture(dt=None):
            tw, th = lbl.texture_size
            padding_x = bubble.padding[0] * 2 if isinstance(bubble.padding, (list, tuple)) else bubble.padding * 2
            new_width = min(tw, max_bubble_width) + padding_x
            new_height = th + (bubble.padding[1] * 2 if isinstance(bubble.padding, (list, tuple)) else bubble.padding * 2)
            lbl.width = min(tw, max_bubble_width)
            lbl.height = th
            bubble.width = new_width
            bubble.height = max(36, new_height)
            container.height = bubble.height + (container.padding[1] * 2 if isinstance(container.padding, (list, tuple)) else container.padding * 2)

        Clock.schedule_once(_resize_from_texture, 0)
        bubble.add_widget(lbl)

        spacer = Widget()
        if is_me:
            container.add_widget(spacer)
            container.add_widget(bubble)
        else:
            container.add_widget(bubble)
            container.add_widget(spacer)

        Clock.schedule_once(lambda dt: setattr(container, 'height', bubble.height), 0)

        self._bubble_items.append({'bubble': bubble, 'lbl': lbl, 'container': container, 'is_me': is_me})
        self.messages_layout.add_widget(container)

    def _reflow_bubbles(self, dt=None):
        if not hasattr(self, '_bubble_items'):
            return

        max_bubble_width = int(Window.width * 0.7)
        for item in self._bubble_items:
            bubble = item['bubble']
            lbl = item['lbl']
            container = item['container']
            lbl.text_size = (max_bubble_width, None)
            Clock.schedule_once(lambda dt, l=lbl, b=bubble, c=container: self._apply_texture_size(l, b, c, max_bubble_width), 0)

    def _apply_texture_size(self, lbl, bubble, container, max_bubble_width):
        tw, th = lbl.texture_size
        padding_x = bubble.padding[0] * 2 if isinstance(bubble.padding, (list, tuple)) else bubble.padding * 2
        padding_y = bubble.padding[1] * 2 if isinstance(bubble.padding, (list, tuple)) else bubble.padding * 2
        new_width = min(tw, max_bubble_width) + padding_x
        new_height = th + padding_y
        lbl.width = min(tw, max_bubble_width)
        lbl.height = th
        bubble.width = new_width
        bubble.height = max(36, new_height)
        container.height = bubble.height + (container.padding[1] * 2 if isinstance(container.padding, (list, tuple)) else container.padding * 2)
