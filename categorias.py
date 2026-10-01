from config import carregar

TIPOS_PADRAO = {
    "Imagens":          ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
    "Vídeos":           ["mp4", "avi", "mkv", "mov", "wmv", "flv"],
    "Documentos":       ["pdf", "doc", "docx", "txt", "xlsx", "pptx", "odt", "pbix"],
    "Músicas":          ["mp3", "wav", "flac", "aac", "ogg"],
    "Compactados":      ["rar", "zip", "7z", "tar", "gz", "bz2"],
    "Instaladores":     ["exe", "msi", "deb", "apk"],
    "Scripts":          ["py", "js", "java", "c", "cpp", "sh"],
    "Design":           ["svg", "psd", "ai", "eps"],
    "Planilhas_Bancos": ["csv", "sql", "db", "accdb"],
}


def obter_tipos(config: dict | None = None) -> dict:
    """
    Retorna o dicionário de categorias.
    Se config tiver extensões customizadas, usa elas.
    Caso contrário usa os padrões.
    """
    if config is None:
        config = carregar()

    tipos_custom = config.get("extensoes_custom", {})
    if tipos_custom:
        return tipos_custom
    return dict(TIPOS_PADRAO)


def encontrar_categoria(extensao: str, config: dict | None = None) -> str:
    """Retorna a categoria de uma extensão, ou 'Outros' se não encontrar."""
    tipos = obter_tipos(config)
    return next(
        (cat for cat, lista in tipos.items() if extensao in lista),
        "Outros"
    )


# Mantém compatibilidade com imports antigos
TIPOS = TIPOS_PADRAO
