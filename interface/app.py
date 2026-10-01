import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

import config as cfg
import log as logger
import mover as mov
import historico as hist
from categorias import obter_tipos
from interface.frame_botoes import FrameBotoes
from interface.frame_categorias import FrameCategorias
from interface.janela_duplicatas import JanelaDuplicatas
from interface.janela_dryrun import JanelaDryRun
from interface.janela_historico import JanelaHistorico
from interface.janela_configuracoes import JanelaConfiguracoes

COR_BG        = "#0e0e0e"
COR_PAINEL    = "#161616"
COR_BORDA     = "#222"
COR_VERDE     = "#1DB954"
COR_TEXTO_DIM = "#555"
FONTE_TITULO  = ("Consolas", 20, "bold")
FONTE_MONO    = ("Consolas", 11)

#janela principal
class App(ctk.CTk):
    def __init__(self):
        self._config = cfg.carregar()
        ctk.set_default_color_theme("green")
        ctk.set_appearance_mode(self._config.get("tema", "dark"))

        super().__init__()
        self.title("Organizador de Arquivos")
        self.geometry("900x780")
        self.resizable(True, True)
        self.configure(fg_color=COR_BG)

        self._cancelar       = False
        self._pastas_origem  = []   # lista de pastas de origem
        self._pasta_destino  = None

        self._build_ui()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def _build_ui(self):

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="ORGANIZADOR",
            font=FONTE_TITULO,
            text_color=COR_VERDE,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="v7.0",
            font=("Consolas", 11),
            text_color=COR_TEXTO_DIM,
        ).pack(side="left", padx=(8, 0), anchor="s", pady=(0, 4))

        ctk.CTkFrame(self, height=1, fg_color=COR_BORDA).pack(fill="x", padx=24, pady=(0, 14))

        FrameBotoes(
            self,
            config=self._config,
            on_organizar=self._iniciar_mover,
            on_copiar=self._iniciar_copiar,
            on_cancelar=self._cancelar_organizar,
            on_toggle_dll=self._toggle_dll,
            on_duplicatas=self._abrir_duplicatas,
            on_historico=self._abrir_historico,
            on_configuracoes=self._abrir_configuracoes,
        ).pack(padx=24, anchor="w")

        # Painel de pastas de origem
        ctk.CTkLabel(
            self,
            text="PASTAS DE ORIGEM",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(14, 4))

        pastas_frame = ctk.CTkFrame(self, fg_color=COR_PAINEL, corner_radius=12)
        pastas_frame.pack(fill="x", padx=24)

        # Linha de botões de pastas
        pastas_btn_row = ctk.CTkFrame(pastas_frame, fg_color="transparent")
        pastas_btn_row.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkButton(
            pastas_btn_row,
            text="+ Adicionar Pasta",
            command=self._adicionar_pasta_origem,
            corner_radius=6,
            height=30,
            font=FONTE_MONO,
            fg_color="#1a3a1a",
            hover_color="#1f4a1f",
            border_width=1,
            border_color=COR_VERDE,
            text_color=COR_VERDE,
            width=140,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            pastas_btn_row,
            text="✕ Limpar",
            command=self._limpar_pastas_origem,
            corner_radius=6,
            height=30,
            font=FONTE_MONO,
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#444",
            text_color="#888",
            width=80,
        ).pack(side="left")

        self._pastas_label = ctk.CTkLabel(
            pastas_btn_row,
            text="Nenhuma pasta selecionada",
            font=FONTE_MONO,
            text_color="#444",
            anchor="w",
        )
        self._pastas_label.pack(side="left", padx=12)

        # Lista de pastas selecionadas
        self._pastas_scroll = ctk.CTkScrollableFrame(
            pastas_frame,
            height=70,
            fg_color="transparent",
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._pastas_scroll.pack(fill="x", padx=12, pady=(0, 10))

        # Categorias
        ctk.CTkLabel(
            self,
            text="FILTROS E FERRAMENTAS",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(12, 2))

        self._frame_categorias = FrameCategorias(
            self,
            config=self._config,
            categorias=list(obter_tipos(self._config).keys()),
            on_toggle=self._toggle_categoria,
            on_toggle_dll=self._toggle_dll,
            on_duplicatas=self._abrir_duplicatas,
        )
        self._frame_categorias.pack(padx=24, fill="x")

        # Progresso
        ctk.CTkLabel(
            self,
            text="PROGRESSO",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(12, 4))

        prog_frame = ctk.CTkFrame(self, fg_color=COR_PAINEL, corner_radius=12)
        prog_frame.pack(fill="x", padx=24)

        self._progresso = ctk.CTkProgressBar(
            prog_frame,
            width=830,
            height=6,
            corner_radius=3,
            fg_color="#1e1e1e",
            progress_color=COR_VERDE,
        )
        self._progresso.pack(padx=16, pady=(14, 6))
        self._progresso.set(0)

        self._contador_label = ctk.CTkLabel(
            prog_frame,
            text="Aguardando início...",
            font=FONTE_MONO,
            text_color=COR_TEXTO_DIM,
        )
        self._contador_label.pack(anchor="w", padx=16, pady=(0, 12))

        # Log
        log_header = ctk.CTkFrame(self, fg_color="transparent")
        log_header.pack(fill="x", padx=24, pady=(12, 4))

        ctk.CTkLabel(
            log_header,
            text="LOG",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(side="left")

        ctk.CTkButton(
            log_header,
            text="abrir arquivo ↗",
            command=self._abrir_log,
            corner_radius=6,
            height=22,
            width=110,
            font=("Consolas", 10),
            fg_color="transparent",
            hover_color="#1e1e1e",
            border_width=1,
            border_color="#333",
            text_color="#555",
        ).pack(side="right")

        self._log_box = ctk.CTkTextbox(
            self,
            width=850,
            height=120,
            state="disabled",
            font=FONTE_MONO,
            fg_color=COR_PAINEL,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            text_color="#4CAF50",
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._log_box.pack(padx=24, pady=(0, 16))

    # ------------------------------------------------------------------
    # Múltiplas pastas de origem
    # ------------------------------------------------------------------
    def _adicionar_pasta_origem(self):
        pasta = filedialog.askdirectory(title="Adicionar pasta de origem")
        if not pasta:
            return

        pasta_path = Path(pasta)
        if pasta_path in self._pastas_origem:
            messagebox.showwarning("Aviso", "Essa pasta já foi adicionada!")
            return

        self._pastas_origem.append(pasta_path)
        self._atualizar_lista_pastas()

    def _limpar_pastas_origem(self):
        self._pastas_origem.clear()
        self._atualizar_lista_pastas()

    def _remover_pasta_origem(self, pasta: Path):
        if pasta in self._pastas_origem:
            self._pastas_origem.remove(pasta)
            self._atualizar_lista_pastas()

    def _atualizar_lista_pastas(self):
        for w in self._pastas_scroll.winfo_children():
            w.destroy()

        total = len(self._pastas_origem)
        if total == 0:
            self._pastas_label.configure(text="Nenhuma pasta selecionada")
        else:
            self._pastas_label.configure(
                text=f"{total} pasta(s) selecionada(s)",
                text_color=COR_VERDE,
            )

        for pasta in self._pastas_origem:
            row = ctk.CTkFrame(self._pastas_scroll, fg_color="#1e1e1e", corner_radius=6)
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=str(pasta),
                font=FONTE_MONO,
                text_color="#aaa",
                anchor="w",
            ).pack(side="left", padx=10, pady=4)

            ctk.CTkButton(
                row,
                text="✕",
                command=lambda p=pasta: self._remover_pasta_origem(p),
                width=24,
                height=22,
                corner_radius=4,
                font=("Consolas", 9),
                fg_color="#3a0a0a",
                hover_color="#4a1010",
                text_color="#c0392b",
                border_width=0,
            ).pack(side="right", padx=6, pady=3)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _toggle_dll(self) -> bool:
        return cfg.toggle_dll(self._config)

    def _toggle_categoria(self, categoria: str) -> bool:
        novo   = cfg.toggle_categoria(self._config, categoria)
        estado = "ignorado" if novo else "movido"
        self._log(f"[filtro] {categoria} → {estado}")
        return novo

    def _abrir_duplicatas(self):
        JanelaDuplicatas(self)

    def _abrir_historico(self):
        JanelaHistorico(self)

    def _abrir_configuracoes(self):
        JanelaConfiguracoes(self, on_salvar=self._recarregar_config)

    def _recarregar_config(self):
        self._config = cfg.carregar()
        self._frame_categorias.destroy()
        self._frame_categorias = FrameCategorias(
            self,
            config=self._config,
            categorias=list(obter_tipos(self._config).keys()),
            on_toggle=self._toggle_categoria,
            on_toggle_dll=self._toggle_dll,
            on_duplicatas=self._abrir_duplicatas,
        )
        self._frame_categorias.pack(padx=24, fill="x", before=self._progresso.master)
        self._log("[config] Configurações recarregadas.")

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------
    def _log(self, mensagem: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", mensagem + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")
        logger.registrar(mensagem)

    def _abrir_log(self):
        caminho = logger.caminho_log()
        if Path(caminho).exists():
            if os.name == "nt":
                os.startfile(caminho)
            else:
                os.system(f"xdg-open '{caminho}'")
        else:
            messagebox.showinfo("Log", "Nenhum arquivo de log encontrado ainda.")

    # ------------------------------------------------------------------
    # Seleção de destino e início
    # ------------------------------------------------------------------
    def _selecionar_destino(self) -> bool:
        if not self._pastas_origem:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma pasta de origem!")
            return False

        pasta = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not pasta:
            return False

        self._pasta_destino = Path(pasta)
        return True

    def _iniciar_mover(self):
        if not self._selecionar_destino():
            return
        JanelaDryRun(
            self,
            pasta_origem=self._pastas_origem[0],
            pasta_destino=self._pasta_destino,
            config=self._config,
            copiar=False,
            on_confirmar=self._confirmar_e_processar,
        )

    def _iniciar_copiar(self):
        if not self._selecionar_destino():
            return
        JanelaDryRun(
            self,
            pasta_origem=self._pastas_origem[0],
            pasta_destino=self._pasta_destino,
            config=self._config,
            copiar=True,
            on_confirmar=self._confirmar_e_processar,
        )

    def _confirmar_e_processar(self, copiar: bool):
        threading.Thread(
            target=self._processar_thread,
            args=(list(self._pastas_origem), self._pasta_destino, copiar),
            daemon=True,
        ).start()

    def _cancelar_organizar(self):
        resposta = messagebox.askyesno("Cancelar", "Tem certeza que deseja cancelar?")
        if resposta:
            self._cancelar = True
            self._log("[!] Cancelamento solicitado.")
        else:
            self._log("[—] Cancelamento ignorado.")

    # ------------------------------------------------------------------
    # Processamento
    # ------------------------------------------------------------------
    def _processar_thread(self, pastas_origem: list[Path], pasta_destino: Path, copiar: bool):
        self._cancelar = False
        modo = "cópia" if copiar else "movimentação"

        # Valida cada pasta de origem
        for pasta in pastas_origem:
            erro = mov.validar_pastas(pasta, pasta_destino)
            if erro:
                messagebox.showerror("Erro", f"{pasta.name}: {erro}")
                self._log(f"[erro] {erro}")
                return

        # Coleta todos os arquivos
        todos_arquivos = []
        for pasta in pastas_origem:
            todos_arquivos.extend([f for f in pasta.rglob("*") if f.is_file()])

        if not todos_arquivos:
            messagebox.showwarning("Aviso", "Nenhum arquivo encontrado nas pastas de origem!")
            return

        if not mov.checar_espaco(todos_arquivos, pasta_destino):
            messagebox.showerror("Erro", "Espaço insuficiente em disco!")
            self._log("[erro] Espaço insuficiente em disco.")
            return

        logger.registrar_sessao_inicio()
        self._progresso.set(0)
        total = len(todos_arquivos)
        self._log(f"[inicio] {modo} de {total} arquivo(s) em {len(pastas_origem)} pasta(s)")

        def on_progresso(atual, total):
            pct = int((atual / total) * 100)
            self._progresso.set(atual / total)
            self._contador_label.configure(text=f"{atual} / {total}  ({pct}%)")

        oks, ignorados, cancelado, movimentos = mov.organizar(
            pastas_origem=pastas_origem,
            pasta_destino=pasta_destino,
            config=self._config,
            num_threads=self._config.get("threads", 8),
            cancelar_flag=lambda: self._cancelar,
            on_progresso=on_progresso,
            on_log=self._log,
            copiar=copiar,
        )

        if movimentos and not copiar and not cancelado:
            hist.registrar_operacao(movimentos, modo="mover")

        logger.registrar_sessao_fim(oks, ignorados, cancelado)

        if cancelado:
            self._log("[!] Processo cancelado pelo usuário.")
            self._contador_label.configure(text="Cancelado.")
        else:
            acao = "copiado(s)" if copiar else "movido(s)"
            self._contador_label.configure(
                text=f"Concluído — {oks} {acao}, {ignorados} ignorado(s)"
            )
            self._log(f"[ok] {oks} {acao} | {ignorados} ignorado(s)")
            messagebox.showinfo(
                "Concluído",
                f"{oks} arquivo(s) {acao}\n{ignorados} arquivo(s) ignorado(s)",
            )
