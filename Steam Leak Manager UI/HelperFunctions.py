from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QSizePolicy
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgRenderer

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLabel, QHeaderView, QCheckBox, QApplication, QStyledItemDelegate
)
from PyQt5.QtGui import QFont, QColor, QBrush, QPalette
from PyQt5.QtCore import Qt, QSize
import icons_rc  # Import the compiled resource file
import sys



class Gradient_Card(QWidget):
    def __init__(self, title, content, title_colors, content_colors, icon_path=None):
        super().__init__()
        self.title_labels = []
        self.value_labels = []
        self.initial_width = None  # Store the initial width
        self.initUI(title, content, title_colors, content_colors, icon_path)

    def initUI(self, title, content, title_colors, content_colors, icon_path):
        # Title background
        if len(title_colors) == 1:
            title_style = f"background: {title_colors[0]};"
        else:
            title_gradient_stops = ", ".join([f"stop:{i/(len(title_colors)-1)} {color}" for i, color in enumerate(title_colors)])
            title_style = f"background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, {title_gradient_stops});"

        # Content background
        if len(content_colors) == 1:
            content_style = f"background: {content_colors[0]};"
        else:
            content_gradient_stops = ", ".join([f"stop:{i/(len(content_colors)-1)} {color}" for i, color in enumerate(content_colors)])
            content_style = f"background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, {content_gradient_stops});"

        # Create the section widget
        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(0)

        # Title section
        title_widget = QWidget()
        title_widget.setStyleSheet(title_style)
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_widget.setFixedHeight(60)

        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 14, QFont.Bold))  # Fixed font size
        title_label.setStyleSheet('color: #000000; background-color: transparent; border: none;')
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label, alignment=Qt.AlignCenter)

        title_widget.setLayout(title_layout)
        section_layout.addWidget(title_widget)
        self.title_labels.append((title_label, 14))  # Store the reference and initial size

        # Content section
        content_widget = QWidget()
        content_widget.setStyleSheet(content_style)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 20, 0, 20)
        content_layout.setSpacing(10)
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add content directly
        if isinstance(content, QWidget):
            content_layout.addWidget(content)
        else:
            # Create a semi-transparent white square that resizes
            white_square = QWidget()
            white_square.setStyleSheet("""
                background-color: rgba(255, 255, 255, 0.2);  /* White with 20% opacity */
                border-radius: 10px;  /* Match the card's border-radius */
            """)
            white_square_layout = QVBoxLayout()
            white_square_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside the white square
            white_square_layout.setSpacing(5)
            white_square.setLayout(white_square_layout)

            white_square.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            value_label = QLabel(content)
            value_label.setFont(QFont('Arial', 14, QFont.Bold))  # Fixed font size
            value_label.setStyleSheet('color: #FFFFFF; background-color: transparent; border: none;')
            value_label.setWordWrap(True)
            value_label.setAlignment(Qt.AlignCenter)
            white_square_layout.addWidget(value_label, alignment=Qt.AlignCenter)

            # Add the white square to the content layout, with extra space above and below
            content_layout.addWidget(white_square, alignment=Qt.AlignCenter)


        content_widget.setLayout(content_layout)
        section_layout.addWidget(content_widget)

        # Create a QFrame container to hold the gradient card
        container = QFrame()
        container.setFrameShape(QFrame.Box)
        container.setFrameShadow(QFrame.Raised)
        container.setStyleSheet("border: 2px solid #cccccc; border-radius: 10px;")

        # Add the gradient card to the container
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container.setLayout(container_layout)
        container_layout.addWidget(section)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(20)  # Increase the blur radius
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(8)  # Center the shadow to avoid clipping issues
        shadow_effect.setColor(QColor(0, 0, 0, 100))  # Make the shadow more subtle
        container.setGraphicsEffect(shadow_effect)

        # Add margin around the container to prevent clipping of shadow
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)  # Increase margins to avoid clipping
        main_layout.setSpacing(0)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        if not hasattr(self, 'initial_width') or self.initial_width is None or self.initial_width == 0:
            self.initial_width = self.width()

        super().resizeEvent(event)
        self.adjustFonts()

    def adjustFonts(self):
        if self.initial_width is None or self.initial_width == 0:
            return

        current_width = self.width()
        scale_factor = current_width / self.initial_width

        # Ensure the scale factor does not reduce the font size excessively
        min_scale_factor = 0.8  # Prevent fonts from shrinking below 80% of the original size
        scale_factor = max(min_scale_factor, scale_factor)

        for label, base_size in self.title_labels:
            new_size = max(14, int(base_size * scale_factor))
            label.setFont(QFont('Arial', new_size, QFont.Bold))

        for label, base_size in self.value_labels:
            new_size = max(14, int(base_size * scale_factor))
            label.setFont(QFont('Arial', new_size, QFont.Bold))


