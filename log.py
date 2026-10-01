from datetime import datetime
from pathlib import Path

LOG_FILE = "organizador.log"

def _timestamp() -> str:
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def registrar(mensagem: str) -> None:
    """Salva a mensagem no arquivo de log com timestamp."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{_timestamp()} {mensagem}\n")

def registrar_muitos(mensagens: list[str]) -> None:
    """Salva várias mensagens de uma vez."""
    ts = _timestamp()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for msg in mensagens:
            f.write(f"{ts} {msg}\n")

def registrar_sessao_inicio() -> None:
    registrar("=" * 50)
    registrar("Nova sessão de organização iniciada.")

def registrar_sessao_fim(movidos: int, ignorados: int, cancelado: bool = False) -> None:
    if cancelado:
        registrar("Sessão cancelada pelo usuário.")
    else:
        registrar(f"Sessão concluída. Movidos: {movidos} | Ignorados: {ignorados}")
    registrar("=" * 50)

def caminho_log() -> str:
    return str(Path(LOG_FILE).resolve())
