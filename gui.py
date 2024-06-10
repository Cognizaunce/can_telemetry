from typing import List
from PyQt6 import QtWidgets, uic
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd


class AppWindow(QtWidgets.QMainWindow):
    """
    Main window class for the GUI application.

    Args:
        ui_file_path (str): Path to the .ui file for the GUI
        app_dir (str): Directory of the specific app for reading resources like CSV files
        parent: Optional parent widget
    """

    def __init__(self, ui_file_path: str, app_dir: str, parent=None):
        """
        Initializes the MainWindow class.

        Args:
            ui_file_path (str): Path to the .ui file for the GUI
            app_dir (str): Directory of the specific app for reading resources like CSV files
            parent: Optional parent widget
        """
        super(AppWindow, self).__init__(parent)
        uic.loadUi(ui_file_path, self)
        self.app_dir = app_dir
        self.canvas = None
        self.graph_config = None

        self.button_layout = self.findChild(QtWidgets.QHBoxLayout, 'buttonLayout')
        if self.button_layout is None:
            raise ValueError("QHBoxLayout with object name 'buttonLayout' not found in the UI file.")

        self.plot_area = self.findChild(QtWidgets.QWidget, 'plotArea')
        if self.plot_area is None:
            raise ValueError("QWidget with object name 'plotArea' not found in the UI file.")

    def load_graph_config(self, config_file: str):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
                self.graph_config = config.get('plots', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading graph config: {e}")
            return

        for graph_name, graph_details in self.graph_config.items():
            button = QtWidgets.QPushButton(graph_name)
            button.clicked.connect(lambda _, g=graph_name: self.display_graph(g))
            self.button_layout.addWidget(button)

    def display_graph(self, graph_name: str):
        if self.canvas:
            self.canvas.setParent(None)
        self.canvas = FigureCanvas(plt.figure())
        self.plot_area.layout().addWidget(self.canvas)
        self.update_graph(graph_name)

    def update_graph(self, graph_name: str):
        graph_details = self.graph_config[graph_name]
        csv_file = f"{self.app_dir}/{graph_details['data']}"
        title = graph_details['title']

        try:
            data = pd.read_csv(csv_file)
            print(f"CSV columns: {data.columns}")  # Debug statement to print columns
        except FileNotFoundError as e:
            print(f"Error loading CSV file: {e}")
            return

        if data.shape[1] < 2:
            print("Error: CSV file does not have enough columns.")
            return

        # Use the last 20 rows for plotting
        last_20_entries = data.tail(20)

        x_data = last_20_entries.iloc[:, 0]
        y_data = last_20_entries.iloc[:, 1]

        ax = self.canvas.figure.add_subplot(111)
        ax.clear()
        ax.plot(x_data, y_data)
        ax.set_title(title)
        ax.set_xlabel(data.columns[0])  # Use the column name for x-axis
        ax.set_ylabel(data.columns[1])  # Use the column name for y-axis
        self.canvas.draw()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_file_path: str, apps_list: List[str]):
        """
        Initializes the MainWindow class. The UI file must have a QComboBox widget called "comboBox".

        Args:
            ui_file_path (str): Path to the .ui file for the GUI.
            apps_list (List[str]): List of apps to display in the QComboBox.
        """
        super().__init__()
        # Load the .ui file
        uic.loadUi(ui_file_path, self)

        # Get the QComboBox widget from the loaded UI
        self.combo_box = self.findChild(QtWidgets.QComboBox, 'comboBox')

        # Check if the QComboBox widget was found
        if self.combo_box is None:
            raise ValueError("QComboBox widget with object name 'comboBox' not found in the UI file.")

        # Populate the QComboBox widget with items from the list
        self.combo_box.addItems(apps_list)

        # Get the QPushButton widget from the loaded UI
        self.open_button = self.findChild(QtWidgets.QPushButton, 'openButton')

        # Check if the QPushButton widget was found
        if self.open_button is None:
            raise ValueError("QPushButton widget with object name 'openButton' not found in the UI file.")

        # Connect the button click event to the launch_app method
        self.open_button.clicked.connect(self.launch_app)

        # Variable to store the selected app directory
        self.selected_app = None

    def launch_app(self):
        """Handles the open button click event to launch the selected app."""
        # Get the selected item from the combo box
        self.selected_app = self.combo_box.currentText()
        # Close the main window
        self.close()
