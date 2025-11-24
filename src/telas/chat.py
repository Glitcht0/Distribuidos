from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from tinydb import TinyDB, Query
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex


class TelaChat(ModalView):
    def __init__(self, nome_ip = "desconhecido", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)  # Cobre 100% da tela
        self.auto_dismiss = False # Obriga a clicar no botão voltar para sair
        self.background_color = (0, 0, 0, 0) # Tira o fundo padrão cinza do modal

        self.nome_ip = nome_ip
        self.layout = BoxLayout(orientation='vertical') # Layout Principal da Tela
        

        header = BoxLayout(size_hint_y=None, height=60, padding=10)
        
        # Fundo do Header
        with header.canvas.before:
            Color(*get_color_from_hex("#07070A"))
            self.rect_header = Rectangle(size=header.size, pos=header.pos)
        
        header.bind(size=self._update_rect, pos=self._update_rect)

        # Botão Voltar (<)
        btn_voltar = Button(text="< Voltar", size_hint=(None, 1), width=80, background_normal='')
        btn_voltar.background_color = (0.2, 0.2, 0.2, 1)
        btn_voltar.bind(on_press=self.fechar_tela) # Chama a função de destruir
        
        # Título (Nome do IP)
        lbl_titulo = Label(text=f"Detalhes: {self.nome_ip}",bold=True,font_size=20, markup=False)

        
        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        
        self.layout.add_widget(header)
        
        
        conteudo = BoxLayout(orientation='vertical', padding=20) # --- 2. O CORPO DA TELA (Espaço vazio para infos futuras) ---
        
        # Fundo do Corpo
        with self.layout.canvas.before:
             Color(*get_color_from_hex("#0E0E14"))
             self.rect_bg = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_bg, pos=self._update_bg)

        # Área de mensagens: ScrollView com GridLayout vertical
        self.messages_scroll = ScrollView(size_hint=(1, 1))
        self.messages_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height')) # Faz o layout crescer para permitir o scroll
        self.messages_scroll.add_widget(self.messages_layout)


        # ========= Area de digitar mensagem ===========
        self.box_input = BoxLayout(size_hint_y=None, height=60, padding=5, spacing=5)

        self.txt_msg = TextInput(
            hint_text="Digite uma mensagem...",
            multiline=False,
            size_hint=(1, 1)
        )

        btn_enviar = Button(
            text="Enviar",
            size_hint=(None, 1),
            width=100
        )
        btn_enviar.bind(on_press=self.enviar_mensagem)

        self.box_input.add_widget(self.txt_msg)
        self.box_input.add_widget(btn_enviar)
        # ============================================


        conteudo.add_widget(self.messages_scroll)
        self.layout.add_widget(conteudo)
        self.layout.add_widget(self.box_input)

        
        try: # Inicializa DB e carrega mensagens desse chat
            self.db = TinyDB('superbanco.json')
        except Exception:
            self.db = None

        
        self._bubble_items = [] # Lista para controlar bolhas e permitir reflow quando a janela mudar de tamanho
        self.carregar_mensagens() # Recarrega mensagens (popula mensagens + _bubble_items)

         
        Window.bind(size=lambda *a: Clock.schedule_once(self._reflow_bubbles, 0)) # Reflow quando a janela for redimensionada
        self.add_widget(self.layout)  # Adiciona o layout completo na ModalView







    def enviar_mensagem(self, *args):
        texto = self.txt_msg.text.strip()
        if texto == "":
            return

        # Salva no banco
        messages_table = self.db.table('messages')
        messages_table.insert({
            'chat': self.nome_ip,
            'sender': 'me',
            'text': texto,
            'timestamp': Clock.get_time()
        })

        self.txt_msg.text = ""  # limpa o campo

        
        self.display_message(texto, sender="me") # Atualiza visualmente

        # Scroll automático para última mensagem
        Clock.schedule_once(lambda dt: setattr(
            self.messages_scroll, 'scroll_y', 0), 0.1)




    def carregar_mensagens(self):
        self.messages_layout.clear_widgets() # Limpa mensagens antigas
        self._bubble_items = []

        if not hasattr(self, 'db') or self.db is None:
            return

        messages_table = self.db.table('messages')
        q = Query()
        # Suporta algumas chaves possíveis para pesquisar (dependendo de como você editou o JSON)
        try:
            msgs = messages_table.search((q.chat == self.nome_ip) | (q.chat_ip == self.nome_ip) | (q.ip == self.nome_ip))
        except Exception:
            msgs = []

        
        try: 
            msgs = sorted(msgs, key=lambda m: m.get('timestamp', 0)) # Ordena por timestamp se disponível
        except Exception:
            pass

        for m in msgs:
            sender = m.get('sender', '')
            text = m.get('text', '')
            self.display_message(text, sender=sender) # Mostra o texto e passa o sender separado para alinhamento

        Clock.schedule_once(lambda dt: setattr(self.messages_scroll, 'scroll_y', 0), 0.1)







    def display_message(self, text, sender=None):
        is_me = False
        if sender:
            is_me = str(sender).lower() in ('me', 'eu', 'local')

        # Container horizontal que empurra a bolha para esquerda ou direita
        container = BoxLayout(
            size_hint_y=None,
            padding=5,
            height=0
        )

        max_bubble_width = int(Window.width * 0.7)

        # --- Bolha da mensagem ---
        bubble = BoxLayout(
            size_hint=(None, None),
            orientation='vertical',
            padding=(8, 6),
            spacing=3
        )

        # Cor da bolha
        with bubble.canvas.before:
            Color(*get_color_from_hex('#2EE6A6') if is_me else get_color_from_hex('#1F1F29'))
            bubble.bg_rect = Rectangle(size=bubble.size, pos=bubble.pos)

        def update_rect(*_):
            bubble.bg_rect.size = bubble.size
            bubble.bg_rect.pos = bubble.pos

        bubble.bind(size=update_rect, pos=update_rect)

        # --- Label do texto ---
        lbl = Label(
            text=text,
            size_hint=(None, None),
            halign="left",
            valign="middle",
            markup=False,   
            color=(0, 0, 0, 1) if is_me else (1, 1, 1, 1)
        )


        lbl.text_size = (max_bubble_width, None)

        # Permite wrap correto
        lbl.bind(
            texture_size=lambda *_: self._recalc_bubble(bubble, lbl, container, max_bubble_width)
        )

        bubble.add_widget(lbl)

        # --- Status (✓) ---
        status_text = "1" if is_me else "0"
        status_lbl = Label(
            text=status_text,
            size_hint=(1, None),
            height=15,
            halign='right',
            valign='middle',
            markup=False,   
            font_size=12,
            color=get_color_from_hex("#056EAAFF") if is_me else get_color_from_hex("#0493D4FF")
        )

        status_lbl.text_size = (max_bubble_width, None)
        bubble.add_widget(status_lbl)

        # --- Alinhamento ---
        spacer = Widget()

        if is_me:
            container.add_widget(spacer)
            container.add_widget(bubble)
        else:
            container.add_widget(bubble)
            container.add_widget(spacer)

        self.messages_layout.add_widget(container)

        # Salva para reflow
        self._bubble_items.append({'bubble': bubble, 'lbl': lbl, 'container': container})



    def _recalc_bubble(self, bubble, lbl, container, max_w):
        tw, th = lbl.texture_size

        lbl.width = min(tw, max_w)
        lbl.height = th

        pad_x = bubble.padding[0] * 2
        pad_y = bubble.padding[1] * 2

        bubble.width = min(tw, max_w) + pad_x
        bubble.height = max(36, th + pad_y + 15)  # 15 = status

        container.height = bubble.height + 10






    def _reflow_bubbles(self, dt=None):
        # Recalcula largura máxima e reaplica sizing para cada bolha existente
        if not hasattr(self, '_bubble_items'):
            return

        max_bubble_width = int(Window.width * 0.7)
        for item in self._bubble_items:
            bubble = item['bubble']
            lbl = item['lbl']
            container = item['container']

            
            lbl.text_size = (max_bubble_width, None) # Atualiza text_size para novo limite
            Clock.schedule_once(lambda dt, l=lbl, b=bubble, c=container: self._apply_texture_size(l, b, c, max_bubble_width), 0) # Força recalculo de texture



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

    def fechar_tela(self, *args):
        self.dismiss() # Isso fecha a tela e remove ela da visão


    
    def _update_rect(self, instance, value):
        if hasattr(self, 'rect_header'):
            self.rect_header.pos = instance.pos
            self.rect_header.size = instance.size

    def _update_bg(self, instance, value):
        self.rect_bg.pos = instance.pos
        self.rect_bg.size = instance.size

