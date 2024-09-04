import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QInputDialog, QStackedWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QWidget, QMenu, QLabel, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect, QAction, QMenuBar
)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QBrush, QLinearGradient
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QSize
import datetime
from SteamDashboardWidget import SteamDashboard
from TechnicalTrendsWidget import TechnicalTrends
from SteamLeakDataWidget import SteamLeakData
from SavingsOpportunityWidget import SavingsOpportunity
from GHGDataWidget import GHGData
from ScheduledOutlookWidget import ScheduledOutlook
import icons_rc  # Import the compiled resource module
import white_icons_rc
import sqlite3




# Helper function to convert SVG to QPixmap
def svg_to_pixmap(svg_path, size):
    renderer = QSvgRenderer(svg_path)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent) 
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

# Styles
button_styles = """
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
"""

button_icon_only_styles = """
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
"""

toggle_button_styles = """
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
"""

class SidebarButton(QPushButton):
    def __init__(self, text, icon_path, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet(button_styles)
        self.setIcon(QIcon(svg_to_pixmap(icon_path, QSize(24, 24))))
        self.setIconSize(QSize(24, 24))
        self.setText(text)
        self.setFont(QFont("Helvetica", 10, QFont.Bold))

    def set_icon_only(self):
        self.setStyleSheet(button_icon_only_styles)
        self.setText("")

    def set_text_and_icon(self, text):
        self.setStyleSheet(button_styles)
        self.setText(text)

class GradientHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#2031BA"))
        gradient.setColorAt(1, QColor("#030D26"))
        painter.fillRect(self.rect(), QBrush(gradient))

class GradientMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#2031BA"))
        gradient.setColorAt(1, QColor("#030D26"))
        painter.fillRect(self.rect(), QBrush(gradient))
        super().paintEvent(event)

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Steam Leak Management System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: transparent; color: #FFFFFF;")
        
        self.sidebar_expanded = True

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_header()
        self.setup_sidebar()
        self.setup_content()
        self.setup_menu_bar()
        
        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addLayout(self.content_layout)
        self.header_widget.raise_()

        self.resize(1800, 1000)  # You can set a default window size

    def setup_menu_bar(self):
        # Create a menu bar with gradient
        menubar = GradientMenuBar(self)
        self.setMenuBar(menubar)

        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2031BA;  /* Start of the gradient */
                color: #FFFFFF;  /* Text color */
            }
            QMenuBar::item {
                background-color: #2031BA;  /* Start of the gradient */
                color: #FFFFFF;  /* Text color */
            }
            QMenuBar::item:selected {
                background-color: #4E4E6B;  /* Hover effect */
            }
            QMenuBar::item:pressed {
                background-color: #030D26;  /* End of the gradient */
            }
            QMenu {
                background-color: #FFFFFF;  /* Force white background for dropdown menu */
                color: #000000;  /* Black text for menu items */
                border: 1px solid #CCCCCC;
            }
            QMenu::item {
                background-color: #FFFFFF;  /* White background for menu items */
                color: #000000;  /* Black text for menu items */
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #E5E5E5;  /* Light gray for hover on menu items */
                color: #000000;  /* Keep text black on hover */
            }
            QMenu::item:pressed {
                background-color: #CCCCCC;  /* Darker gray for pressed menu items */
                color: #000000;  /* Keep text black when pressed */
            }
            QMenu::separator {
                height: 1px;
                background-color: #CCCCCC;
                margin: 5px 0;
            }
        """)


        # Create File menu and add actions
        file_menu = menubar.addMenu('File')
        
        refresh_action = QAction('Refresh', self)
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.triggered.connect(self.refresh_dashboard)
        file_menu.addAction(refresh_action)

        # Create Data menu
        data_menu = menubar.addMenu('Steam Leak Data')

        insert_action = QAction('Insert Steam Leak', self)
        insert_action.setShortcut('Ctrl+L')
        data_menu.addAction(insert_action)

        # Add the "Select Year" submenu
        select_year_menu = QMenu('Select Year', self)
        self.populate_year_menu(select_year_menu)  # Pass the QMenu to populate it with year options
        data_menu.addMenu(select_year_menu)
        
        # Create Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        help_menu.addAction(about_action)

    def populate_year_menu(self, menu):
        # Fetch all available years from the database
        available_years = self.get_available_years()
        available_years.sort(reverse=True)

        # Add an option for the current year
        current_year = datetime.datetime.now().year

        # Add "Current Year" option
        current_year_action = QAction(f"Current Year ({current_year})", self)
        current_year_action.triggered.connect(lambda: self.update_dashboard_for_year(current_year))
        menu.addAction(current_year_action)

        # Add actions for each year
        for year in available_years:
            year_action = QAction(str(year), self)
            year_action.triggered.connect(lambda _, y=year: self.update_dashboard_for_year(int(y)))
            menu.addAction(year_action)

    def update_dashboard_for_year(self, year):
        self.selected_year = year
        self.steam_dashboard.update_dashboard_for_year(year)

    def get_available_years(self):
        # Connect to the SQLite database
        conn = sqlite3.connect('SteamLeakDatabase.db')
        cursor = conn.cursor()

        # Query to get distinct years from the DateCompleted column
        cursor.execute('''
            SELECT DISTINCT strftime('%Y', "DateCompleted") as Year
            FROM leaks
            WHERE "Status" = "Complete"
            ORDER BY Year DESC
        ''')
        years = cursor.fetchall()
        conn.close()

        # Extract the years from the query result
        return [year[0] for year in years]

    def setup_header(self):
        self.header_widget = GradientHeader()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(0)

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(15)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(5)
        shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.header_widget.setGraphicsEffect(shadow_effect)

        self.toggle_button = QPushButton()
        self.toggle_button.setFont(QFont("Helvetica", 20))
        svg_icon = svg_to_pixmap(":/white_icons.qrc/menu.svg", QSize(24, 24))
        self.toggle_button.setIcon(QIcon(svg_icon))
        self.toggle_button.setIconSize(QSize(24, 24))
        self.toggle_button.setStyleSheet(toggle_button_styles)
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        self.header_layout.addWidget(self.toggle_button, alignment=Qt.AlignLeft)
        self.header_label = QLabel("Energy Monitoring System")
        self.header_label.setFont(QFont("Helvetica", 20))
        self.header_label.setStyleSheet("color: #FFFFFF; padding: 10px;")
        self.header_layout.addWidget(self.header_label)
        self.header_layout.addStretch()

    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet("background-color: #081A57; z-index: 1;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(10)
        self.sidebar.setFixedWidth(200)

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

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.sidebar_layout.addItem(spacer)

        self.bottom_button = SidebarButton("Settings", ":/white_icons.qrc/settings.svg")
        self.sidebar_layout.addWidget(self.bottom_button)

    def setup_content(self):
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #D3D3D3; border: 1px solid #454F55")

        self.steam_dashboard = SteamDashboard()
        self.stacked_widget.addWidget(self.steam_dashboard)

        self.steamleak_data = SteamLeakData()
        self.stacked_widget.addWidget(self.steamleak_data)

        self.savings_opportunity = SavingsOpportunity()
        self.stacked_widget.addWidget(self.savings_opportunity)

        self.technical_trends = TechnicalTrends()
        self.stacked_widget.addWidget(self.technical_trends)

        self.ghg_data = GHGData()
        self.stacked_widget.addWidget(self.ghg_data)

        self.scheduled_outlook = ScheduledOutlook()
        self.stacked_widget.addWidget(self.scheduled_outlook)

        # Add more pages if needed
        for i in range(7):
            page = self.create_page(f"Page {i+1}")
            self.stacked_widget.addWidget(page)  # Index 3, 4, ...

        self.link_sidebar_buttons()

        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.stacked_widget)

    def refresh_dashboard(self):
        # Refresh the dashboard with the currently selected year
        self.update_dashboard_for_year(self.selected_year)

    def link_sidebar_buttons(self):
        # First button -> SteamDashboard
        self.sidebar_buttons[0].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Second button -> SteamLeakData
        self.sidebar_buttons[1].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # Third button -> SavingsOpportunity
        self.sidebar_buttons[2].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        # Third button -> TechnicalTrends
        self.sidebar_buttons[3].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        # Fourth button -> GHG Data
        self.sidebar_buttons[4].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))

        self.sidebar_buttons[5].clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))

        # Link other buttons to other pages if needed
        for i in range(6, len(self.sidebar_buttons)):
            self.sidebar_buttons[i].clicked.connect(lambda _, idx=i+1: self.stacked_widget.setCurrentIndex(idx))

        # Assuming bottom_button is for some other page, adjust the index accordingly
        self.bottom_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(7))  # Example index for the last page
    
    def create_page(self, title):
        page = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        page.setLayout(layout)
        return page

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar.setFixedWidth(50)
            for btn in self.sidebar_buttons:
                btn.set_icon_only()
            self.bottom_button.set_icon_only()
        else:
            self.sidebar.setFixedWidth(200)
            for btn, (text, _) in zip(self.sidebar_buttons, [
                ("Steam Dashboard", ":/white_icons.qrc/droplet.svg"),
                ("Steam Leak Data", ":/white_icons.qrc/activity.svg"),
                ("Savings Opportunity", ":/white_icons.qrc/trending-up.svg"),
                ("Technical Trends", ":/white_icons.qrc/bar-chart-2.svg"),
                ("GHG Data", ":/white_icons.qrc/bar-chart-2.svg"),
                ("Scheduled Outlook", ":/white_icons.qrc/calendar.svg")
            ]):
                btn.set_text_and_icon(text)
            self.bottom_button.set_text_and_icon("Settings")
        self.sidebar_expanded = not self.sidebar_expanded

def main():
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
