from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from tinydb.table import Document

class AddIPPopup(Popup):
    """Janela flutuante para adicionar um novo IP"""
    def __init__(self, main_screen, **kwargs):
        # Recebe a referência da tela principal
        super().__init__(title="Adicionar IP", size_hint=(0.8, 0.4), **kwargs)
        self.main_screen = main_screen  # Guarda a referência

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.input_ip = TextInput(hint_text="Digite o IP", multiline=False)
        layout.add_widget(self.input_ip)

        btn_add = Button(text="Adicionar", size_hint_y=None, height=40)
        btn_add.bind(on_press=self.add_ip)
        layout.add_widget(btn_add)

        self.content = layout

    def add_ip(self, *args):
        ip = self.input_ip.text.strip()
        if ip:
            # --- A CORREÇÃO ESTÁ AQUI ---
            # Em vez de apenas .append(ip), chamamos a função da tela principal
            # que cria o CARD visual e também adiciona na lista.
            self.main_screen.adicionar_card_ip(ip)
            
            print(f"IP Visual Adicionado: {ip}")
        self.dismiss()



class AddConnectionPopup(Popup):
    def __init__(self, main_screen, **kwargs):
        # 1. Cria a janela e os campos (NÃO lê os valores aqui)
        super().__init__(title="Configurar Portas", size_hint=(0.8, 0.6), **kwargs)
        self.main_screen = main_screen

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Input para porta de saída
        self.input_port_out = TextInput(hint_text="Porta de Saída (OUT)", multiline=False, input_filter='int')
        layout.add_widget(self.input_port_out)

        # Input para porta de entrada
        self.input_port_in = TextInput(hint_text="Porta de Entrada (IN)", multiline=False, input_filter='int')
        layout.add_widget(self.input_port_in)

        # Botão Salvar
        btn_save = Button(text="Salvar", size_hint_y=None, height=40)
        btn_save.bind(on_press=self.add_connection)
        layout.add_widget(btn_save)

        self.content = layout

    # 2. Esta função deve estar FORA do __init__ (observe a indentação à esquerda)
    def add_connection(self, *args):
        # Aqui sim lemos os valores, pois o usuário já digitou e clicou no botão
        porta_out = self.input_port_out.text.strip()
        porta_in = self.input_port_in.text.strip()

        if not porta_out or not porta_in:
            print("Preencha todas as portas!")
            return

        try:
            conexao = {
                "porta_out": int(porta_out),
                "porta_in": int(porta_in)
            }

            # Lógica corrigida para o TinyDB
            if self.main_screen.config_db.contains(doc_id=1):
                self.main_screen.config_db.update(conexao, doc_ids=[1])
            else:
                self.main_screen.config_db.insert(Document(conexao, doc_id=1))

            self.main_screen.porta_out = int(porta_out)
            self.main_screen.porta_in = int(porta_in)

            print("Portas configuradas:", conexao)
        except ValueError:
            print("Portas devem ser números inteiros!")
            return

        self.dismiss()