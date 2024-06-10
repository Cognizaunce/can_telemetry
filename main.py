"""Main application module.

This module serves as the entry point for the CAN Telemetry Application.
It initializes the telemetry backend and graphical user interface (GUI),
loads configuration settings, and manages the application lifecycle.

Attributes:
    None.
"""

import sys
import json
from typing import List
from PyQt6 import QtWidgets
from gui import AppWindow, MainWindow
from app_config import CANTelemetryAppConfig


def run_app(app_dir: str):
    """Run the selected telemetry application.

    Args:
        app_dir (str): Directory containing the app's configuration files.
    """
    # Load configuration settings from the app directory.
    config_file = f"{app_dir}/config.json"
    try:
        with open(config_file, 'r') as file:
            content = file.read()
            print(f"Contents of {config_file}:\n{content}")  # Print the contents for debugging
            config = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading app config: {e}")
        return

    gui_file = f"{app_dir}/{config['gui']}"
    graph_config_file = config_file

    # Initialize and display the graphical user interface (GUI) for the selected app.
    gui = QtWidgets.QApplication(sys.argv)
    app_window = AppWindow(gui_file, app_dir)
    app_window.load_graph_config(graph_config_file)
    app_window.show()

    try:
        # Run the GUI event loop for the app.
        gui.exec()
    except KeyboardInterrupt:  # Handle GUI closure by user.
        pass


if __name__ == "__main__":
    start = "start.json"
    # Open the file and read its contents
    try:
        with open(start, 'r') as file:
            content = file.read()
            if not content:
                print(f"The file {start} is empty.")
                sys.exit(1)  # Exit if the start file is empty
            else:
                print("Content:", content)
    except FileNotFoundError:
        print(f"The file {start} does not exist.")
        sys.exit(1)
    except IOError as e:
        print(f"An IOError occurred: {e}")
        sys.exit(1)

    # Load JSON data from a file
    try:
        app_list = json.loads(content)['list-of-app-directories']
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)  # Exit the program if JSON decoding fails

    # Now `app_list` contains the JSON content
    print("App List:", app_list)

    app = QtWidgets.QApplication(sys.argv)

    keep_running = True
    while keep_running:
        # Show the main window for app selection
        app_selector = MainWindow("main_window.ui", app_list)
        app_selector.show()

        # Run the GUI event loop for the main window
        app.exec()

        # Check if an app was selected
        selected_app = app_selector.selected_app
        if selected_app:
            # Run the selected app
            run_app(selected_app)
        else:
            keep_running = False  # Exit the loop if no app is selected

    # Exit the application
    sys.exit()
