import sys
import os

from PIL import Image

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QMessageBox
)

from PyQt6.QtCore import Qt


BLACK_THRESHOLD = 10


class DropLabel(QLabel):
    def __init__(self, callback):
        super().__init__()

        self.callback = callback

        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setText(
            "拖入图片\n\n或点击下方按钮选择"
        )

        self.setStyleSheet("""
            QLabel{
                border:2px dashed #888;
                border-radius:12px;
                font-size:18px;
                color:#666;
                background:white;
            }
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()

        if urls:
            self.callback(
                urls[0].toLocalFile()
            )


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("黑色像素修正")
        self.resize(420, 280)

        layout = QVBoxLayout(self)

        self.drop = DropLabel(self.process_file)

        layout.addWidget(self.drop)

        btn = QPushButton("选择图片")
        btn.clicked.connect(self.select_file)

        layout.addWidget(btn)

        self.status = QLabel("")
        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(self.status)

    def select_file(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if path:
            self.process_file(path)

    def process_file(self, path):

        try:

            img = Image.open(path).convert("RGBA")

            pixels = img.load()

            w, h = img.size

            changed = 0

            for y in range(h):
                for x in range(w):

                    r, g, b, a = pixels[x, y]

                    if (
                        r <= BLACK_THRESHOLD
                        and g <= BLACK_THRESHOLD
                        and b <= BLACK_THRESHOLD
                    ):
                        pixels[x, y] = (
                            0,
                            0,
                            0,
                            a
                        )

                        changed += 1

            folder = os.path.dirname(path)

            name = os.path.splitext(
                os.path.basename(path)
            )[0]

            output_path = os.path.join(
                folder,
                f"{name}_blackfix.png"
            )

            img.save(output_path)

            self.status.setText(
                f"完成\n修改像素:{changed}\n{os.path.basename(output_path)}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "错误",
                str(e)
            )


if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = Window()

    win.show()

    sys.exit(app.exec())