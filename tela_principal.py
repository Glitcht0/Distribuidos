from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView  # Importante para rolar
from kivy.uix.gridlayout import GridLayout  # Importante para organizar a lista
from kivy.uix.behaviors import ButtonBehavior # Para tornar o layout clicável
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from src.pop import AddIPPopup
from src.itens.Card import IPCard
from tinydb import TinyDB, Query



class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        # Chama o construtor da classe pai (BoxLayout)
        super().__init__(orientation='vertical', padding=[0, 0, 0, 0], spacing=10, **kwargs) # Define o layout vertical, com espaçamento e margens

        
        self.db = TinyDB('superbanco.json')
        
        self.logical_clock = 0
        self.ip_list = []

        self.elementos_Ui()
        self.carregar_ips_salvos()
        

        
     

        
        


    



    def open_add_ip_popup(self, *args):
        print(self.ip_list)
        popup = AddIPPopup(self)  # passa a tela principal pro popup
        popup.open()


    def carregar_ips_salvos(self):
        todos_ips = self.db.all()
        print(f"IPs carregados do banco: {todos_ips}")

        for item in todos_ips:
            self.adicionar_card_ip(item['ip'], salvar=False)

    def elementos_Ui(self):
        # 1. Header (Cabeçalho)
        self.header = BoxLayout(size_hint_y=None, height=60, padding=10)
        
        # Fundo da tela inteira
        with self.canvas.before:
            Color(*get_color_from_hex("#0E0E14"))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Fundo do Header
        with self.header.canvas.before:
            Color(*get_color_from_hex("#07070A"))
            self.header_rect = Rectangle(size=self.header.size, pos=self.header.pos)
        self.header.bind(size=self.update_header, pos=self.update_header)
        
        # Texto do Header
        self.header.add_widget(Label(text="Laport Chat", bold=True, font_size=20, color=(1,1,1,1)))
        
       
        btn_add = Button(text="+", size_hint=(None, 1), width=50, background_color=(0.2, 0.2, 0.2, 1))
        btn_add.bind(on_press=self.open_add_ip_popup)
        self.header.add_widget(btn_add)

        self.add_widget(self.header)

        # --- ÁREA DE ROLAGEM (SCROLLVIEW) ---
        self.scroll_view = ScrollView(size_hint=(1, 1)) # Ocupa o resto da tela
        
        # Container dos IPs (Cresce verticalmente)
        self.lista_ips_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=20)
        
        # MAGIA: Faz o layout crescer conforme adiciona widgets, permitindo o scroll
        self.lista_ips_layout.bind(minimum_height=self.lista_ips_layout.setter('height'))

        self.scroll_view.add_widget(self.lista_ips_layout)
        self.add_widget(self.scroll_view)




    # Função chamada para adicionar um novo IP na interface visual
    def adicionar_card_ip(self, ip,salvar=True):

        novo_card = IPCard(ip_address=ip)
        self.lista_ips_layout.add_widget(novo_card)

        if salvar:
            # Salva no banco de dados
            self.db.insert({'ip': ip})
            print(f"IP Salvo no banco: {ip}")





    def open_add_ip_popup(self, *args):
        popup = AddIPPopup(self)
        popup.open()

    def update_header(self, *args):
        self.header_rect.size = self.header.size
        self.header_rect.pos = self.header.pos

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
