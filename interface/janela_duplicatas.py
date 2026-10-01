import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

import duplicatas as dup
import log as logger

COR_BG        = "#0e0e0e"
COR_PAINEL    = "#161616"
COR_BORDA     = "#222"
COR_VERDE     = "#1DB954"
COR_AMARELO   = "#f0c040"
COR_TEXTO_DIM = "#555"
FONTE_MONO    = ("Consolas", 11)


class JanelaDuplicatas(ctk.CTkToplevel):
    """
    Janela dedicada para detecção e remoção de arquivos duplicados.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Verificar Duplicatas")
        self.geometry("560x580")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()  # Torna a janela modal

        self._pasta_origem  = None
        self._pasta_destino = None
        self._duplicatas    = {}

        self._build_ui()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def _build_ui(self):

        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="DUPLICATAS",
            font=("Consolas", 20, "bold"),
            text_color=COR_AMARELO,
        ).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=COR_BORDA).pack(fill="x", padx=24, pady=(0, 16))

        # Seleção de pasta de origem
        origem_frame = ctk.CTkFrame(self, fg_color=COR_PAINEL, corner_radius=10)
        origem_frame.pack(fill="x", padx=24, pady=(0, 8))

        ctk.CTkLabel(
            origem_frame,
            text="PASTA PARA VERIFICAR",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        origem_row = ctk.CTkFrame(origem_frame, fg_color="transparent")
        origem_row.pack(fill="x", padx=14, pady=(0, 10))

        self._label_origem = ctk.CTkLabel(
            origem_row,
            text="Nenhuma pasta selecionada",
            font=FONTE_MONO,
            text_color="#444",
            anchor="w",
        )
        self._label_origem.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            origem_row,
            text="Selecionar",
            command=self._selecionar_origem,
            corner_radius=6,
            height=28,
            width=90,
            font=FONTE_MONO,
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#444",
        ).pack(side="right")

        # Seleção de pasta de destino
        destino_frame = ctk.CTkFrame(self, fg_color=COR_PAINEL, corner_radius=10)
        destino_frame.pack(fill="x", padx=24, pady=(0, 14))

        ctk.CTkLabel(
            destino_frame,
            text="PASTA DE DESTINO (onde criar /Duplicatas)",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        destino_row = ctk.CTkFrame(destino_frame, fg_color="transparent")
        destino_row.pack(fill="x", padx=14, pady=(0, 10))

        self._label_destino = ctk.CTkLabel(
            destino_row,
            text="Nenhuma pasta selecionada",
            font=FONTE_MONO,
            text_color="#444",
            anchor="w",
        )
        self._label_destino.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            destino_row,
            text="Selecionar",
            command=self._selecionar_destino,
            corner_radius=6,
            height=28,
            width=90,
            font=FONTE_MONO,
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#444",
        ).pack(side="right")

        # Botões de ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 14))

        self._btn_verificar = ctk.CTkButton(
            btn_frame,
            text="🔍  Verificar",
            command=self._verificar,
            corner_radius=8,
            height=38,
            font=("Consolas", 13, "bold"),
            fg_color=COR_AMARELO,
            hover_color="#c9a030",
            text_color="#0a0a0a",
        )
        self._btn_verificar.grid(row=0, column=0, padx=6)

        self._btn_mover = ctk.CTkButton(
            btn_frame,
            text="📦  Mover Duplicatas",
            command=self._mover,
            corner_radius=8,
            height=38,
            font=("Consolas", 13, "bold"),
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#444",
            text_color="#555",
            state="disabled",
        )
        self._btn_mover.grid(row=0, column=1, padx=6)

        # Resultado
        ctk.CTkLabel(
            self,
            text="RESULTADO",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(0, 4))

        self._resultado_box = ctk.CTkTextbox(
            self,
            width=512,
            height=220,
            state="disabled",
            font=FONTE_MONO,
            fg_color=COR_PAINEL,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_AMARELO,
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._resultado_box.pack(padx=24, pady=(0, 16))

        # Rodapé
        self._status_label = ctk.CTkLabel(
            self,
            text="Selecione uma pasta para começar.",
            font=("Consolas", 10),
            text_color=COR_TEXTO_DIM,
        )
        self._status_label.pack(pady=(0, 12))

    # ------------------------------------------------------------------
    # Seleção de pastas — na thread principal
    # ------------------------------------------------------------------
    def _selecionar_origem(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta para verificar")
        if not pasta:
            return
        self._pasta_origem = Path(pasta)
        self._label_origem.configure(text=str(self._pasta_origem), text_color="#aaa")
        self._duplicatas = {}
        self._btn_mover.configure(state="disabled", text_color="#555", border_color="#444")
        self._limpar_resultado()

    def _selecionar_destino(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not pasta:
            return
        self._pasta_destino = Path(pasta)
        self._label_destino.configure(text=str(self._pasta_destino), text_color="#aaa")

    # ------------------------------------------------------------------
    # Verificar duplicatas
    # ------------------------------------------------------------------
    def _verificar(self):
        if not self._pasta_origem:
            messagebox.showwarning("Aviso", "Selecione uma pasta para verificar!")
            return

        self._limpar_resultado()
        self._status_label.configure(text="Verificando...")
        self._btn_verificar.configure(state="disabled")

        threading.Thread(target=self._verificar_thread, daemon=True).start()

    def _verificar_thread(self):
        self._duplicatas = dup.encontrar_duplicatas(self._pasta_origem)
        total_grupos  = len(self._duplicatas)
        total_arquivos = sum(len(v) - 1 for v in self._duplicatas.values())

        if not self._duplicatas:
            self._escrever("Nenhuma duplicata encontrada! ✓")
            self._status_label.configure(text="Tudo limpo.")
        else:
            self._escrever(f"Encontrado(s): {total_grupos} grupo(s) | {total_arquivos} arquivo(s) duplicado(s)\n")
            for nome, caminhos in self._duplicatas.items():
                self._escrever(f"── {nome}  ({len(caminhos)}x)")
                for c in caminhos:
                    self._escrever(f"   {c}")
                self._escrever("")

            self._status_label.configure(
                text=f"{total_grupos} grupo(s) de duplicatas encontrado(s)."
            )
            # Habilita botão mover
            self._btn_mover.configure(
                state="normal",
                fg_color="#3a2a00",
                hover_color="#4a3800",
                border_color=COR_AMARELO,
                text_color=COR_AMARELO,
            )

        self._btn_verificar.configure(state="normal")

    # ------------------------------------------------------------------
    # Mover duplicatas
    # ------------------------------------------------------------------
    def _mover(self):
        if not self._duplicatas:
            messagebox.showwarning("Aviso", "Nenhuma duplicata encontrada ainda!")
            return

        if not self._pasta_destino:
            messagebox.showwarning("Aviso", "Selecione uma pasta de destino!")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Mover duplicatas para:\n{self._pasta_destino / 'Duplicatas'}\n\nContinuar?",
        )
        if not confirmar:
            return

        self._btn_mover.configure(state="disabled")
        self._status_label.configure(text="Movendo duplicatas...")

        threading.Thread(target=self._mover_thread, daemon=True).start()

    def _mover_thread(self):
        mensagens, total = dup.mover_duplicatas(self._duplicatas, self._pasta_destino)

        logger.registrar_muitos(mensagens)
        self._limpar_resultado()
        for m in mensagens:
            self._escrever(m)

        self._duplicatas = {}
        self._status_label.configure(text=f"Concluído — {total} arquivo(s) movido(s).")
        messagebox.showinfo("Concluído", f"{total} arquivo(s) duplicado(s) movido(s) para\n{self._pasta_destino / 'Duplicatas'}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _escrever(self, texto: str):
        self._resultado_box.configure(state="normal")
        self._resultado_box.insert("end", texto + "\n")
        self._resultado_box.see("end")
        self._resultado_box.configure(state="disabled")

    def _limpar_resultado(self):
        self._resultado_box.configure(state="normal")
        self._resultado_box.delete("1.0", "end")
        self._resultado_box.configure(state="disabled")
