import socket
import threading
from kivy.clock import Clock
from src.logical_clock import update
from tinydb import TinyDB


class MessageServer:

    def __init__(self, app_reference, port=5397):
        """
        app_reference → referência para o aplicativo principal.
        Isso permite que o servidor avise a UI quando receber mensagens.

        port → porta onde o servidor vai ouvir (UDP).
        """

        self.app = app_reference
        self.port = port

        # Abre (ou cria) a tabela "messages" dentro do superbanco.json
        self.db = TinyDB("superbanco.json").table("messages")


    def start(self):
        """
        Inicia o servidor em uma thread separada.

        IMPORTANTE:
        - Threads são necessárias porque o servidor não pode travar a UI.
        - daemon=True faz a thread fechar automaticamente quando o app fechar.
        """

        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()


    def listen(self):
        """
        Loop infinito que fica ouvindo mensagens UDP de qualquer dispositivo na rede.

        Cada celular roda um servidor desses, assim todos podem enviar mensagens
        diretamente uns para os outros.
        """

        # Cria o socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Escuta em todas interfaces (0.0.0.0) e na porta definida
        sock.bind(("0.0.0.0", self.port))

        print(f"[SERVIDOR] Ouvindo na porta {self.port}...")


        # Loop eterno: sempre ouvindo mensagens
        while True:

            # Espera uma mensagem (bloqueante, mas não trava a UI pois está em uma thread)
            data, addr = sock.recvfrom(4096)

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


            # ------------------------------------------------------------------
            # Atualiza o relógio lógico local
            # usando o relógio recebido:
            #
            #   clock = max(local, recebido) + 1
            #
            # Isso garante ordenação de Lamport
            # ------------------------------------------------------------------
            local_clock = update(recv_clock)


            # ------------------------------------------------------------------
            # Salva a mensagem no banco
            # ------------------------------------------------------------------
            self.db.insert({
                "chat": ip,          # identifica a conversa pelo IP do outro lado
                "sender": "remote",  # mensagem recebida
                "text": msg,
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
