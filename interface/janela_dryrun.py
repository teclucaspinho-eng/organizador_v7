import customtkinter as ctk
from pathlib import Path
from typing import Callable

from categorias import encontrar_categoria

COR_BG        = "#0e0e0e"
COR_PAINEL    = "#161616"
COR_BORDA     = "#222"
COR_VERDE     = "#1DB954"
COR_AZUL      = "#1565C0"
COR_TEXTO_DIM = "#555"
FONTE_MONO    = ("Consolas", 11)


class JanelaDryRun(ctk.CTkToplevel):
    """
    Mostra o que seria feito antes de confirmar a operação.
    Se o usuário confirmar, chama on_confirmar(copiar).
    """

    def __init__(
        self,
        master,
        pasta_origem: Path,
        pasta_destino: Path,
        config: dict,
        copiar: bool,
        on_confirmar: Callable[[bool], None],
    ):
        super().__init__(master)
        self.title("Simulação — Dry Run")
        self.geometry("600x560")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        self._copiar       = copiar
        self._on_confirmar = on_confirmar

        self._build_ui()
        self._simular(pasta_origem, pasta_destino, config, copiar)

    def _build_ui(self):

        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="DRY RUN",
            font=("Consolas", 20, "bold"),
            text_color=COR_VERDE,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="— simulação, nada será alterado",
            font=("Consolas", 11),
            text_color=COR_TEXTO_DIM,
        ).pack(side="left", padx=(10, 0), anchor="s", pady=(0, 4))

        ctk.CTkFrame(self, height=1, fg_color=COR_BORDA).pack(fill="x", padx=24, pady=(0, 14))

        # Resumo
        self._resumo_label = ctk.CTkLabel(
            self,
            text="Calculando...",
            font=("Consolas", 12, "bold"),
            text_color=COR_VERDE,
        )
        self._resumo_label.pack(anchor="w", padx=26, pady=(0, 6))

        # Preview
        ctk.CTkLabel(
            self,
            text="O QUE SERIA FEITO",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(0, 4))

        self._preview_box = ctk.CTkTextbox(
            self,
            width=552,
            height=300,
            state="disabled",
            font=FONTE_MONO,
            fg_color=COR_PAINEL,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            text_color="#aaa",
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._preview_box.pack(padx=24, pady=(0, 16))

        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 16))

        cor      = COR_AZUL if self._copiar else COR_VERDE
        hover    = "#0d47a1" if self._copiar else "#17a349"
        txt_acao = "⧉  Confirmar Cópia" if self._copiar else "▶  Confirmar Movimento"

        self._btn_confirmar = ctk.CTkButton(
            btn_frame,
            text=txt_acao,
            command=self._confirmar,
            corner_radius=8,
            height=38,
            font=("Consolas", 13, "bold"),
            fg_color=cor,
            hover_color=hover,
            text_color="#0a0a0a" if not self._copiar else "#e0e0e0",
        )
        self._btn_confirmar.grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            btn_frame,
            text="✕  Cancelar",
            command=self.destroy,
            corner_radius=8,
            height=38,
            font=("Consolas", 13),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            border_width=1,
            border_color="#444",
        ).grid(row=0, column=1, padx=6)

    def _simular(self, pasta_origem: Path, pasta_destino: Path, config: dict, copiar: bool):
        arquivos  = [f for f in pasta_origem.rglob("*") if f.is_file()]
        acao      = "COPIAR" if copiar else "MOVER"

        movidos   = 0
        ignorados = 0
        linhas    = []

        for arquivo in arquivos:
            extensao = arquivo.suffix.lower().lstrip(".") if arquivo.suffix else "sem_extensao"

            if extensao == "dll" and not config.get("mover_dll", False):
                linhas.append(f"[ignorar]  {arquivo.name}  (DLL)")
                ignorados += 1
                continue

            categoria = encontrar_categoria(extensao)
            chave = f"ignorar_{categoria.lower()}"
            if config.get(chave, False):
                linhas.append(f"[ignorar]  {arquivo.name}  ({categoria})")
                ignorados += 1
                continue

            destino = pasta_destino / categoria / arquivo.name
            linhas.append(f"[{acao}]  {arquivo.name}  →  {categoria}/")
            movidos += 1

        # Atualiza resumo
        self._resumo_label.configure(
            text=f"{movidos} arquivo(s) serão {acao.lower()}s  |  {ignorados} ignorado(s)"
        )

        # Preenche preview
        self._preview_box.configure(state="normal")
        self._preview_box.delete("1.0", "end")
        for linha in linhas:
            self._preview_box.insert("end", linha + "\n")
        self._preview_box.configure(state="disabled")

    def _confirmar(self):
        self.destroy()
        self._on_confirmar(self._copiar)
