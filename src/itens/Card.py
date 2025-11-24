
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior # Para tornar o layout clicável
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from src.telas.chat import TelaChat



class IPCard(ButtonBehavior, BoxLayout):
    def __init__(self, ip_address, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical' # Organiza infos uma embaixo da outra (pode mudar para horizontal)
        self.size_hint_y = None       # Altura fixa para não esticar
        self.height = 90              # Altura do cartão (ajuste como quiser)
        self.padding = 15
        self.spacing = 5
        self.ip_address = ip_address

        self.Status = "Desconectado"  
        self.nome = "Desconhecido"

        # Fundo do cartão (Retângulo)
        with self.canvas.before:
            Color(*get_color_from_hex("#1F1F29")) # Cor do botão (um pouco mais clara que o fundo)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        # --- AQUI VOCÊ ADICIONA AS INFORMAÇÕES ---
        
        # 1. Nome (Destaque)
        # Mostrar o IP diretamente no cartão para facilitar identificação
        self.lbl_ip = Label(text=self.ip_address, bold=True, font_size=18, color=(1,1,1,1), size_hint_y=None, height=30, halign='left', valign='middle')
        self.lbl_ip.bind(size=self.lbl_ip.setter('text_size')) # Alinha texto à esquerda
        self.add_widget(self.lbl_ip)

        # 2. Espaço para info futura (ex: Status, Ping, Porta)
        self.lbl_status = Label(text=f"Status: {self.Status}        Ip:{self.ip_address}", font_size=14, color=(0.6, 0.6, 0.6, 1), size_hint_y=None, height=20, halign='left', valign='middle')
        self.lbl_status.bind(size=self.lbl_status.setter('text_size'))
        self.add_widget(self.lbl_status)



    




    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        # Ao abrir, passamos o IP mostrado no cartão para a tela de chat
        print(f"Abrindo detalhes do IP: {self.lbl_ip.text}")
        tela_detalhes = TelaChat(nome_ip=self.lbl_ip.text)
        tela_detalhes.open()