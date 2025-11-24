'''import rpyc
from rpyc.utils.server import ThreadedServer

class MyTestService(rpyc.Service):
    def exposed_soma(self, a, b):
        return a + b



if __name__ == "__main__":
    server = ThreadedServer(MyTestService, port=18861)
    print("Servidor Iniciado")
    server.start()
    
'''