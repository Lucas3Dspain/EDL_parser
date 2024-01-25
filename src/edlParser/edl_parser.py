"""
Coding Test: Make UI to select an EDL, parse it and show the needed data.

"""
import re
import sys
from typing import Optional, List

from qtpy import QtCore, QtGui, QtWidgets


# todo: fix column spacing
# todo: make columns expand horizontally to fit the text plus a margin. on update.
# todo: Add Clip method/property to build path as season/episode/shot -- for folder generation.
# todo: [before release] remove demo_edl and default_path
# todo: [before release] code-review variable names, formating, typing, docstrings

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

    def get_attributes(self):
        """
        Get attributes of the Clip object.

        :return: Dictionary containing attribute names and values.
        """
        return {attr: getattr(self, attr) for attr in vars(self) if not callable(getattr(self, attr)) and not attr.startswith("__")}


class FileSelectionWidget(QtWidgets.QWidget):
    file_filter = "EDL Files (*.edl);;All Files (*)"
    default_path = r"C:\Users\LucasMorante\Desktop\_Repos\BidayaMedia\CodingTest_Assignment"

    def __init__(self, parent=None):
        super(FileSelectionWidget, self).__init__(parent)

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


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, header_labels, parent=None):
        super(TableModel, self).__init__(parent)
        self._data = data
        self._header_labels = header_labels

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self.rowCount() > 0:
            clip_attributes = [attr for attr in self._data[0].get_attributes()]
            return len(clip_attributes)
        else:
            return 0

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            clip = self._data[index.row()]
            clip_attributes = [attr for attr in clip.get_attributes()]
            attribute_name = clip_attributes[index.column()]
            return str(getattr(clip, attribute_name))
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._header_labels[section]
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._data.sort(key=lambda x: getattr(x, list(x.get_attributes().keys())[column]))
        if order == QtCore.Qt.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()

    def update_data(self, new_data):
        """
        Update the underlying data of the model.

        :param new_data: New data to replace the current data.
        """
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()


class TableView(QtWidgets.QTableView):
    def __init__(self, model, parent=None):
        super(TableView, self).__init__(parent)
        self.setModel(model)

        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)

        # Set resize modes for the horizontal header
        # self.horizontalHeader().setStretchLastSection(False)
        # self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Custom)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Interactive)



class ClipTableWidget(QtWidgets.QWidget):
    """
    Widget for displaying a table of Clip objects.
    """

    def __init__(self, parent=None):
        super(ClipTableWidget, self).__init__(parent)

        # Create a table widget
        self.header_labels = ['Clip', 'Shot', 'Episode', 'Season']
        self.table_model = TableModel(data=[], header_labels=self.header_labels)
        self.table_view = TableView(model=self.table_model)

        # Set up layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.table_view)
        self.setLayout(main_layout)

    def populate_table(self, data):
        """
        Populate the table with Clip objects.

        :param data: List of Clip objects.
        """
        self.table_model.update_data(data)


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
    # DEMO
    demo_edl = "C:/Users/LucasMorante/Desktop/_Repos/BidayaMedia/CodingTest_Assignment/s01e10_v06_r30_06062022_FH.edl"
    widget.filePickerWdg.file_path_line_edit.setText(demo_edl)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
