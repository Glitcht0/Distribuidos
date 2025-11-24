import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
import platform

class buscar_ip():
    def __init__(self):
        self.ips = self.escanear_rede()





    def ping(self, ip):
        sistema = platform.system().lower()
        comando = ["ping", "-c", "1", "-W", "1", ip] if sistema != "windows" else ["ping", "-n", "1", "-w", "1000", ip]

        try:
            saida = subprocess.check_output(comando, stderr=subprocess.DEVNULL, text=True)
            if "ttl" in saida.lower():  # Respondeu
                return ip
        except subprocess.CalledProcessError:
            pass
        return None
    
    def escanear_rede(self, base="192.168.0.", intervalo=(1, 254)):
       
        ativos = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            resultados = executor.map(self.ping, [f"{base}{i}" for i in range(intervalo[0], intervalo[1] + 1)])
        for ip in resultados:
            if ip:
                ativos.append(ip)
        return ativos