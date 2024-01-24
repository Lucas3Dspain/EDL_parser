"""
Coding Test: Make UI to select an EDL, parse it and show the needed data.

"""
import re
import sys
from typing import Optional, List

from qtpy import QtCore, QtGui, QtWidgets


def parse_edl(file_path: str, pattern: str) -> List[str]:
    """
    Function to extract strings that match the provided regex pattern in the provided EDL file.

    :param file_path: Path to the EDL file.
    :param pattern: Regex pattern to match.
    :return: List of strings matching the pattern.
    """
    files = []
    with (open(file_path, 'r') as edl_file):
        for line in edl_file:
            if line.startswith('* FROM CLIP NAME:'):
                clip_info = line.split(': ')[1].strip()
                if re.match(pattern=pattern, string=clip_info) and clip_info not in files:
                    files.append(clip_info)
    return files


class Clip:
    """
    Object to represent a editorial clip
    """

    # todo: Add method/property to build path as season/episode/shot
    def __init__(self, name, shot, episode, season):
        self.name = name
        self.shot = shot
        self.episode = episode
        self.season = season

    @classmethod
    def from_file(cls, file_name):
        """
        Create a Clip object from a file. It will extract Season, Episode, shot from the file name.

        :param file_name: Name of the file.
        :return: Clip object.
        """
        prefix = file_name.split('-', 1)[0]
        season, episode, shot = re.match(r's(\d{2})e(\d{2})_(\d{3})', prefix).groups()

        formatted_season = 's' + season.zfill(2)
        formatted_episode = 'e' + episode.zfill(3)
        formatted_shot = shot.zfill(4)

        return cls(name=file_name,
                   shot=formatted_shot,
                   episode=formatted_episode,
                   season=formatted_season)


class FileSelectionWidget(QtWidgets.QWidget):
    file_filter = "EDL Files (*.edl);;All Files (*)"
    default_path = r"C:\Users\LucasMorante\Desktop\_Repos\BidayaMedia\CodingTest_Assignment"

    def __init__(self):
        super().__init__()

        self.file_path_line_edit = QtWidgets.QLineEdit(self)
        self.file_path_line_edit.setReadOnly(True)

        self.select_file_button = QtWidgets.QPushButton("Select File", self)
        self.select_file_button.clicked.connect(self.show_file_dialog)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.file_path_line_edit)
        layout.addWidget(self.select_file_button)

    def show_file_dialog(self):
        """
        Show a file dialog to select a file and update the file path line edit.
        """
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select File", self.default_path, self.file_filter, options=options
        )
        if file_path:
            self.file_path_line_edit.setText(file_path)


class ClipTableWidget(QtWidgets.QWidget):
    """
    Widget for displaying a table of Clip objects.
    """

    def __init__(self):
        super().__init__()

        # Create a table widget
        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Clip", "Shot", "Episode", "Season"])

        # Hide the row count number
        self.table_widget.verticalHeader().setVisible(False)

        # Set minimum width for each column
        self.table_widget.setMinimumWidth(40)

        # Enable sorting for the table
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Set up layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.table_widget)

    def populate_table(self, clips):
        """
        Populate the table with Clip objects.

        :param clips: List of Clip objects.
        """

        # self.table_widget.setRowCount(0)
        # self.table_widget.clearContents()

        for row, clip in enumerate(clips):
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QtWidgets.QTableWidgetItem(clip.name))
            self.table_widget.setItem(row, 1, QtWidgets.QTableWidgetItem(clip.shot))
            self.table_widget.setItem(row, 2, QtWidgets.QTableWidgetItem(clip.episode))
            self.table_widget.setItem(row, 3, QtWidgets.QTableWidgetItem(clip.season))


class EdlViewer(QtWidgets.QWidget):
    """
    Main application window for viewing EDL files.
    """
    window_name = 'EDL Viewer'
    window_icon = None

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # Main Window
        self.setWindowTitle(self.window_name)
        # self.setWindowIcon(QtGui.QIcon(filename=self.window_icon))

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # File Picker Widget
        self.filePickerWdg = FileSelectionWidget()
        self.main_layout.addWidget(self.filePickerWdg)

        # Table widget
        self.clipTableWdg = ClipTableWidget()
        self.main_layout.addWidget(self.clipTableWdg)

        # Generate Folders Button
        self.generateBtn = QtWidgets.QPushButton(text="Generate Folders")
        self.main_layout.addWidget(self.generateBtn)

    def connect_signals(self):
        # Changed File
        self.filePickerWdg.file_path_line_edit.textChanged.connect(self._update_file)

        # Generate Button
        self.generateBtn.clicked.connect(self._generate_folders)

    def _update_file(self):
        """
        Update the table data with the new EDL file.
        """
        """
        - parse new file
        - generate list of clips
        - update self.data with List[Clips]
        - Refresh table (if necessary)
        """
        print("Hit on _update_file")

        # Get EDL path
        self.edl_path = self.filePickerWdg.file_path_line_edit.text()

        # Get EDL matching files
        regex_pattern = r"s+[0-9]{2}e+[0-9]{2}_+[0-9]{3}-.+\.wav"
        files = parse_edl(self.edl_path, regex_pattern)
        clips = [Clip.from_file(f) for f in files]

        # Populate the table with data
        self.clipTableWdg.populate_table(clips)

    def _generate_folders(self):
        """
        Generate shot folders based on the Clip´s path.
        """
        """
        - get edl path to use as root dir
        - use optimized logic to build all paths robustly.
        """
        print("Hit on _generate_folders")
        return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = EdlViewer()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
