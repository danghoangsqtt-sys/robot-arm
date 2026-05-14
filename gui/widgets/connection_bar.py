"""
widgets/connection_bar.py – Thanh công cụ kết nối cổng Serial.

Cung cấp các nút để chọn cổng, chọn baud rate (tốc độ baud), nút kết nối/ngắt kết nối,
nút làm mới danh sách cổng và đèn LED báo trạng thái.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial

from config import C, BAUD_RATES, DEFAULT_BAUD, FONT_LABEL, FONT_BOLD, FONT_SMALL
from serial_comm import SerialComm


class ConnectionBar(tk.Frame):
    """
    Widget thanh trên cùng (top-bar) sở hữu đối tượng SerialComm và cung cấp
    các callback `on_connect` / `on_disconnect` để ứng dụng chính có thể phản hồi.
    """

    def __init__(self, master, comm: SerialComm,
                 on_connect=None, on_disconnect=None, **kwargs):
        super().__init__(master, bg=C["surface"], pady=6, padx=10, **kwargs)
        self._comm = comm
        self._on_connect    = on_connect
        self._on_disconnect = on_disconnect
        self._connected = False

        self._build()

    #  Xây dựng giao diện (Build UI) 

    def _build(self):
        #  Đèn LED trạng thái (LED indicator) 
        self._led = tk.Canvas(
            self, width=14, height=14,
            bg=C["surface"], highlightthickness=0
        )
        self._led_oval = self._led.create_oval(2, 2, 12, 12, fill=C["dim"], outline="")
        self._led.grid(row=0, column=0, padx=(0, 8))

        #  Trình chọn cổng (Port selector) 
        tk.Label(self, text="Port", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL).grid(row=0, column=1, padx=(0, 4))

        self._port_var = tk.StringVar()
        self._port_cb = ttk.Combobox(
            self, textvariable=self._port_var,
            width=14, state="readonly", font=FONT_LABEL
        )
        self._port_cb.grid(row=0, column=2, padx=(0, 6))

        # Nút làm mới danh sách cổng
        tk.Button(
            self, text="⟳", font=FONT_BOLD,
            bg=C["surface2"], fg=C["text"], relief="flat",
            activebackground=C["border"], activeforeground=C["text"],
            cursor="hand2", command=self._refresh_ports,
            width=2,
        ).grid(row=0, column=3, padx=(0, 12))

        #  Trình chọn tốc độ baud (Baud selector) 
        tk.Label(self, text="Baud", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL).grid(row=0, column=4, padx=(0, 4))

        self._baud_var = tk.StringVar(value=str(DEFAULT_BAUD))
        ttk.Combobox(
            self, textvariable=self._baud_var,
            values=[str(b) for b in BAUD_RATES],
            width=8, state="readonly", font=FONT_LABEL
        ).grid(row=0, column=5, padx=(0, 14))

        #  Nút Kết nối / Ngắt kết nối (Connect / Disconnect button) 
        self._btn = tk.Button(
            self, text="Connect", width=11, font=FONT_BOLD,
            bg=C["accent"], fg=C["bg"], relief="flat",
            activebackground=C["accent_dk"], activeforeground=C["bg"],
            cursor="hand2", command=self._toggle,
        )
        self._btn.grid(row=0, column=6, padx=(0, 16))

        #  Dòng trạng thái (Status text) 
        tk.Label(self, text="Status:", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL).grid(row=0, column=7, padx=(0, 4))
        self._status_var = tk.StringVar(value="Disconnected")
        tk.Label(
            self, textvariable=self._status_var,
            bg=C["surface"], fg=C["dim"], font=FONT_BOLD, width=20, anchor="w"
        ).grid(row=0, column=8)

        self._refresh_ports()

    #  Quản lý cổng (Port management) 

    def _refresh_ports(self):
        ports = SerialComm.list_ports()
        self._port_cb["values"] = ports
        if ports and not self._port_var.get():
            self._port_var.set(ports[0])

    #  Kết nối / Ngắt kết nối (Connect / disconnect) 

    def _toggle(self):
        if self._connected:
            self._do_disconnect()
        else:
            self._do_connect()

    def _do_connect(self):
        port = self._port_var.get()
        baud = int(self._baud_var.get())
        if not port:
            messagebox.showerror("Connection", "Select a serial port first.")
            return
        try:
            self._comm.connect(port, baud)
            self._set_connected(True)
            if self._on_connect:
                self._on_connect(port, baud)
        except serial.SerialException as exc:
            messagebox.showerror("Connection Error", str(exc))

    def _do_disconnect(self):
        self._comm.disconnect()
        self._set_connected(False)
        if self._on_disconnect:
            self._on_disconnect()

    def _set_connected(self, state: bool):
        self._connected = state
        if state:
            self._led.itemconfig(self._led_oval, fill=C["green"])
            self._btn.config(text="Disconnect", bg=C["red"])
            self._status_var.set(f"Connected  –  {self._port_var.get()}")
            self._update_status_color(C["green"])
        else:
            self._led.itemconfig(self._led_oval, fill=C["dim"])
            self._btn.config(text="Connect", bg=C["accent"])
            self._status_var.set("Disconnected")
            self._update_status_color(C["dim"])

    # Được gọi bởi ứng dụng chính khi có cờ báo ngắt kết nối đột ngột
    def force_disconnect(self):
        self._set_connected(False)

    def _update_status_color(self, color: str):
        for w in self.winfo_children():
            if isinstance(w, tk.Label) and w["textvariable"] == str(self._status_var):
                w.config(fg=color)
                return
        # Cách dự phòng: tìm kiếm dựa trên vị trí lưới (grid)
        for w in self.grid_slaves(row=0, column=8):
            if isinstance(w, tk.Label):
                w.config(fg=color)

    #  Các hàm Public (Public) 

    def set_status(self, text: str, color: str | None = None):
        self._status_var.set(text)
        if color:
            self._update_status_color(color)
