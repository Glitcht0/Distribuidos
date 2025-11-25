import sys
import os
from tinydb import TinyDB

def obter_caminho_real(arquivo):
    """
    Retorna o caminho correto:
    - Se for script .py: retorna a pasta do arquivo.
    - Se for .exe (frozen): retorna a pasta onde o executável está.
    """
    if getattr(sys, 'frozen', False):
        # Se empacotado como executável, coloque o DB ao lado do executável
        pasta_base = os.path.dirname(sys.executable)
    else:
        # Se rodando como script, queremos o diretório raiz do projeto
        # (assumimos que este arquivo está em <projeto>/src/itens/)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        # Sobe dois níveis para chegar no diretório do projeto (onde está main.py)
        pasta_base = os.path.abspath(os.path.join(this_dir, '..', '..'))

    return os.path.join(pasta_base, arquivo)