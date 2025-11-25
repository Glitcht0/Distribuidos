import socket
import threading
from kivy.clock import Clock
from src.logical_clock import update, get
from tinydb import TinyDB
from tinydb import TinyDB

class MessageServer:

    def __init__(self, app_reference, port=5000):
        """
        app_reference → referência para o aplicativo principal.
        Isso permite que o servidor avise a UI quando receber mensagens.

        port → porta onde o servidor vai ouvir (UDP).
        """

        self.app = app_reference
        try:
            # Abre o banco apenas para ler a config 
            with TinyDB("superbanco.json") as db:
                config_table = db.table("config")
                config = config_table.get(doc_id=1)

                if config and 'porta_in' in config:
                    self.port = int(config['porta_in'])
                    print(f"Servidor: Porta {self.port} carregada.")
                else:
                    self.port = 5000
                    print("Servidor: Porta padrão 5000 (config não encontrada).")

        except Exception as e:
            print(f"Erro ao ler config: {e}")
            self.port = 5000
        
        self.db = TinyDB("superbanco.json").table("messages") # Abre (ou cria) a tabela "messages" dentro do superbanco.json


    def start(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()


    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria o socket UDP

       
        sock.bind(("0.0.0.0", self.port))  # Escuta em todas interfaces (0.0.0.0) e na porta definida

        print(f"[SERVIDOR] Ouvindo na porta {self.port}...")


        # Loop eterno: sempre ouvindo mensagens
        while True:

            
            data, addr = sock.recvfrom(4096) # Espera uma mensagem (bloqueante, mas não trava a UI pois está em uma thread)

            text = data.decode()   # Decodifica de bytes para string
            ip = addr[0]           # Endereço IP do remetente
            

            # ------------------------------------------------------------------
            # Formato esperado da mensagem: "clock|texto"
            # Exemplo: "15|Oi, tudo bem?"
            #
            # Isso permite enviar o relógio lógico junto com a mensagem.
            # ------------------------------------------------------------------
            try:
                recv_clock, msg = text.split("|", 1)
                recv_clock = int(recv_clock)
            except:
                # Se estiver mal formatado, ainda funciona (só ignora o clock remoto)
                recv_clock = 0
                msg = text

            antigo = get()

            local_clock = update(recv_clock)

            novo = get()
            # Exemplo de uso
            print(f"\n\n{"\033[96m"}---- [SERVIDOR] Mensagem recebida de {ip}: {text} ----{"\033[0m"}")
            print(f"{"\033[93m"}clock recebido: {recv_clock}, clock local atualizado: {novo} e antigo: {antigo}{"\033[0m"}")


            
            local_db = TinyDB("superbanco.json").table("messages")

            local_db.insert({
                "chat": ip,
                "sender": "remote",
                "text": msg,
                "status": "received",
                "clock": local_clock
            })
            



            # ------------------------------------------------------------------
            # Aqui temos um detalhe CRUCIAL:
            #
            #    A UI DO KIVY SÓ PODE SER ALTERADA PELA MAIN THREAD.
            #
            # Mas o servidor roda em outra thread.
            #
            # Solução: usar Clock.schedule_once → envia a atualização
            # para a thread de UI processar.
            # ------------------------------------------------------------------
            Clock.schedule_once(
                lambda dt: self.app.on_new_message(ip, msg, local_clock)
            )



def send_message(ip, port, text):
    from src.logical_clock import increment, get
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    increment()
    clk = get()

    payload = f"{clk}|{text}"
    sock.sendto(payload.encode(), (ip, port))
