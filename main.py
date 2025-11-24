from tela_principal import MainScreen

from kivy.app import App
from kivy.core.window import Window

class LogicalClockApp(App):
    def build(self):
        return MainScreen()





def main():
    print("Software Cliente Servidor de mensagens")

    # Define tamanho da janela padrão para formato de celular (facilita testes em desktop)
    # Exemplo: 360x800 (largura x altura) — ajuste conforme desejar
    try:
        Window.size = (360, 800)
    except Exception:
        pass

    LogicalClockApp().run() 









if __name__ == "__main__":
    main()
    
