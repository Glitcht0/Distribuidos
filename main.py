from tela_principal import MainScreen

from src.logical_clock import increment, update, get


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
        """
        Esse método é chamado sempre que o servidor UDP
        recebe uma mensagem de algum outro dispositivo.
        
        Ele apenas repassa o evento para a tela principal.
        """
        self.main.route_message(ip, text, clock)





def main():
    print("Software Cliente Servidor de mensagens")
    print("Clock atual =", get())


    # Define tamanho da janela padrão para formato de celular (facilita testes em desktop)
    # Exemplo: 360x800 (largura x altura) — ajuste conforme desejar
    try:
        Window.size = (360, 800)
    except Exception:
        pass

    LogicalClockApp().run() 









if __name__ == "__main__":
    main()
    
