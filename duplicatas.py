import shutil
from pathlib import Path
from collections import defaultdict


def encontrar_duplicatas(pasta: Path) -> dict[str, list[Path]]:
    """
    Varre a pasta recursivamente e agrupa arquivos com o mesmo nome.
    Retorna apenas os grupos que têm mais de um arquivo.

    Exemplo de retorno:
    {
        "relatorio.pdf": [Path("..."), Path("...")],
        "foto.jpg":      [Path("..."), Path("..."), Path("...")],
    }
    """
    grupos: dict[str, list[Path]] = defaultdict(list)

    for arquivo in pasta.rglob("*"):
        if arquivo.is_file():
            grupos[arquivo.name].append(arquivo)

    # Retorna só os que têm duplicata
    return {nome: caminhos for nome, caminhos in grupos.items() if len(caminhos) > 1}


def mover_duplicatas(
    duplicatas: dict[str, list[Path]],
    pasta_destino: Path,
) -> tuple[list[str], int]:
    """
    Move os arquivos duplicados (mantém o primeiro, move os demais)
    para pasta_destino/Duplicatas/.

    Retorna (mensagens, total_movidos).
    """
    pasta_dup = pasta_destino / "Duplicatas"
    pasta_dup.mkdir(parents=True, exist_ok=True)

    mensagens = []
    total_movidos = 0

    for nome, caminhos in duplicatas.items():
        # Mantém o primeiro, move os demais
        original = caminhos[0]
        copias   = caminhos[1:]

        mensagens.append(f"[original] {original}")

        for i, copia in enumerate(copias, start=1):
            try:
                destino = pasta_dup / nome
                contador = 1
                while destino.exists():
                    stem = Path(nome).stem
                    suffix = Path(nome).suffix
                    destino = pasta_dup / f"{stem}_dup{contador}{suffix}"
                    contador += 1

                shutil.move(str(copia), str(destino))
                mensagens.append(f"[movido]   {copia.name} → Duplicatas/{destino.name}")
                total_movidos += 1
            except Exception as e:
                mensagens.append(f"[erro]     {copia.name}: {e}")

    return mensagens, total_movidos
