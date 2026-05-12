"""
serial_comm.py – Thread-safe serial communication layer.

A background daemon thread continuously reads lines from the serial port
and puts them into a thread-safe queue.  The GUI polls that queue via
Tk's after() mechanism – no cross-thread widget updates.
"""

import threading
import queue
import serial
import serial.tools.list_ports


class SerialComm:
    """
    Manages one serial connection.

    Usage:
        comm = SerialComm()
        comm.connect("/dev/ttyUSB0", 115200)
        comm.send("T")                    # send status query
        line = comm.poll()                # non-blocking read
        comm.disconnect()
    """

    def __init__(self):
        self._ser: serial.Serial | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._rx_queue: queue.Queue[str] = queue.Queue()
        self._lock = threading.Lock()

    #  Connection management 

    def connect(self, port: str, baud: int) -> None:
        """Open port and start reader thread.  Raises serial.SerialException on failure."""
        with self._lock:
            self._ser = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=0.05,       # short timeout keeps reader loop responsive
                write_timeout=1.0,
            )
            self._running = True
            self._thread = threading.Thread(
                target=self._read_loop, name="serial-reader", daemon=True
            )
            self._thread.start()

    def disconnect(self) -> None:
        """Stop reader thread and close port."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.5)
            self._thread = None
        with self._lock:
            if self._ser and self._ser.is_open:
                self._ser.close()
            self._ser = None

    @property
    def is_connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    #  Send 

    def send(self, cmd: str) -> bool:
        """
        Write a command string (newline appended automatically).
        Returns False if not connected or write fails.
        """
        if not self.is_connected:
            return False
        try:
            with self._lock:
                self._ser.write((cmd.strip() + "\n").encode("ascii"))
            return True
        except serial.SerialException:
            return False

    #  Receive 

    def poll(self) -> str | None:
        """Return next available received line, or None."""
        try:
            return self._rx_queue.get_nowait()
        except queue.Empty:
            return None

    def flush_rx(self) -> None:
        """Discard any buffered incoming data."""
        while not self._rx_queue.empty():
            try:
                self._rx_queue.get_nowait()
            except queue.Empty:
                break

    #  Background reader 

    def _read_loop(self) -> None:
        """Daemon thread: reads lines and enqueues them."""
        while self._running:
            try:
                with self._lock:
                    ser = self._ser
                if ser and ser.is_open:
                    raw = ser.readline()
                    if raw:
                        line = raw.decode("ascii", errors="ignore").strip()
                        if line:
                            self._rx_queue.put(line)
            except serial.SerialException:
                # Port was closed or disconnected
                self._running = False
                self._rx_queue.put("__DISCONNECTED__")   # sentinel
                break

    #  Utility 

    @staticmethod
    def list_ports() -> list[str]:
        """Return a list of available serial port names."""
        return sorted(p.device for p in serial.tools.list_ports.comports())
