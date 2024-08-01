import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QBrush, QLinearGradient
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QRect, QTimer, QPoint

import icons_rc  # Import the compiled resource module
import white_icons_rc

def svg_to_pixmap(svg_path, size):
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

class SidebarButton(QPushButton):
    def __init__(self, text, icon_path, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)  # Add fixed height for buttons

        self.setStyleSheet("""
            QPushButton {
                background-color: #081A57;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                text-align: left;
                padding-left: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4E4E6B;
            }
        """)
        self.setIcon(QIcon(svg_to_pixmap(icon_path, QSize(24, 24))))
        self.setIconSize(QSize(24, 24))
        self.setText(text)
        self.setFont(QFont("Helvetica", 10, QFont.Bold))

    def set_icon_only(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #081A57;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                text-align: center;
                padding-left: 0px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4E4E6B;
            }
        """)
        self.setText("")

    def set_text_and_icon(self, text):
        self.setStyleSheet("""
            QPushButton {
                background-color: #081A57;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                text-align: left;
                padding-left: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4E4E6B;
            }
        """)
        self.setText(text)

class GradientHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)  # Set fixed height for the header

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#2031BA"))
        gradient.setColorAt(1, QColor("#030D26"))
        painter.fillRect(self.rect(), QBrush(gradient))

class RevolvingWidget(QWidget):
    def __init__(self, numbers, parent=None):
        super().__init__(parent)
        self.numbers = numbers
        self.current_index = 0

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Helvetica", 15, QFont.Bold))  # Adjust the font size here
        self.label.setStyleSheet("color: #6EC531; padding: 10px;")

        self.animation = QPropertyAnimation(self.label, b"pos")
        self.animation.setDuration(3000)  # Adjust the duration for speed (in milliseconds)
        self.animation.finished.connect(self.update_number)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.update_number()

    def resizeEvent(self, event):
        self.label.resize(self.size())  # Make the label size match the widget size
        super().resizeEvent(event)

    def update_number(self):
        self.label.setText(str(self.numbers[self.current_index]))
        self.current_index = (self.current_index + 1) % len(self.numbers)
        self.label.move(self.width(), 0)  # Start from the right
        self.animation.setStartValue(QPoint(self.width(), 0))
        self.animation.setEndValue(QPoint(-self.width(), 0))  # Move the label across the entire widget
        QTimer.singleShot(0, self.animation.start)  # Start the animation immediately after updating text and position



class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Energy Monitoring System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: transparent; color: #FFFFFF;")
        
        # Flag to track sidebar state
        self.sidebar_expanded = True

        # Main container widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header widget with layout
        self.header_widget = GradientHeader()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(0)
        # Add shadow effect to the header widget
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(15)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(5)
        shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.header_widget.setGraphicsEffect(shadow_effect)

        self.toggle_button = QPushButton()
        self.toggle_button.setFont(QFont("Helvetica", 20))
        svg_icon = svg_to_pixmap(":/white_icons.qrc/menu.svg", QSize(24, 24))  # Use the resource path
        self.toggle_button.setIcon(QIcon(svg_icon))
        self.toggle_button.setIconSize(QSize(24, 24))
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                border-radius: 5px;
                padding-left: 20px;
                padding-right: 20px;
            }
            QPushButton:hover {
                background-color: #4E4E6B;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        self.header_layout.addWidget(self.toggle_button, alignment=Qt.AlignLeft)
        self.header_label = QLabel("Energy Monitoring System")
        self.header_label.setFont(QFont("Helvetica", 20))
        self.header_label.setStyleSheet("color: #FFFFFF; padding: 10px;")
        self.header_layout.addWidget(self.header_label)
        self.header_layout.addStretch()

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("background-color: #081A57; z-index: 1;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(10)
        self.sidebar.setFixedWidth(200)  # Initial sidebar width

        # Add buttons to the sidebar
        buttons = [
            ("Steam Dashboard", ":/white_icons.qrc/droplet.svg"),
            ("Steam Leak Data", ":/white_icons.qrc/activity.svg"),
            ("Savings Opportunity", ":/white_icons.qrc/trending-up.svg"),
            ("Technical Trends", ":/white_icons.qrc/bar-chart-2.svg"),
            ("GHG Data", ":/white_icons.qrc/bar-chart-2.svg"),
            ("Scheduled Outlook", ":/white_icons.qrc/calendar.svg")
        ]
        self.sidebar_buttons = []
        for btn_text, icon_path in buttons:
            btn = SidebarButton(btn_text, icon_path)
            self.sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        # Add vertical spacer to push buttons to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sidebar_layout.addItem(spacer)

        # Add the bottom button with label and icon
        self.bottom_button = SidebarButton("Settings", ":/icons/settings.svg")
        self.sidebar_layout.addWidget(self.bottom_button)

        # Main content layout
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Example label in content area
        self.example_label = QLabel("Content Area")
        self.example_label.setFont(QFont("Arial", 16))
        self.example_label.setStyleSheet("padding: 10px; background-color: #6C63FF; border-radius: 10px;")
        self.example_label.setFixedSize(200, 300)
        content_container = QWidget()
        content_container.setLayout(QVBoxLayout())
        content_container.layout().addWidget(self.example_label)
        content_container.layout().addStretch()
        content_container.setStyleSheet("background-color: #CFC8FF;")  # Match the background color

        # Add sidebar and content to main layout
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(content_container)
        self.main_layout.addWidget(self.header_widget)  # Add header widget to the main layout
        self.main_layout.addLayout(self.content_layout)  # Add content layout to the main layout

        # Add revolving widget at the bottom
        self.revolving_widget = RevolvingWidget([123, 456, 789, 1011, 1213], self)
        self.revolving_widget.setFixedHeight(50)
        self.revolving_layout = QHBoxLayout()
        self.revolving_layout.addStretch()
        self.revolving_layout.addWidget(self.revolving_widget)
        self.revolving_layout.addStretch()
        
        self.main_layout.addLayout(self.revolving_layout)  # Add revolving layout to the main layout

        # Ensure the header widget overlaps the content area to show the shadow
        self.header_widget.raise_()



    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.setFixedWidth(50)
            for btn in self.sidebar_buttons:
                btn.set_icon_only()
            self.bottom_button.set_icon_only()
        else:
            self.sidebar.setFixedWidth(200)
            for btn, (text, _) in zip(self.sidebar_buttons, [
            ("Steam Dashboard", ":/icons/box.svg"),
            ("Steam Leak Data", ":/icons/box.svg"),
            ("Savings Opportunity", ":/icons/box.svg"),
            ("Technical Trends", ":/icons/box.svg"),
            ("GHG Data", ":/icons/box.svg"),
            ("Scheduled Outlook", ":/icons/box.svg")
            ]):
                btn.set_text_and_icon(text)
            self.bottom_button.set_text_and_icon("Help")
        self.sidebar_expanded = not self.sidebar_expanded

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
