import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from categorias import encontrar_categoria


def _esta_na_lista_negra(caminho: Path, lista_negra: list[str]) -> bool:
    """
    Verifica se o arquivo ou qualquer pasta pai está na lista negra.
    Compara por nome (case-insensitive).
    """
    nomes_negros = [n.lower() for n in lista_negra]
    for parte in caminho.parts:
        if parte.lower() in nomes_negros:
            return True
    return False


def processar_arquivo(
    caminho_arquivo: Path,
    pasta_destino: Path,
    config: dict,
    copiar: bool = False,
) -> tuple[str, str, dict | None]:
    arquivo  = caminho_arquivo.name
    extensao = caminho_arquivo.suffix.lower().lstrip(".") if caminho_arquivo.suffix else "sem_extensao"

    # Lista negra
    lista_negra = config.get("lista_negra", [])
    if _esta_na_lista_negra(caminho_arquivo, lista_negra):
        return f"Ignorado (lista negra): {arquivo}", "ignorado", None

    # DLL
    if extensao == "dll" and not config.get("mover_dll", False):
        return f"Ignorado: {arquivo} (DLL)", "ignorado", None

    # Categoria ignorada
    categoria = encontrar_categoria(extensao, config)
    chave = f"ignorar_{categoria.lower()}"
    if config.get(chave, False):
        return f"Ignorado: {arquivo} ({categoria})", "ignorado", None

    destino_final = pasta_destino / categoria
    destino_final.mkdir(parents=True, exist_ok=True)

    try:
        destino_arquivo = destino_final / arquivo
        contador = 1
        while destino_arquivo.exists():
            destino_arquivo = destino_final / f"{caminho_arquivo.stem}_{contador}{caminho_arquivo.suffix}"
            contador += 1

        if copiar:
            shutil.copy2(str(caminho_arquivo), str(destino_arquivo))
            acao = "Copiado"
        else:
            shutil.move(str(caminho_arquivo), str(destino_arquivo))
            acao = "Movido"

        movimento = {"origem": str(caminho_arquivo), "destino": str(destino_arquivo)}
        return f"{acao}: {arquivo} → {destino_final}", "ok", movimento

    except Exception as e:
        return f"Erro ao processar {arquivo}: {e}", "erro", None


def mover_arquivo(caminho_arquivo, pasta_destino, config):
    msg, status, _ = processar_arquivo(caminho_arquivo, pasta_destino, config, copiar=False)
    return msg, status


def validar_pastas(origem: Path, destino: Path) -> str | None:
    o = origem.resolve()
    d = destino.resolve()

    if o == d:
        return "A pasta de origem e destino não podem ser a mesma!"
    try:
        d.relative_to(o)
        return "A pasta de destino não pode estar dentro da pasta de origem!"
    except ValueError:
        pass
    try:
        o.relative_to(d)
        return "A pasta de origem não pode estar dentro da pasta de destino!"
    except ValueError:
        pass
    return None


def checar_espaco(arquivos: list[Path], destino: Path) -> bool:
    tamanho_total = sum(f.stat().st_size for f in arquivos)
    livre = shutil.disk_usage(str(destino)).free
    return livre >= tamanho_total


def organizar(
    pastas_origem: list[Path],
    pasta_destino: Path,
    config: dict,
    num_threads: int,
    cancelar_flag: Callable[[], bool],
    on_progresso: Callable[[int, int], None],
    on_log: Callable[[str], None],
    copiar: bool = False,
) -> tuple[int, int, bool, list[dict]]:
    """
    Aceita múltiplas pastas de origem.
    Retorna (total_oks, total_ignorados, foi_cancelado, movimentos).
    """
    # Coleta arquivos de todas as pastas de origem
    arquivos = []
    for pasta in pastas_origem:
        arquivos.extend([f for f in pasta.rglob("*") if f.is_file()])

    total      = len(arquivos)
    oks        = 0
    ignorados  = 0
    movimentos = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futuros = {
            executor.submit(processar_arquivo, f, pasta_destino, config, copiar): f
            for f in arquivos
        }
        for i, futuro in enumerate(as_completed(futuros), start=1):
            if cancelar_flag():
                return oks, ignorados, True, movimentos

            mensagem, status, movimento = futuro.result()
            on_log(mensagem)

            if status == "ok":
                oks += 1
                if movimento:
                    movimentos.append(movimento)
            elif status == "ignorado":
                ignorados += 1

            on_progresso(i, total)

    return oks, ignorados, False, movimentos
