import json
from datetime import datetime
from pathlib import Path

HISTORICO_FILE = "historico.json"


def _carregar() -> list[dict]:
    if Path(HISTORICO_FILE).exists():
        with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _salvar(historico: list[dict]) -> None:
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)


def registrar_operacao(movimentos: list[dict], modo: str) -> None:
    """
    Salva uma operação no histórico.
    movimentos = [{"origem": "...", "destino": "..."}, ...]
    modo = "mover" | "copiar"
    """
    historico = _carregar()
    historico.append({
        "data":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modo":       modo,
        "movimentos": movimentos,
    })
    _salvar(historico)


def listar_operacoes() -> list[dict]:
    """Retorna todas as operações salvas, da mais recente para a mais antiga."""
    return list(reversed(_carregar()))


def desfazer_operacao(indice_reverso: int) -> tuple[list[str], int, int]:
    """
    Desfaz a operação no índice (0 = mais recente).
    Retorna (mensagens, revertidos, erros).
    """
    historico = _carregar()
    if not historico:
        return ["[aviso] Nenhuma operação no histórico."], 0, 0

    # Converte índice reverso para índice real
    indice_real = len(historico) - 1 - indice_reverso
    if indice_real < 0 or indice_real >= len(historico):
        return ["[erro] Operação não encontrada."], 0, 0

    operacao  = historico[indice_real]
    mensagens = []
    revertidos = 0
    erros      = 0

    for mov in operacao["movimentos"]:
        origem  = Path(mov["origem"])
        destino = Path(mov["destino"])

        if not destino.exists():
            mensagens.append(f"[aviso] Não encontrado: {destino.name}")
            erros += 1
            continue

        try:
            origem.parent.mkdir(parents=True, exist_ok=True)
            destino.rename(origem)
            mensagens.append(f"[revertido] {destino.name} → {origem.parent}")
            revertidos += 1
        except Exception as e:
            mensagens.append(f"[erro] {destino.name}: {e}")
            erros += 1

    # Remove a operação do histórico após desfazer
    historico.pop(indice_real)
    _salvar(historico)

    return mensagens, revertidos, erros
