import customtkinter as ctk


class FrameBotoes(ctk.CTkFrame):

    def __init__(self, master, config: dict, on_organizar, on_copiar, on_cancelar, on_toggle_dll, on_duplicatas, on_historico, on_configuracoes, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        ctk.CTkButton(
            self,
            text="▶  Mover",
            command=on_organizar,
            corner_radius=8,
            height=38,
            font=("Consolas", 13, "bold"),
            fg_color="#1DB954",
            hover_color="#17a349",
            text_color="#0a0a0a",
        ).grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            self,
            text="⧉  Copiar",
            command=on_copiar,
            corner_radius=8,
            height=38,
            font=("Consolas", 13, "bold"),
            fg_color="#1565C0",
            hover_color="#0d47a1",
            text_color="#e0e0e0",
        ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            self,
            text="✕  Cancelar",
            command=on_cancelar,
            corner_radius=8,
            height=38,
            font=("Consolas", 13),
            fg_color="#2a2a2a",
            hover_color="#3a3a3a",
            border_width=1,
            border_color="#444",
        ).grid(row=0, column=2, padx=6)

        ctk.CTkButton(
            self,
            text="↩  Histórico",
            command=on_historico,
            corner_radius=8,
            height=38,
            font=("Consolas", 12),
            fg_color="#3a0a0a",
            hover_color="#4a1010",
            border_width=1,
            border_color="#c0392b",
            text_color="#c0392b",
        ).grid(row=0, column=3, padx=6)

        ctk.CTkButton(
            self,
            text="⚙  Config",
            command=on_configuracoes,
            corner_radius=8,
            height=38,
            font=("Consolas", 12),
            fg_color="#2a2a2a",
            hover_color="#333",
            border_width=1,
            border_color="#555",
            text_color="#aaa",
        ).grid(row=0, column=4, padx=6)
