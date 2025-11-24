from tela_principal import MainScreen

from src.logical_clock import increment, update, get
from src.telas.chat import TelaChat

from kivy.utils import platform

from kivy.app import App
from kivy.core.window import Window

from tela_principal import MainScreen
from src.network import MessageServer   # ← seu servidor UDP

class LogicalClockApp(App):

    def build(self):
        # Passa referência do app para o MainScreen
        self.main = MainScreen(app_reference=self)

        # Inicia o servidor UDP em thread separada
        self.server = MessageServer(self)
        self.server.start()

        return self.main

    def on_new_message(self, ip, text, clock):
        # Procura tela que já está aberta para esse IP
        for screen in self.root_window.children:
            if isinstance(screen, TelaChat) and screen.nome_ip == ip:
                screen.receber_mensagem(text, clock)
                return

        print(f"[AVISO] Recebi mensagem de {ip}, mas nenhuma TelaChat está aberta.")






def main():
    print(f"{"\033[96m"} Software Cliente Servidor de mensagens{"\033[0m"}")

    print("Clock atual =", get())


    # Define tamanho da janela padrão para formato de celular (facilita testes em desktop)
    # Exemplo: 360x800 (largura x altura) — ajuste conforme desejar
    if platform == 'win' or platform == 'linux' or platform == 'macosx':
        Window.size = (360, 800)

    LogicalClockApp().run() 









if __name__ == "__main__":
    main()
    