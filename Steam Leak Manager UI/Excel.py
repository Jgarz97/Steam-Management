from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QStyledItemDelegate, QVBoxLayout, QWidget, QHeaderView, QStyleOptionButton, QStyle
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QRect, QEvent, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter

class QCheckboxDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()

        # Check if the checkbox is checked and apply green background to the whole row
        if index.data(Qt.CheckStateRole) == Qt.Checked:
            option.backgroundBrush = QColor("#66bb6a")  # Set the entire row background to green
            painter.fillRect(option.rect, QColor("#66bb6a"))

        check_box_style_option = QStyleOptionButton()

        if index.data() == Qt.Checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.get_check_box_rect(option)
        check_box_style_option.state |= QStyle.State_Enabled

        QApplication.style().drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)

        painter.restore()

    def get_check_box_rect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QPoint(int(option.rect.x() + option.rect.width() / 2 - check_box_rect.width() / 2),
                                int(option.rect.y() + option.rect.height() / 2 - check_box_rect.height() / 2))
        return QRect(check_box_point, check_box_rect.size())

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            current_state = index.data(Qt.CheckStateRole)
            new_state = Qt.Unchecked if current_state == Qt.Checked else Qt.Checked
            model.setData(index, new_state, Qt.CheckStateRole)

            # Trigger a full row update
            model.dataChanged.emit(index.siblingAtColumn(0), index.siblingAtColumn(model.columnCount() - 1))

            return True

        return super().editorEvent(event, model, option, index)

class CustomTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

        if role == Qt.CheckStateRole and index.column() == 0:
            return self._data[index.row()][index.column()]

        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | Qt.AlignLeft

        if role == Qt.FontRole:
            font = QFont("Arial", 10)
            return font

        if role == Qt.ForegroundRole:
            return QColor("#000000")  # Set text color

        if role == Qt.BackgroundRole:
            # Apply green background if the checkbox is checked
            if self._data[index.row()][0] == Qt.Checked:
                return QColor("#66bb6a")

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole and index.column() == 0:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index.siblingAtColumn(0), index.siblingAtColumn(self.columnCount() - 1), [Qt.BackgroundRole])
            return True
        return False

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = ["Select", "Order #", "Company name", "Status"]
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return headers[section]
        return QVariant()

    def flags(self, index):
        if index.column() == 0:  # Make the checkbox column checkable
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return Qt.ItemIsEnabled

# Sample data with fewer entries
data = [
    [Qt.Unchecked, "#SO-00001", "John Doe", "Pending"],
    [Qt.Unchecked, "#SO-00002", "Jane Smith", "Shipped"],
    [Qt.Unchecked, "#SO-00003", "Alice Brown", "Delivered"],
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal QTableView Example")
        self.setGeometry(100, 100, 800, 300)

        self.model = CustomTableModel(data)

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setShowGrid(False)  # Remove grid lines
        self.table_view.horizontalHeader().setStretchLastSection(True)

        # Apply custom delegate to the first column for checkboxes
        self.table_view.setItemDelegateForColumn(0, QCheckboxDelegate())

        self.table_view.setStyleSheet("""
            QTableView {
                border: none;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f3f3f3;
                color: black;
                font-weight: bold;
                padding: 5px;
            }
            QTableView::item:hover {
                background-color: #e0f7fa;
            }
            QTableView::item {
                padding: 5px;
                border: none;
            }
        """)

        self.table_view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_selection_changed(self, selected, deselected):
        # Prevent row color change on selection
        self.table_view.setStyleSheet("""
            QTableView {
                border: none;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f3f3f3;
                color: black;
                font-weight: bold;
                padding: 5px;
            }
            QTableView::item:hover {
                background-color: #e0f7fa;
            }
            QTableView::item {
                padding: 5px;
                border: none;
            }
            QTableView::item:selected {
                background-color: transparent;  # Make selected row transparent
            }
        """)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
