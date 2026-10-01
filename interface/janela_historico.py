import threading
import customtkinter as ctk
from tkinter import messagebox

import historico as hist
import log as logger

COR_BG        = "#0e0e0e"
COR_PAINEL    = "#161616"
COR_BORDA     = "#222"
COR_AZUL      = "#1565C0"
COR_VERMELHO  = "#c0392b"
COR_TEXTO_DIM = "#555"
FONTE_MONO    = ("Consolas", 11)


class JanelaHistorico(ctk.CTkToplevel):
    """
    Janela para visualizar o histórico de operações e desfazê-las.
    """

    def __init__(self, master):
        super().__init__(master)
        self.title("Histórico de Operações")
        self.geometry("600x520")
        self.resizable(False, False)
        self.configure(fg_color=COR_BG)
        self.grab_set()

        self._operacoes = []
        self._selecionada = None
        self._build_ui()
        self._carregar_historico()

    def _build_ui(self):

        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header,
            text="HISTÓRICO",
            font=("Consolas", 20, "bold"),
            text_color=COR_AZUL,
        ).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=COR_BORDA).pack(fill="x", padx=24, pady=(0, 14))

        # Lista de operações
        ctk.CTkLabel(
            self,
            text="OPERAÇÕES REGISTRADAS",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(0, 4))

        self._lista_frame = ctk.CTkScrollableFrame(
            self,
            height=180,
            fg_color=COR_PAINEL,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._lista_frame.pack(fill="x", padx=24, pady=(0, 12))

        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 12))

        self._btn_desfazer = ctk.CTkButton(
            btn_frame,
            text="↩  Desfazer Selecionada",
            command=self._desfazer,
            corner_radius=8,
            height=38,
            font=("Consolas", 13, "bold"),
            fg_color="#3a0a0a",
            hover_color="#4a1010",
            border_width=1,
            border_color=COR_VERMELHO,
            text_color=COR_VERMELHO,
            state="disabled",
        )
        self._btn_desfazer.grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            btn_frame,
            text="🔄  Atualizar",
            command=self._carregar_historico,
            corner_radius=8,
            height=38,
            font=("Consolas", 12),
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#444",
            text_color="#888",
        ).grid(row=0, column=1, padx=6)

        # Log da operação de desfazer
        ctk.CTkLabel(
            self,
            text="RESULTADO",
            font=("Consolas", 10, "bold"),
            text_color=COR_TEXTO_DIM,
        ).pack(anchor="w", padx=26, pady=(0, 4))

        self._resultado_box = ctk.CTkTextbox(
            self,
            width=552,
            height=150,
            state="disabled",
            font=FONTE_MONO,
            fg_color=COR_PAINEL,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            text_color="#e57373",
            scrollbar_button_color="#222",
            scrollbar_button_hover_color="#333",
        )
        self._resultado_box.pack(padx=24, pady=(0, 16))

    def _carregar_historico(self):
        # Limpa lista
        for w in self._lista_frame.winfo_children():
            w.destroy()

        self._operacoes  = hist.listar_operacoes()
        self._selecionada = None
        self._btn_desfazer.configure(state="disabled")

        if not self._operacoes:
            ctk.CTkLabel(
                self._lista_frame,
                text="Nenhuma operação registrada ainda.",
                font=FONTE_MONO,
                text_color=COR_TEXTO_DIM,
            ).pack(pady=20)
            return

        for i, op in enumerate(self._operacoes):
            total  = len(op["movimentos"])
            modo   = op["modo"].upper()
            data   = op["data"]
            texto  = f"  {data}   [{modo}]   {total} arquivo(s)"

            btn = ctk.CTkButton(
                self._lista_frame,
                text=texto,
                anchor="w",
                font=FONTE_MONO,
                height=34,
                corner_radius=6,
                fg_color="#1e1e1e",
                hover_color="#2a2a2a",
                border_width=1,
                border_color="#2a2a2a",
                text_color="#888",
            )
            btn.configure(command=lambda b=btn, idx=i: self._selecionar(b, idx))
            btn.pack(fill="x", padx=6, pady=2)

    def _selecionar(self, botao: ctk.CTkButton, indice: int):
        # Desmarca todos
        for w in self._lista_frame.winfo_children():
            if isinstance(w, ctk.CTkButton):
                w.configure(border_color="#2a2a2a", text_color="#888")

        # Marca selecionado
        botao.configure(border_color=COR_VERMELHO, text_color="#e57373")
        self._selecionada = indice
        self._btn_desfazer.configure(state="normal")

    def _desfazer(self):
        if self._selecionada is None:
            return

        op    = self._operacoes[self._selecionada]
        total = len(op["movimentos"])

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Desfazer operação de {op['data']}?\n{total} arquivo(s) serão revertidos.",
        )
        if not confirmar:
            return

        self._btn_desfazer.configure(state="disabled")
        threading.Thread(
            target=self._desfazer_thread,
            args=(self._selecionada,),
            daemon=True,
        ).start()

    def _desfazer_thread(self, indice: int):
        mensagens, revertidos, erros = hist.desfazer_operacao(indice)

        logger.registrar_muitos(mensagens)
        self._limpar_resultado()
        for m in mensagens:
            self._escrever(m)

        self._carregar_historico()
        messagebox.showinfo(
            "Concluído",
            f"{revertidos} arquivo(s) revertido(s)\n{erros} erro(s)",
        )

    def _escrever(self, texto: str):
        self._resultado_box.configure(state="normal")
        self._resultado_box.insert("end", texto + "\n")
        self._resultado_box.see("end")
        self._resultado_box.configure(state="disabled")

    def _limpar_resultado(self):
        self._resultado_box.configure(state="normal")
        self._resultado_box.delete("1.0", "end")
        self._resultado_box.configure(state="disabled")
