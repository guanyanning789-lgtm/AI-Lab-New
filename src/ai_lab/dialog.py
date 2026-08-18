from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext

from .runtime.approval import PreviewApprovalSession


def launch_dialog(root: Path | None = None) -> None:
    session = PreviewApprovalSession(root or Path.cwd())

    window = tk.Tk()
    window.title("AI Lab")
    window.geometry("900x680")
    window.minsize(720, 520)

    history = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 12))
    history.pack(fill=tk.BOTH, expand=True, padx=16, pady=(16, 8))

    entry = tk.Entry(window, font=("Segoe UI", 12))
    entry.pack(fill=tk.X, padx=16, pady=(0, 8))

    def append(role: str, message: str) -> None:
        history.configure(state=tk.NORMAL)
        history.insert(tk.END, f"{role}\n{message}\n\n")
        history.configure(state=tk.DISABLED)
        history.see(tk.END)

    def send(_: object | None = None) -> None:
        text = entry.get().strip()
        if not text:
            return
        entry.delete(0, tk.END)
        append("你", text)
        try:
            reply = session.submit(text)
        except Exception as exc:
            append("AI Lab", f"無法建立或執行計劃：{exc}")
            return
        append("AI Lab", reply.message)

    send_button = tk.Button(window, text="發送", command=send, font=("Segoe UI", 11))
    send_button.pack(pady=(0, 16))

    entry.bind("<Return>", send)
    append(
        "AI Lab",
        "告訴我你要做什麼。我會先顯示執行計劃，不會立即修改。確認後請輸入「執行」。",
    )
    entry.focus_set()
    window.mainloop()
