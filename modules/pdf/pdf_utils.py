import fitz
import os


def pdf_to_image(pdf_path: str) -> str:
    """
    Convert the FIRST page of a PDF to PNG.
    Returns the PNG path.
    """

    doc = fitz.open(pdf_path)

    page = doc.load_page(0)

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    image_path = os.path.splitext(pdf_path)[0] + ".png"

    pix.save(image_path)

    doc.close()

    return image_path