from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QComboBox, QLabel, QSpacerItem
import sqlite3
from HelperFunctions import Gradient_Card
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import matplotlib.ticker as mticker
import locale
import matplotlib.dates as mdates
import numpy as np
import datetime
import sys
import pandas as pd
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QSpacerItem, QSizePolicy, QToolTip
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QPieSeries, QPieSlice
from PyQt5.QtCore import Qt, QDateTime, QPointF, QTimer
from PyQt5.QtGui import QPainter, QIcon, QFont, QColor, QCursor

locale.setlocale(locale.LC_ALL, '')



class PieChartCard(QWidget):
    def __init__(self, parent=None, selected_year=None):
        super().__init__(parent)
        self.selected_year = selected_year if selected_year is not None else datetime.datetime.now().year
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Create the pie chart series
        series = QPieSeries()

        # Fetch data from the database
        df = self.fetch_data_from_db()

        if not df.empty:
            # Populate the pie series with data from the database
            colors = [QColor(255, 69, 0), QColor(60, 179, 113), QColor(106, 90, 205), QColor(255, 105, 180)]  # Red, Green, Blue, Pink
            
            for i, row in df.iterrows():
                if row['total_loss_per_year'] > 0:  # Ensure that we only add meaningful slices
                    slice = QPieSlice(f"{row['Area']}: ${row['total_loss_per_year']:,.2f}", row['total_loss_per_year'])
                    slice.setLabelPosition(QPieSlice.LabelOutside)  # Move labels outside for better visibility
                    slice.setLabelVisible(True)
                    slice.setPen(QColor(0, 0, 0))  # Black border for slices
                    slice.setBrush(colors[i % len(colors)])  # Cycle through the color list
                    series.append(slice)

                    # Adjust label font size and color for better readability
                    slice.setLabelFont(QFont("Arial", 10, QFont.Bold))
                    slice.setLabelColor(Qt.white)  # Change to white for better contrast

            # Customize the chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Total Loss Per Year by Area")
            chart.setAnimationOptions(QChart.SeriesAnimations)

            # Customize the chart title and legend fonts
            font = QFont()
            font.setBold(True)
            font.setPointSize(14)
            chart.setTitleFont(font)
            chart.setTitleBrush(Qt.white)

            # Adjust legend font and position
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)  # Move legend to the right
            chart.legend().setFont(QFont("Arial", 10, QFont.Bold))
            chart.legend().setLabelColor(Qt.white)

            # Increase the size of the pie chart
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_view.setMinimumSize(600, 400)  # Adjust the size as needed

            # Set transparent background
            chart.setBackgroundBrush(Qt.transparent)
            chart_view.setStyleSheet("background: transparent;")

            # Adjust chart view settings
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            chart_view.setSizePolicy(sizePolicy)
            layout.addWidget(chart_view)
        else:
            print("No data available for the pie chart.")

        self.setLayout(layout)

    def fetch_data_from_db(self, db_path='SteamLeakDatabase.db'):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        query = """
        SELECT Area, SUM(LossPerYear) AS total_loss_per_year
        FROM leaks
        WHERE strftime('%Y', DateCompleted) = ?
        GROUP BY Area
        """
        # Use pandas to read the SQL query directly into a DataFrame
        df = pd.read_sql_query(query, conn, params=(str(self.selected_year),))
        conn.close()
        return df

