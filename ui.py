# ui.py

import sys
import configparser
import logger
import wget  # Import wget here
import streamClasses
import tools
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextEdit,
    QFileDialog,
    QListWidget,
    QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from typing import Optional, Any


class MainWindow(QMainWindow):
    """
    Main window for the M3U to STRM converter application.

    Provides a user interface for selecting an M3U file, configuring settings,
    and initiating the conversion process.
    """

    def __init__(self) -> None:
        """Initializes the MainWindow.

        Sets up the UI layout, connects signals to slots, and loads
        the initial configuration.
        """
        super().__init__()

        self.setWindowTitle(f"M3U to STRM Converter")

        # Main layout
        self.main_layout: QVBoxLayout = QVBoxLayout()

        # --- Input Section ---
        self.input_label: QLabel = QLabel("Input M3U:")
        self.input_line_edit: QLineEdit = QLineEdit()
        self.browse_button: QPushButton = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        input_layout: QHBoxLayout = QHBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line_edit)
        input_layout.addWidget(self.browse_button)
        self.main_layout.addLayout(input_layout)

        # --- Settings Section ---
        self.settings_label: QLabel = QLabel("Settings:")
        self.log_level_label: QLabel = QLabel("Log Level:")
        self.log_level_combo: QComboBox = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])

        self.output_dir_label: QLabel = QLabel("Output Directory:")
        self.output_dir_line_edit: QLineEdit = QLineEdit()

        self.movie_output_dir_label: QLabel = QLabel("Movie Output Directory:")
        self.movie_output_dir_line_edit: QLineEdit = QLineEdit()

        self.tvshow_output_dir_label: QLabel = QLabel("TV Show Output Directory:")
        self.tvshow_output_dir_line_edit: QLineEdit = QLineEdit()

        self.file_permissions_label: QLabel = QLabel("File Permissions:")
        self.file_permissions_line_edit: QLineEdit = QLineEdit()

        self.dir_permissions_label: QLabel = QLabel("Directory Permissions:")
        self.dir_permissions_line_edit: QLineEdit = QLineEdit()

        settings_layout: QVBoxLayout = QVBoxLayout()
        settings_layout.addWidget(self.settings_label)
        settings_layout.addWidget(self.log_level_label)
        settings_layout.addWidget(self.log_level_combo)
        settings_layout.addWidget(self.output_dir_label)
        settings_layout.addWidget(self.output_dir_line_edit)
        settings_layout.addWidget(self.movie_output_dir_label)
        settings_layout.addWidget(self.movie_output_dir_line_edit)
        settings_layout.addWidget(self.tvshow_output_dir_label)
        settings_layout.addWidget(self.tvshow_output_dir_line_edit)
        settings_layout.addWidget(self.file_permissions_label)
        settings_layout.addWidget(self.file_permissions_line_edit)
        settings_layout.addWidget(self.dir_permissions_label)
        settings_layout.addWidget(self.dir_permissions_line_edit)

        self.main_layout.addLayout(settings_layout)

        # --- Action Section ---
        self.process_button: QPushButton = QPushButton("Process M3U")
        self.process_button.clicked.connect(self.process_m3u)
        self.main_layout.addWidget(self.process_button)

        # --- Output Section ---
        self.output_text_edit: QTextEdit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        self.output_list_widget: QListWidget = QListWidget()

        output_layout: QVBoxLayout = QVBoxLayout()
        output_layout.addWidget(self.output_text_edit)
        output_layout.addWidget(self.output_list_widget)

        # --- Progress Bar ---
        self.progress_bar: QProgressBar = QProgressBar()
        output_layout.addWidget(self.progress_bar)

        self.main_layout.addLayout(output_layout)

        # Central widget
        central_widget: QWidget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Load initial configuration
        self.load_config()
        self.log = logger.Logger(__file__, logger.LogLevel.DEBUG)
        self.log.ui_emitter.log_signal.connect(self.log_message_received)

    def log_message_received(self, message: str) -> None:
        """Slot to receive log messages and display them in the UI."""
        self.output_text_edit.append(message)

    def set_progress_total(self, total: int) -> None:
        """Sets the maximum value of the progress bar."""
        self.progress_bar.setMaximum(total)

    def update_progress(self, value: int) -> None:
        """Updates the current value of the progress bar."""
        self.progress_bar.setValue(value)

    def browse_file(self) -> None:
        """Opens a file dialog to select an M3U file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select M3U File", "", "M3U Files (*.m3u)"
        )
        if file_path:
            self.input_line_edit.setText(file_path)

    def load_config(self) -> None:
        """Loads configuration from config.ini file and populates UI fields."""
        self.config: configparser.ConfigParser = configparser.ConfigParser()
        self.config.read("config.ini")

        input_m3u: str = self.config.get("paths", "input_m3u", fallback="")
        output_dir: str = self.config.get("paths", "output_dir", fallback="")
        log_level: str = self.config.get("settings", "log_level", fallback="INFO")
        movie_output_dir: str = self.config.get(
            "output_paths", "movie_output_dir", fallback="movies"
        )
        tvshow_output_dir: str = self.config.get(
            "output_paths", "tvshow_output_dir", fallback="tvshows"
        )
        file_permissions_str: str = self.config.get("output_paths", "file_permissions", fallback="644")
        dir_permissions_str: str = self.config.get("output_paths", "dir_permissions", fallback="755")

        self.input_line_edit.setText(input_m3u)
        self.output_dir_line_edit.setText(output_dir)
        self.log_level_combo.setCurrentText(log_level)
        self.movie_output_dir_line_edit.setText(movie_output_dir)
        self.tvshow_output_dir_line_edit.setText(tvshow_output_dir)
        self.file_permissions_line_edit.setText(file_permissions_str)
        self.dir_permissions_line_edit.setText(dir_permissions_str)

    def save_config(self) -> None:
        """Saves current UI settings to the config.ini file."""
        self.config["paths"]["input_m3u"] = self.input_line_edit.text()
        self.config["paths"]["output_dir"] = self.output_dir_line_edit.text()
        self.config["settings"]["log_level"] = self.log_level_combo.currentText()
        self.config["output_paths"]["movie_output_dir"] = self.movie_output_dir_line_edit.text()
        self.config["output_paths"]["tvshow_output_dir"] = self.tvshow_output_dir_line_edit.text()
        self.config["output_paths"]["file_permissions"] = self.file_permissions_line_edit.text()
        self.config["output_paths"]["dir_permissions"] = self.dir_permissions_line_edit.text()

        with open("config.ini", "w") as configfile:
            self.config.write(configfile)

    def process_m3u(self) -> None:
        """Processes the M3U file based on the current UI settings."""
        self.save_config()
        self.output_text_edit.clear()
        self.output_list_widget.clear()

        # Get settings from UI
        input_m3u: str = self.input_line_edit.text()
        log_level_str: str = self.log_level_combo.currentText()
        log_level: logger.LogLevel = getattr(logger.LogLevel, log_level_str, logger.LogLevel.INFO)

        # Download the M3U file if it's a URL
        if input_m3u.startswith("http"):
            self.output_text_edit.append(f"Downloading M3U from {input_m3u}...")
            try:
                local_m3u_path: str = "m3u/downloaded.m3u"  # Temporary local path
                wget.download(input_m3u, local_m3u_path)
                self.output_text_edit.append("Download complete.")
                input_m3u = local_m3u_path  # Use the local file
            except Exception as e:
                self.output_text_edit.append(f"Error downloading M3U: {e}")
                return
        elif not input_m3u.startswith("/") and not input_m3u.startswith("C:\\"):
            input_m3u = f"m3u/{input_m3u}"

        # Check if file exists
        if not tools.check_file_exists(input_m3u):
            self.output_text_edit.append(f"Error: M3U file not found at {input_m3u}")
            return

        # Process the M3U file
        try:
            stream_list: streamClasses.rawStreamList = streamClasses.rawStreamList(self.config, log_level)
            stream_list.progress_total.connect(self.set_progress_total)
            stream_list.progress_update.connect(self.update_progress)
            # Output the created filenames to the UI and list
            for filename in stream_list.streams.values():
                if filename:
                    self.output_list_widget.addItem(filename)
                    self.output_text_edit.append(f"Created: {filename}")

        except Exception as e:
            self.output_text_edit.append(f"An error occurred: {e}")

        self.output_text_edit.append("Processing finished.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
