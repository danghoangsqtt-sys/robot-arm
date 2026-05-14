"""
serial_comm.py – Lớp giao tiếp Serial an toàn đa luồng.

Một luồng nền liên tục đọc các dòng dữ liệu từ cổng serial
và đưa chúng vào một hàng đợi an toàn. GUI sẽ lấy dữ liệu từ
hàng đợi này thông qua cơ chế after() của Tk – tránh cập nhật widget chéo luồng.
"""

import threading
import queue
import serial
import serial.tools.list_ports


class SerialComm:
    """
    Quản lý một kết nối serial.

    Sử dụng:
        comm = SerialComm()
        comm.connect("/dev/ttyUSB0", 115200)
        comm.send("T")                    # gửi truy vấn trạng thái
        line = comm.poll()                # đọc không chặn
        comm.disconnect()
    """

    def __init__(self):
        self._ser: serial.Serial | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._rx_queue: queue.Queue[str] = queue.Queue()
        self._lock = threading.Lock()

    #  Quản lý kết nối (Connection management) 

    def connect(self, port: str, baud: int) -> None:
        """Mở cổng và khởi chạy luồng đọc. Báo lỗi serial.SerialException nếu thất bại."""
        with self._lock:
            self._ser = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=0.05,       # thời gian chờ ngắn giúp vòng lặp đọc phản hồi nhanh
                write_timeout=1.0,
            )
            self._running = True
            self._thread = threading.Thread(
                target=self._read_loop, name="serial-reader", daemon=True
            )
            self._thread.start()

    def disconnect(self) -> None:
        """Dừng luồng đọc và đóng cổng."""
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

    #  Gửi dữ liệu (Send) 

    def send(self, cmd: str) -> bool:
        """
        Ghi một chuỗi lệnh (tự động chèn ký tự xuống dòng ở cuối).
        Trả về False nếu không có kết nối hoặc ghi thất bại.
        """
        if not self.is_connected:
            return False
        try:
            with self._lock:
                self._ser.write((cmd.strip() + "\n").encode("ascii"))
            return True
        except serial.SerialException:
            return False

    #  Nhận dữ liệu (Receive) 

    def poll(self) -> str | None:
        """Trả về dòng dữ liệu tiếp theo nhận được, hoặc None."""
        try:
            return self._rx_queue.get_nowait()
        except queue.Empty:
            return None

    def flush_rx(self) -> None:
        """Loại bỏ bất kỳ dữ liệu đầu vào nào đang được đệm."""
        while not self._rx_queue.empty():
            try:
                self._rx_queue.get_nowait()
            except queue.Empty:
                break

    #  Luồng đọc nền (Background reader) 

    def _read_loop(self) -> None:
        """Luồng daemon: đọc các dòng dữ liệu và đưa vào hàng đợi."""
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
                # Cổng đã bị đóng hoặc bị ngắt kết nối
                self._running = False
                self._rx_queue.put("__DISCONNECTED__")   # cờ báo ngắt kết nối
                break

    #  Tiện ích (Utility) 

    @staticmethod
    def list_ports() -> list[str]:
        """Trả về danh sách tên các cổng serial khả dụng."""
        return sorted(p.device for p in serial.tools.list_ports.comports())
