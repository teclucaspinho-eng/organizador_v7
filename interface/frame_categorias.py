import customtkinter as ctk

ICONES = {
    "Imagens":          "🖼",
    "Vídeos":           "🎬",
    "Documentos":       "📄",
    "Músicas":          "🎵",
    "Compactados":      "📦",
    "Instaladores":     "⚙",
    "Scripts":          "💻",
    "Design":           "🎨",
    "Planilhas_Bancos": "📊",
}


class FrameCategorias(ctk.CTkFrame):

    def __init__(
        self,
        master,
        config: dict,
        categorias: list[str],
        on_toggle,
        on_toggle_dll,
        on_duplicatas,
        **kwargs,
    ):
        kwargs.setdefault("fg_color", "#161616")
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)

        self._config        = config
        self._on_toggle     = on_toggle
        self._on_toggle_dll = on_toggle_dll

        ctk.CTkLabel(
            self,
            text="FILTROS E FERRAMENTAS",
            font=("Consolas", 10, "bold"),
            text_color="#555",
        ).grid(row=0, column=0, columnspan=3, pady=(10, 6), padx=14, sticky="w")

        # Botões de categoria
        for i, categoria in enumerate(categorias):
            chave     = f"ignorar_{categoria.lower()}"
            ignorando = config.get(chave, False)
            icone     = ICONES.get(categoria, "•")

            btn = ctk.CTkButton(
                self,
                text=f"{icone}  {categoria}",
                corner_radius=8,
                height=34,
                width=148,
                font=("Consolas", 12),
                anchor="w",
                **self._estilo_categoria(ignorando),
            )
            btn.configure(command=lambda c=categoria, b=btn: self._toggle(c, b))
            btn.grid(row=(i // 3) + 1, column=i % 3, padx=6, pady=4)

        # Separador
        linha = (len(categorias) // 3) + 2
        ctk.CTkFrame(
            self,
            height=1,
            fg_color="#2a2a2a",
        ).grid(row=linha, column=0, columnspan=3, sticky="ew", padx=10, pady=6)

        # Botão DLL
        linha += 1
        mover_dll = config.get("mover_dll", False)
        self._botao_dll = ctk.CTkButton(
            self,
            text="DLL  ●" if mover_dll else "DLL  ○",
            command=self._toggle_dll,
            corner_radius=8,
            height=34,
            width=148,
            font=("Consolas", 12),
            anchor="w",
            **self._estilo_dll(mover_dll),
        )
        self._botao_dll.grid(row=linha, column=0, padx=6, pady=4)

        # Botão Duplicatas
        ctk.CTkButton(
            self,
            text="🔍  Duplicatas",
            command=on_duplicatas,
            corner_radius=8,
            height=34,
            width=148,
            font=("Consolas", 12),
            anchor="w",
            fg_color="#3a2a00",
            hover_color="#4a3800",
            border_width=1,
            border_color="#f0c040",
            text_color="#f0c040",
        ).grid(row=linha, column=1, padx=6, pady=4)

        ctk.CTkLabel(self, text="", height=6).grid(row=linha + 1, column=0)

    @staticmethod
    def _estilo_categoria(ignorando: bool) -> dict:
        if ignorando:
            return {
                "fg_color":     "#1e1e1e",
                "hover_color":  "#2a2a2a",
                "border_width": 1,
                "border_color": "#333",
                "text_color":   "#444",
            }
        return {
            "fg_color":     "#1a3a1a",
            "hover_color":  "#1f4a1f",
            "border_width": 1,
            "border_color": "#1DB954",
            "text_color":   "#1DB954",
        }

    @staticmethod
    def _estilo_dll(mover_dll: bool) -> dict:
        if mover_dll:
            return {
                "fg_color":     "#1a3a1a",
                "hover_color":  "#1f4a1f",
                "border_width": 1,
                "border_color": "#1DB954",
                "text_color":   "#1DB954",
            }
        return {
            "fg_color":     "#1e1e1e",
            "hover_color":  "#2a2a2a",
            "border_width": 1,
            "border_color": "#333",
            "text_color":   "#444",
        }

    def _toggle(self, categoria: str, botao: ctk.CTkButton):
        agora_ignorando = self._on_toggle(categoria)
        icone = ICONES.get(categoria, "•")
        botao.configure(
            text=f"{icone}  {categoria}",
            **self._estilo_categoria(agora_ignorando),
        )

    def _toggle_dll(self):
        novo = self._on_toggle_dll()
        self._botao_dll.configure(
            text="DLL  ●" if novo else "DLL  ○",
            **self._estilo_dll(novo),
        )
