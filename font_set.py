from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_fonts():
    fonts_path = Path(__file__).with_name('fonts')
    fredoka_file = fonts_path / 'Fredoka_One' / 'FredokaOne-Regular.ttf'
    raleway_file = fonts_path / 'Raleway' / 'static' / 'Raleway-Regular.ttf'
    raleway_bold_file = fonts_path / 'Raleway' / 'static' / 'Raleway-Bold.ttf'
    raleway_italic_file = fonts_path / 'Raleway' / 'static' / 'Raleway-Italic.ttf'
    raleway_bold_italic_file = fonts_path / 'Raleway' / 'static' / 'Raleway-BoldItalic.ttf'
    # If we use the regular names, then there can be collisions between fonts in
    # SVG diagrams and the main body of the document.
    pdfmetrics.registerFont(TTFont("Heading", fredoka_file))
    pdfmetrics.registerFont(TTFont("Body", raleway_file))
    pdfmetrics.registerFont(TTFont("Body-Bold", raleway_bold_file))
    pdfmetrics.registerFont(TTFont("Body-Italic", raleway_italic_file))
    pdfmetrics.registerFont(TTFont("Body-BoldItalic", raleway_bold_italic_file))
    pdfmetrics.registerFontFamily('Body',
                                  'Body',
                                  'Body-Bold',
                                  'Body-Italic',
                                  'Body-BoldItalic')
