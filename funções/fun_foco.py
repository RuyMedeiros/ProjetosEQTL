import tkinter as tk

# -- Função para foco

def askstring_focus(title, prompt, parent=None):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.grab_set()  # Faz a janela modal
    dialog.transient(parent)

    tk.Label(dialog, text=prompt, font=("Segoe UI", 10)).pack(padx=20, pady=(20, 10))

    entry = tk.Entry(dialog, font=("Segoe UI", 10), width=40)
    entry.pack(padx=20, pady=(0, 20))
    entry.focus_force()  # Força o foco no campo

    result = {"value": None}

    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=(0, 15))

    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Cancelar", width=10, command=on_cancel).pack(side=tk.LEFT, padx=5)

    dialog.bind("<Return>", lambda e: on_ok())
    dialog.bind("<Escape>", lambda e: on_cancel())

    # Centraliza na tela
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_reqwidth() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_reqheight() // 2)
    dialog.geometry(f"+{x}+{y}")

    parent.wait_window(dialog)  # Espera a janela ser fechada
    return result["value"]