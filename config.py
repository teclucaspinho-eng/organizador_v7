import json
from pathlib import Path

CONFIG_FILE = "config.json"

DEFAULTS = {
    "mover_dll":                False,
    "ignorar_imagens":          False,
    "ignorar_vídeos":           False,
    "ignorar_documentos":       False,
    "ignorar_músicas":          False,
    "ignorar_compactados":      False,
    "ignorar_instaladores":     False,
    "ignorar_scripts":          False,
    "ignorar_design":           False,
    "ignorar_planilhas_bancos": False,
    "tema":                     "dark",
    "threads":                  8,
    "extensoes_custom":         {},
    "lista_negra":              [],   # nomes de arquivos/pastas a ignorar
}


def carregar() -> dict:
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
        for chave, valor in DEFAULTS.items():
            dados.setdefault(chave, valor)
        return dados
    return dict(DEFAULTS)


def salvar(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def toggle_categoria(config: dict, categoria: str) -> bool:
    chave = f"ignorar_{categoria.lower()}"
    config[chave] = not config.get(chave, False)
    salvar(config)
    return config[chave]


def toggle_dll(config: dict) -> bool:
    config["mover_dll"] = not config.get("mover_dll", False)
    salvar(config)
    return config["mover_dll"]
