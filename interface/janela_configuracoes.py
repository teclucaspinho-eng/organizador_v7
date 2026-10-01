import customtkinter as ctk
from tkinter import messagebox
from copy import deepcopy

import config as cfg
from categorias import TIPOS_PADRAO

COR_BG        = "#0e0e0e"
COR_PAINEL    = "#161616"
COR_PAINEL2   = "#1a1a1a"
COR_BORDA     = "#222"
COR_VERDE     = "#1DB954"
COR_VERMELHO  = "#c0392b"
COR_TEXTO     = "#e0e0e0"
COR_TEXTO_DIM = "#555"
FONTE_MONO    = ("Consolas", 11)
FONTE_BOLD    = ("Consolas", 11, "bold")


class JanelaConfiguracoes(ctk.CTkToplevel):

    def __init__(self, master, on_salvar=None):
        super().__init__(master)
        self.title("Configurações")
        self.geometry("640x580")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        self._config    = cfg.carregar()
        self._on_salvar = on_salvar

        tipos_atuais = self._config.get("extensoes_custom") or deepcopy(TIPOS_PADRAO)
        self._extensoes: dict[str, list[str]] = deepcopy(tipos_atuais)
        self._lista_negra: list[str] = list(self._config.get("lista_negra", []))

        self._build_ui()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def _build_ui(self):

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="CONFIGURAÇÕES",
            font=("Consolas", 20, "bold"),
            text_color=COR_VERDE,
        ).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=COR_BORDA).pack(fill="x", padx=24, pady=(0, 12))

        self._tabview = ctk.CTkTabview(
            self,
            fg_color=COR_PAINEL,
            segmented_button_fg_color="#1a1a1a",
            segmented_button_selected_color=COR_VERDE,
            segmented_button_selected_hover_color="#17a349",
            segmented_button_unselected_color="#1a1a1a",
            segmented_button_unselected_hover_color="#2a2a2a",
            text_color=COR_TEXTO,
            text_color_disabled=COR_TEXTO_DIM,
        )
        self._tabview.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self._tabview.add("⚙  Geral")
        self._tabview.add("📂  Extensões")
        self._tabview.add("🚫  Lista Negra")

        self._build_aba_geral()
        self._build_aba_extensoes()
        self._build_aba_lista_negra()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 16))

        ctk.CTkButton(
            btn_frame,
            text="✓  Salvar",
            command=self._salvar,
            corner_radius=8,
            height=38,
            font=FONTE_BOLD,
            fg_color=COR_VERDE,
            hover_color="#17a349",
            text_color="#0a0a0a",
        ).grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            btn_frame,
            text="↺  Restaurar Padrões",
            command=self._restaurar_padroes,
            corner_radius=8,
            height=38,
            font=FONTE_MONO,
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#444",
            text_color="#888",
        ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            btn_frame,
            text="✕  Cancelar",
            command=self.destroy,
            corner_radius=8,
            height=38,
            font=FONTE_MONO,
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            border_width=1,
            border_color="#444",
        ).grid(row=0, column=2, padx=6)

    # ------------------------------------------------------------------
    # Aba Geral
    # ------------------------------------------------------------------
    def _build_aba_geral(self):
        aba = self._tabview.tab("⚙  Geral")

        threads_frame = ctk.CTkFrame(aba, fg_color=COR_PAINEL2, corner_radius=10)
        threads_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            threads_frame,
            text="THREADS PARALELAS",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            threads_frame,
            text="Quantos arquivos processar ao mesmo tempo.\nMais threads = mais rápido, mas consome mais CPU. Recomendado: 4–16.",
            font=("Consolas", 10),
            text_color="#666",
            justify="left",
        ).pack(anchor="w", padx=14)

        slider_row = ctk.CTkFrame(threads_frame, fg_color="transparent")
        slider_row.pack(fill="x", padx=14, pady=(8, 12))

        self._threads_label = ctk.CTkLabel(
            slider_row,
            text=str(self._config.get("threads", 8)),
            font=("Consolas", 14, "bold"),
            text_color=COR_VERDE,
            width=30,
        )
        self._threads_label.pack(side="left", padx=(0, 10))

        self._threads_slider = ctk.CTkSlider(
            slider_row,
            from_=1,
            to=32,
            number_of_steps=31,
            button_color=COR_VERDE,
            button_hover_color="#17a349",
            progress_color=COR_VERDE,
            fg_color="#2a2a2a",
            command=self._atualizar_threads,
        )
        self._threads_slider.set(self._config.get("threads", 8))
        self._threads_slider.pack(side="left", fill="x", expand=True)

        tema_frame = ctk.CTkFrame(aba, fg_color=COR_PAINEL2, corner_radius=10)
        tema_frame.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            tema_frame,
            text="TEMA",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=14, pady=(10, 6))

        tema_row = ctk.CTkFrame(tema_frame, fg_color="transparent")
        tema_row.pack(fill="x", padx=14, pady=(0, 12))

        self._tema_var = ctk.StringVar(value=self._config.get("tema", "dark"))

        for texto, valor in [("🌙  Escuro", "dark"), ("☀  Claro", "light")]:
            ctk.CTkRadioButton(
                tema_row,
                text=texto,
                variable=self._tema_var,
                value=valor,
                font=FONTE_MONO,
                text_color=COR_TEXTO,
                fg_color=COR_VERDE,
                hover_color="#17a349",
            ).pack(side="left", padx=(0, 20))

    def _atualizar_threads(self, valor):
        self._threads_label.configure(text=str(int(valor)))

    # ------------------------------------------------------------------
    # Aba Extensões
    # ------------------------------------------------------------------
    def _build_aba_extensoes(self):
        aba = self._tabview.tab("📂  Extensões")

        ctk.CTkLabel(
            aba,
            text="Clique em uma categoria para editar suas extensões.",
            font=("Consolas", 10),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        main = ctk.CTkFrame(aba, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self._lista_cats = ctk.CTkScrollableFrame(
            main,
            width=160,
            fg_color=COR_PAINEL2,
            corner_radius=10,
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._lista_cats.pack(side="left", fill="y", padx=(0, 8))

        self._botoes_cat: dict[str, ctk.CTkButton] = {}
        for categoria in self._extensoes:
            btn = ctk.CTkButton(
                self._lista_cats,
                text=categoria,
                anchor="w",
                font=FONTE_MONO,
                height=32,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#2a2a2a",
                text_color="#888",
                border_width=0,
            )
            btn.configure(command=lambda c=categoria, b=btn: self._selecionar_categoria(c, b))
            btn.pack(fill="x", padx=4, pady=2)
            self._botoes_cat[categoria] = btn

        self._editor_frame = ctk.CTkFrame(main, fg_color=COR_PAINEL2, corner_radius=10)
        self._editor_frame.pack(side="left", fill="both", expand=True)

        self._editor_titulo = ctk.CTkLabel(
            self._editor_frame,
            text="← Selecione uma categoria",
            font=FONTE_BOLD,
            text_color=COR_TEXTO_DIM,
        )
        self._editor_titulo.pack(pady=20)

        self._ext_scroll = ctk.CTkScrollableFrame(
            self._editor_frame,
            fg_color="transparent",
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._ext_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        add_row = ctk.CTkFrame(self._editor_frame, fg_color="transparent")
        add_row.pack(fill="x", padx=10, pady=(0, 10))

        self._input_ext = ctk.CTkEntry(
            add_row,
            placeholder_text="nova extensão (ex: webm)",
            font=FONTE_MONO,
            fg_color="#1e1e1e",
            border_color="#333",
            text_color=COR_TEXTO,
            height=32,
        )
        self._input_ext.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            add_row,
            text="+ Adicionar",
            command=self._adicionar_extensao,
            corner_radius=6,
            height=32,
            width=90,
            font=FONTE_MONO,
            fg_color="#1a3a1a",
            hover_color="#1f4a1f",
            border_width=1,
            border_color=COR_VERDE,
            text_color=COR_VERDE,
        ).pack(side="right")

        self._categoria_selecionada = None

    def _selecionar_categoria(self, categoria: str, botao: ctk.CTkButton):
        for b in self._botoes_cat.values():
            b.configure(fg_color="transparent", text_color="#888")
        botao.configure(fg_color="#1a3a1a", text_color=COR_VERDE)
        self._categoria_selecionada = categoria
        self._editor_titulo.configure(text=categoria, text_color=COR_VERDE)
        self._renderizar_extensoes(categoria)

    def _renderizar_extensoes(self, categoria: str):
        for w in self._ext_scroll.winfo_children():
            w.destroy()
        for ext in self._extensoes.get(categoria, []):
            row = ctk.CTkFrame(self._ext_scroll, fg_color="#1e1e1e", corner_radius=6)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row,
                text=f".{ext}",
                font=FONTE_MONO,
                text_color=COR_TEXTO,
                anchor="w",
            ).pack(side="left", padx=10, pady=6)
            ctk.CTkButton(
                row,
                text="✕",
                command=lambda e=ext, c=categoria: self._remover_extensao(c, e),
                width=28,
                height=24,
                corner_radius=4,
                font=("Consolas", 10),
                fg_color="#3a0a0a",
                hover_color="#4a1010",
                text_color=COR_VERMELHO,
                border_width=0,
            ).pack(side="right", padx=6, pady=4)

    def _adicionar_extensao(self):
        if not self._categoria_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma categoria primeiro!")
            return
        ext = self._input_ext.get().strip().lower().lstrip(".")
        if not ext:
            return
        if ext in self._extensoes.get(self._categoria_selecionada, []):
            messagebox.showwarning("Aviso", f"A extensão .{ext} já existe nessa categoria!")
            return
        for cat, lista in self._extensoes.items():
            if ext in lista and cat != self._categoria_selecionada:
                messagebox.showwarning("Aviso", f"A extensão .{ext} já pertence à categoria '{cat}'!")
                return
        self._extensoes[self._categoria_selecionada].append(ext)
        self._input_ext.delete(0, "end")
        self._renderizar_extensoes(self._categoria_selecionada)

    def _remover_extensao(self, categoria: str, ext: str):
        if ext in self._extensoes.get(categoria, []):
            self._extensoes[categoria].remove(ext)
            self._renderizar_extensoes(categoria)

    # ------------------------------------------------------------------
    # Aba Lista Negra
    # ------------------------------------------------------------------
    def _build_aba_lista_negra(self):
        aba = self._tabview.tab("🚫  Lista Negra")

        ctk.CTkLabel(
            aba,
            text="Arquivos e pastas nessa lista nunca serão movidos ou copiados.\nUse o nome exato do arquivo ou pasta. Ex: .git, node_modules, thumbs.db",
            font=("Consolas", 10),
            text_color=COR_TEXTO_DIM,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Input para adicionar
        add_row = ctk.CTkFrame(aba, fg_color="transparent")
        add_row.pack(fill="x", padx=16, pady=(0, 8))

        self._input_negra = ctk.CTkEntry(
            add_row,
            placeholder_text="nome do arquivo ou pasta (ex: .git)",
            font=FONTE_MONO,
            fg_color="#1e1e1e",
            border_color="#333",
            text_color=COR_TEXTO,
            height=34,
        )
        self._input_negra.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._input_negra.bind("<Return>", lambda e: self._adicionar_negra())

        ctk.CTkButton(
            add_row,
            text="+ Adicionar",
            command=self._adicionar_negra,
            corner_radius=6,
            height=34,
            width=100,
            font=FONTE_MONO,
            fg_color="#3a0a0a",
            hover_color="#4a1010",
            border_width=1,
            border_color=COR_VERMELHO,
            text_color=COR_VERMELHO,
        ).pack(side="right")

        # Lista de itens bloqueados
        self._negra_scroll = ctk.CTkScrollableFrame(
            aba,
            fg_color=COR_PAINEL2,
            corner_radius=10,
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._negra_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        self._renderizar_lista_negra()

    def _renderizar_lista_negra(self):
        for w in self._negra_scroll.winfo_children():
            w.destroy()

        if not self._lista_negra:
            ctk.CTkLabel(
                self._negra_scroll,
                text="Nenhum item na lista negra.",
                font=FONTE_MONO,
                text_color=COR_TEXTO_DIM,
            ).pack(pady=20)
            return

        for item in self._lista_negra:
            row = ctk.CTkFrame(self._negra_scroll, fg_color="#1e1e1e", corner_radius=6)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=f"🚫  {item}",
                font=FONTE_MONO,
                text_color="#e57373",
                anchor="w",
            ).pack(side="left", padx=10, pady=8)

            ctk.CTkButton(
                row,
                text="✕",
                command=lambda i=item: self._remover_negra(i),
                width=28,
                height=24,
                corner_radius=4,
                font=("Consolas", 10),
                fg_color="#3a0a0a",
                hover_color="#4a1010",
                text_color=COR_VERMELHO,
                border_width=0,
            ).pack(side="right", padx=6, pady=4)

    def _adicionar_negra(self):
        item = self._input_negra.get().strip()
        if not item:
            return
        if item in self._lista_negra:
            messagebox.showwarning("Aviso", f"'{item}' já está na lista negra!")
            return
        self._lista_negra.append(item)
        self._input_negra.delete(0, "end")
        self._renderizar_lista_negra()

    def _remover_negra(self, item: str):
        if item in self._lista_negra:
            self._lista_negra.remove(item)
            self._renderizar_lista_negra()

    # ------------------------------------------------------------------
    # Salvar / Restaurar
    # ------------------------------------------------------------------
    def _salvar(self):
        self._config["threads"]          = int(self._threads_slider.get())
        self._config["tema"]             = self._tema_var.get()
        self._config["extensoes_custom"] = self._extensoes
        self._config["lista_negra"]      = self._lista_negra

        cfg.salvar(self._config)
        ctk.set_appearance_mode(self._config["tema"])

        if self._on_salvar:
            self._on_salvar()

        messagebox.showinfo("Salvo", "Configurações salvas com sucesso!")
        self.destroy()

    def _restaurar_padroes(self):
        confirmar = messagebox.askyesno(
            "Restaurar Padrões",
            "Isso vai restaurar todas as extensões para os valores originais.\nA lista negra não será afetada.\nContinuar?",
        )
        if not confirmar:
            return
        self._extensoes = deepcopy(TIPOS_PADRAO)
        self._config["extensoes_custom"] = {}
        if self._categoria_selecionada:
            self._renderizar_extensoes(self._categoria_selecionada)
        messagebox.showinfo("Restaurado", "Extensões restauradas para os padrões!")