class LineChartCard(QWidget):
    def __init__(self, parent=None, selected_year=None):
        super().__init__(parent)
        self.selected_year = selected_year if selected_year is not None else datetime.datetime.now().year
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.dropdown = QComboBox(self)
        self.dropdown.addItems(["LossPerYear", "SteamWaste"])
        self.dropdown.currentIndexChanged.connect(self.update_chart)

        # Style the dropdown
        self.dropdown.setStyleSheet("""
            QComboBox {
                background-color: #2031BA;
                color: #FFFFFF;
                padding: 5px;
                border-radius: 5px;
                border: 2px solid #FFFFFF;
                font-size: 12px;
                min-width: 150px;
            }
            QComboBox QAbstractItemView {
                background-color: #2031BA;
                color: #FFFFFF;
                selection-background-color: #3A5FCD;
            }
        """)

        dropdown_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        dropdown_layout.addItem(spacer)
        dropdown_layout.addWidget(self.dropdown)
        self.layout.addLayout(dropdown_layout)

        # Create the chart view
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.AllAnimations)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.layout.addWidget(self.chart_view)

        self.chart.setBackgroundBrush(Qt.transparent)
        self.chart_view.setStyleSheet("background: transparent;")

        self.update_chart()

    def update_chart(self):
        self.chart.removeAllSeries()

        selected_metric = self.dropdown.currentText()
        df = self.fetch_data_from_db()

        colors = {
            'East Plant 1': Qt.red,
            'East Plant 2': Qt.magenta,
            'Terminal': Qt.green,
            'West Plant': Qt.yellow
        }

        for area in df['Area'].unique():
            area_data = df[df['Area'] == area].sort_values('DateCompleted')
            cumulative_data = area_data[selected_metric].cumsum()

            series = QLineSeries()
            series.setName(area)
            series.setPointsVisible(True)

            for date, value in zip(area_data['DateCompleted'], cumulative_data):
                qdate_time = QDateTime(date)
                series.append(qdate_time.toMSecsSinceEpoch(), value)

            series.setColor(colors.get(area, Qt.white))
            self.chart.addSeries(series)

        axisX = QDateTimeAxis()
        axisX.setFormat("MMM yyyy")
        axisX.setTitleText("Date Completed")
        axisX.setTickCount(10)

        axisY = QValueAxis()
        axisY.setTickCount(6)
        axisY.setLabelFormat("%.1f")

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        
        axisX.setLabelsFont(font)
        axisX.setLabelsColor(Qt.white)
        axisX.setTitleFont(font)
        axisX.setTitleBrush(Qt.white)
        
        axisY.setLabelsFont(font)
        axisY.setLabelsColor(Qt.white)
        axisY.setTitleFont(font)
        axisY.setTitleBrush(Qt.white)

        if selected_metric == "SteamWaste":
            self.chart.setTitle("Cumulative Steam Waste Over Time (lb/yr)")
            axisY.setTitleText("Cumulative Steam Waste (lb/yr)")
        else:
            self.chart.setTitle("Cumulative Financial Loss Over Time ($)")
            axisY.setTitleText("Cumulative Financial Loss ($)")

        self.chart.setTitleFont(font)
        self.chart.setTitleBrush(Qt.white)

        legend = self.chart.legend()
        legend.setLabelColor(Qt.white)
        legend.setFont(font)

        self.chart.setAxisX(axisX)
        self.chart.setAxisY(axisY)

        for series in self.chart.series():
            series.attachAxis(axisX)
            series.attachAxis(axisY)

    def fetch_data_from_db(self, db_path='SteamLeakDatabase.db'):
        conn = sqlite3.connect(db_path)
        query = """
        SELECT Area, DateCompleted, LossPerYear, SteamWaste
        FROM leaks
        WHERE Status = 'Complete' AND strftime('%Y', DateCompleted) = ?
        """
        df = pd.read_sql_query(query, conn, params=(str(self.selected_year),))
        conn.close()
        df['DateCompleted'] = pd.to_datetime(df['DateCompleted'])
        df['LossPerYear'] = pd.to_numeric(df['LossPerYear'], errors='coerce') / 1e6
        df['SteamWaste'] = pd.to_numeric(df['SteamWaste'], errors='coerce') * 8760 / 1e6
        return df

    
