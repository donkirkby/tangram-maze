from pathlib import Path

from pymupdf import pymupdf
from space_tracer import LiveImage


class LivePdf(LiveImage):
    def __init__(self, pdf_path: Path, page: int = 0, dpi: int = 24) -> None:
        self.pdf_path = pdf_path
        self.page = page
        self.dpi = dpi
        self.converted_size = (0, 0)

    def convert_to_png(self) -> bytes:
        fitz_doc = pymupdf.open(self.pdf_path)
        page = fitz_doc.load_page(self.page)
        pixmap: pymupdf.Pixmap = page.get_pixmap(dpi=self.dpi)
        pixmap.set_pixel(0, 0, (255, 0, 0))
        pixmap.set_pixel(pixmap.w - 1, pixmap.h - 1, (255, 0, 0))
        self.converted_size = (pixmap.width, pixmap.height)
        return pixmap.tobytes()
