from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel
from HelperFunctions import Gradient_Card

class Settings(QWidget):    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Create and add gradient cards
        title1 = "Cost Savings"
        content1 = "Potential savings of $50,000 annually."
        title_colors = ["#E0E0E0", "#FFFFFF"]
        content_colors = ["#2031BA", "#030D26"]

        gradient_card1 = Gradient_Card(title1, content1, title_colors, content_colors)
        layout.addWidget(gradient_card1)

        title2 = "Energy Reduction"
        content2 = "Potential reduction of 500 MWh per year."

        gradient_card2 = Gradient_Card(title2, content2, title_colors, content_colors)
        layout.addWidget(gradient_card2)

        # Repeat as necessary for more gradient cards
