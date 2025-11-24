from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup

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