def svg_to_pixmap(svg_path, size):
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap



class ListData(QWidget):
    def __init__(self, column_count, column_names, products):
        super().__init__()
        self.checkbox_column_count = 1
        self.column_count = column_count + self.checkbox_column_count
        self.column_names = column_names
        self.products = products
        self.checkboxes = []
        self.initUI()

    def initUI(self):
        self.setStyleSheet("border: none;")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.table = QTableWidget()
        self.table.setColumnCount(self.column_count)
        self.table.setRowCount(len(self.products) + 1)  # +1 for the header row
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(70)
        self.table.setShowGrid(False)
        self.table.setColumnWidth(0, 30)

        # Set the stylesheet to include hover effect
        self.table.setStyleSheet("""
            QTableWidget::item {
                padding: 10px;
                background-color: #D3D3D3;  # Default background color
                color: #3f51b5;
            }
            QTableWidget::item:selected {
                background-color: #d0e7ff;  # Highlight color for selected item
            }
            QTableWidget::item:hover {
                background-color: #e0e0e0;  # Light gray background on hover
            }
            QTableWidget::item:checked {
                background-color: #c0c0c0;  # Checked state background color
            }
        """)
            

        header_checkbox_widget = QWidget()
        header_checkbox_layout = QHBoxLayout(header_checkbox_widget)
        header_checkbox_layout.setContentsMargins(0, 0, 0, 0)
        header_checkbox_layout.setAlignment(Qt.AlignVCenter)
        header_checkbox = QCheckBox()
        header_checkbox_layout.addWidget(header_checkbox)
        header_checkbox_widget.setLayout(header_checkbox_layout)
        self.table.setCellWidget(0, 0, header_checkbox_widget)
        header_checkbox.stateChanged.connect(self.select_all)

        for col, header in enumerate(self.column_names):
            item = QTableWidgetItem(header)
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            font = QFont('Helvetica', 10)
            font.setBold(True)
            item.setFont(font)
            item.setForeground(QColor('#3f51b5'))
            self.table.setItem(0, col + 1, item)  # Adjusted indexing to align with data

        self.populate_table_data()

        for i in range(1, self.column_count):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.table.setSelectionMode(QTableWidget.NoSelection)

        # Apply modern scroll bar styling only for the vertical scroll bar
        self.table.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                margin: 0px 2px 0px 2px;  /* Add space on the left and right side */
            }

            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 6px;  /* Rounded corners */
                min-height: 20px;
                margin: 2px;  /* Add space at the top and bottom */
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;  /* Hide the arrows */
            }

            QScrollBar::handle:vertical:hover {
                background: #555;  /* Darker gray on hover */
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        layout.addWidget(self.table)
        self.setLayout(layout)
        

    def populate_table_data(self):
        try:
            for row, product in enumerate(self.products, start=1):
                if len(product) != len(self.column_names):
                    raise ValueError(f"Data length mismatch at row {row}: {len(product)} vs {len(self.column_names)} expected")

                checkbox = QCheckBox()
                self.checkboxes.append(checkbox)
                self.table.setCellWidget(row, 0, checkbox)
                checkbox.stateChanged.connect(lambda state, r=row: self.highlight_row(r, state))

                for col, data in enumerate(product):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    item.setFont(QFont('Helvetica', 8))
                    item.setForeground(QColor('#3f51b5'))
                    self.table.setItem(row, col + 1, item)  # Align data with correct column
        except Exception as e:
            print(f"Error populating table: {e}")

    def select_all(self, state):
        checked = state == Qt.Checked
        for checkbox in self.checkboxes:
            checkbox.setChecked(checked)

    def highlight_row(self, row, state):
        highlight_color = QColor('#d0e7ff')
        default_color = self.table.palette().color(QPalette.Base)
        color = highlight_color if state == Qt.Checked else default_color
        for col in range(1, self.column_count):
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)