class SteamDashboard(QWidget):
    def __init__(self, selected_year=None):
        super().__init__()
        self.selected_year = selected_year if selected_year is not None else datetime.datetime.now().year
        self.layout = QVBoxLayout()  # Initialize the layout directly
        self.setLayout(self.layout)  # Set the layout for the QWidget
        self.current_year = datetime.datetime.now().year  # Store the current year
        self.initUI()

    def initUI(self):
        # Clear the layout before adding new widgets
        self.clear_layout(self.layout)

        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        title_colors = ["#E0E0E0", "#FFFFFF"]
        content_colors = ["#2031BA", "#030D26"]

        # Stats Sections
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # Calculate the total steam loss from the database
        total_steam_loss = self.calculate_current_steam_loss_sum_db(self.selected_year)
        total_steam_leaks = self.calculate_current_steam_leaks_count_db(self.selected_year)
        total_energy_loss = self.calculate_current_sum_of_energy_loss(self.selected_year, unit_conversion=1e6)
        ytd_opportunity = self.calculate_ytd_savings(self.selected_year)
        future_savings = self.calculate_future_opportunity(self.selected_year)  # Placeholder for the new calculation

        steam_loss_card = Gradient_Card(f"Current Steam Loss for {self.current_year}", f"{total_steam_loss:.2f} Mlbs/h", title_colors, content_colors, ":/white_icons.qrc/droplet.svg")
        energy_consumption_card = Gradient_Card(f"Current Energy Consumption for {self.current_year}", f"{total_energy_loss:.2f} MMBTU/h", title_colors, content_colors, ":/white_icons.qrc/droplet.svg")
        steam_leaks_card = Gradient_Card(f"Current Outstanding Steam Leaks for {self.current_year}", f"{total_steam_leaks}", title_colors, content_colors, ":/white_icons.qrc/droplet.svg")

        stats_layout.addWidget(steam_loss_card)
        stats_layout.addWidget(energy_consumption_card)
        stats_layout.addWidget(steam_leaks_card)

        # Diagram Section
        diagram_layout = QHBoxLayout()
        diagram_layout.setSpacing(20)

        # Left vertical layout (for the pie chart)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        pie_chart_widget = PieChartCard(selected_year=self.selected_year)
        pie_chart_card = Gradient_Card(f"YTD Plant Area Leak Breakdown for {self.selected_year}", pie_chart_widget, title_colors, content_colors)
        left_layout.addWidget(pie_chart_card)

        # Right vertical layout (for the line chart and diagram)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(20)

        line_chart_widget = LineChartCard(selected_year=self.selected_year)
        line_chart_card = Gradient_Card(f"YTD Area Performance for {self.selected_year}", line_chart_widget, title_colors, content_colors)
        right_layout.addWidget(line_chart_card)

        # Horizontal layout for the YTD Opportunity and new card
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        ytd_opportunity_formatted = "${:,.2f}".format(ytd_opportunity)
        ytd_opportunity_card = Gradient_Card(f"YTD Savings for {self.selected_year}", ytd_opportunity_formatted, title_colors, content_colors, ":/white_icons.qrc/droplet.svg")
        bottom_layout.addWidget(ytd_opportunity_card)

        # Add the new "Future Savings" card
        future_savings_formatted = "${:,.2f}".format(future_savings)
        future_savings_card = Gradient_Card("Present Opportunity", future_savings_formatted, title_colors, content_colors, ":/white_icons.qrc/droplet.svg")
        bottom_layout.addWidget(future_savings_card)

        left_layout.addLayout(bottom_layout)
        
        line_chart_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Add the left and right layouts to the main diagram layout
        diagram_layout.addLayout(left_layout, 5)
        diagram_layout.addLayout(right_layout, 7)

        self.layout.addLayout(stats_layout, 3)
        self.layout.addLayout(diagram_layout, 7)

    def clear_layout(self, layout):
        """Helper method to clear all widgets from a layout."""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    self.clear_layout(child.layout())

    def update_dashboard_for_year(self, year):
        self.selected_year = year
        self.initUI()





    def calculate_current_steam_loss_sum_db(self, year):
        conn = sqlite3.connect('SteamLeakDatabase.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM("SteamWaste") 
            FROM leaks
            WHERE "Status" = "Complete"

        ''')
        result = cursor.fetchone()
        conn.close()

        total_loss = result[0] if result[0] is not None else 0.0
        return total_loss
    
    def calculate_current_steam_leaks_count_db(self, year):
        conn = sqlite3.connect('SteamLeakDatabase.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT("LeakID") 
            FROM leaks
            WHERE "Status" = "Complete"
        ''')
        result = cursor.fetchone()
        conn.close()

        total_leaks = result[0] if result[0] is not None else 0
        return total_leaks
    
    def calculate_current_sum_of_energy_loss(self, year, unit_conversion=1e3):
        conn = sqlite3.connect('SteamLeakDatabase.db')
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT SUM("EnergyLoss") 
                       FROM leaks
                       WHERE "Status" = "Complete"
                       ''')
        total_energy_loss = cursor.fetchone()[0]
        conn.close()

        # Convert units, e.g., from units to thousands
        total_energy_loss_converted = total_energy_loss / unit_conversion

        return total_energy_loss_converted

    def calculate_ytd_savings(self, year):
        conn = sqlite3.connect('SteamLeakDatabase.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM("LossPerYear") 
            FROM leaks
            WHERE "Status" = "Complete"
            AND strftime('%Y', "DateCompleted") = ?
        ''', (str(year),))
        
        result = cursor.fetchone()
        conn.close()

        ytd_opportunity = result[0] if result[0] is not None else 0
        return ytd_opportunity

    def calculate_future_opportunity(self, year):
        conn = sqlite3.connect('SteamLeakDatabase.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM("LossPerYear") 
            FROM leaks
            WHERE "Status" = "Pending"
        ''')
        result = cursor.fetchone()
        conn.close()

        ytd_opportunity = result[0] if result[0] is not None else 0
        return ytd_opportunity





    def update_steam_loss_card(self):
        total_loss = self.calculate_steam_loss_sum_db()
        steam_loss_card = Gradient_Card("Steam Loss", f"{total_loss:.2f} lbs/h", ["#E0E0E0", "#FFFFFF"], ["#2031BA", "#030D26"], ":/white_icons.qrc/droplet.svg")
        self.layout().itemAt(0).layout().replaceWidget(self.layout().itemAt(0).layout().itemAt(0).widget(), steam_loss_card)

    def update_energy_consumption_card(self):
        total_energy_loss = self.calculate_sum_of_energy_loss(unit_conversion=1e6)
        energy_consumption_card = Gradient_Card("Energy Consumption", f"{total_energy_loss:.2f} MMBTU", ["#E0E0E0", "#FFFFFF"], ["#2031BA", "#030D26"], ":/white_icons.qrc/droplet.svg")
        self.layout().itemAt(0).layout().replaceWidget(self.layout().itemAt(0).layout().itemAt(1).widget(), energy_consumption_card)

    def update_steam_leaks_card(self):
        total_leaks = self.calculate_steam_leaks_count_db()
        steam_leaks_card = Gradient_Card("Steam Leaks", f"{total_leaks}", ["#E0E0E0", "#FFFFFF"], ["#2031BA", "#030D26"], ":/white_icons.qrc/droplet.svg")
        self.layout().itemAt(0).layout().replaceWidget(self.layout().itemAt(0).layout().itemAt(2).widget(), steam_leaks_card)

    def update_ytd_opportunity_card(self):
        ytd_opportunity = self.calculate_ytd_opportunity()
        ytd_opportunity_formatted = "${:,.2f}".format(ytd_opportunity)  # Format with 2 decimal places and commas
        ytd_opportunity_card = Gradient_Card("YTD Opportunity", ytd_opportunity_formatted, ["#E0E0E0", "#FFFFFF"], ["#2031BA", "#030D26"], ":/white_icons.qrc/droplet.svg")
        self.layout().itemAt(1).layout().replaceWidget(self.layout().itemAt(1).layout().itemAt(2).widget(), ytd_opportunity_card)







