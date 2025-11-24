import json
import shutil
from pathlib import Path


def try_fix_string(s: str) -> str:
    """Tenta corrigir uma string com dupla-encoding comum (UTF-8 lido como latin-1).

    Estratégia:
    - tenta decodificar como se a string tivesse sido decodificada incorretamente: s -> bytes via
      latin-1 -> decodifica bytes como utf-8.
    - se decodificação falhar, retorna a string original.
    - usa heurística simples: se o resultado contém caracteres acima de ASCII e não contém o
      caracter de substituição pesado, escolhe o corrigido.
    """
    try:
        fixed = s.encode('latin-1').decode('utf-8')
    except Exception:
        return s

    # heurística: prefere o que contém mais caracteres não-ASCII
    orig_non_ascii = sum(1 for c in s if ord(c) > 127)
    fixed_non_ascii = sum(1 for c in fixed if ord(c) > 127)
    if fixed_non_ascii >= orig_non_ascii:
        return fixed
    return s


def fix_obj(obj):
    if isinstance(obj, dict):
        return {k: fix_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fix_obj(v) for v in obj]
    if isinstance(obj, str):
        return try_fix_string(obj)
    return obj


def main():
    path = Path('superbanco.json')
    if not path.exists():
        print('Arquivo superbanco.json não encontrado no diretório atual.')
        return

    backup = path.with_suffix('.backup.json')
    print(f'Criando backup em: {backup}')
    shutil.copy2(path, backup)

    with path.open('r', encoding='utf-8', errors='replace') as f:
        data = json.load(f)

    fixed = fix_obj(data)

    # Regrava como UTF-8, garantindo que acentos sejam preservados
    with path.open('w', encoding='utf-8') as f:
        json.dump(fixed, f, ensure_ascii=False, indent=2)

    print('Arquivo regravado em UTF-8. Se quiser, verifique o conteúdo ou abra o app novamente.')


if __name__ == '__main__':
    main()
