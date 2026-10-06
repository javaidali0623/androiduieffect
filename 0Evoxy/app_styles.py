from PyQt5.QtGui import QFont, QColor, QPalette

class AppStyles:

    label_font = QFont("Arial", 12)
    label_bold_font = QFont("Arial", 12)
    label_bold_font.setBold(True)
    label_small_font = QFont("Arial", 10)

    warn_css = "color: red;"
    info_css = "color: blue; "

