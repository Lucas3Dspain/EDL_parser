"""
Coding Test: Make UI to select an EDL, parse it and show the needed data.
"""

import os
import re
import sys
from typing import Dict, List, Optional

from qtpy import QtCore, QtWidgets


ITEM_DATA_ROLE = QtCore.Qt.UserRole + 1
DEFAULT_SEARCH_PATH = r"C:\Users\LucasMorante\Desktop\_Repos\BidayaMedia\CodingTest_Assignment"


def parse_edl(file_path: str, pattern: str) -> List[str]:
    """
    Function to extract strings that match the provided regex pattern in the provided EDL file.

    Parameters
    ----------
    file_path: str
        Fullpath of the EDL file.
    pattern: str
        Regex pattern.

    Returns
    -------
    List[str]
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
    def __init__(self, name, shot, episode, season):
        self.name = name
        self.shot = shot
        self.episode = episode
        self.season = season

    @classmethod
    def from_file(cls, file_name: str) -> Optional['Clip']:
        """
        Create a Clip object from a file. It will extract Season, Episode, shot from the file name.

        Parameters
        ----------
        file_name: str
            Fullpath of the EDL file.

        Returns
        -------
        Optional['Clip']
        """
        prefix = file_name.split('-', 1)[0]
        match = re.match(r's(\d{2})e(\d{2})_(\d{3})', prefix)
        if not match:
            return None
        season, episode, shot = match.groups()

        formatted_season = 's' + season.zfill(2)
        formatted_episode = 'e' + episode.zfill(3)
        formatted_shot = 's' + shot.zfill(4)

        return cls(name=file_name,
                   shot=formatted_shot,
                   episode=formatted_episode,
                   season=formatted_season)

    def get_attributes(self) -> Dict[str, str]:
        """
        Get attributes of the Clip object.

        Returns
        -------
        Dict[str, str]
            Dictionary containing attribute names and values.
        """
        return {attr: getattr(self, attr) for attr in vars(self)
                if not callable(getattr(self, attr)) and not attr.startswith("__")}


class FileSelectionWidget(QtWidgets.QWidget):
    file_filter = "EDL Files (*.edl);;All Files (*)"

    def __init__(self, parent=None):
        super(FileSelectionWidget, self).__init__(parent)

        # Main Layout
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.file_path_line_edit = QtWidgets.QLineEdit(parent=self)
        self.file_path_line_edit.setReadOnly(True)

        self.select_file_button = QtWidgets.QPushButton(parent=self, text="Select File")
        self.select_file_button.clicked.connect(self.show_file_dialog)

        layout.addWidget(self.file_path_line_edit)
        layout.addWidget(self.select_file_button)

    def show_file_dialog(self):
        """
        Show a file dialog to select a file and update the file path line edit.
        """
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select File", DEFAULT_SEARCH_PATH, self.file_filter, options=options
        )
        if file_path:
            self.file_path_line_edit.setText(file_path)


class CenterTextDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() > 0:
            option.displayAlignment = QtCore.Qt.AlignCenter
        super().paint(painter, option, index)


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
        clip = self._data[index.row()]
        if role == QtCore.Qt.DisplayRole:
            clip_attributes = [attr for attr in clip.get_attributes()]
            attribute_name = clip_attributes[index.column()]
            return str(getattr(clip, attribute_name))
        elif role == ITEM_DATA_ROLE:
            return clip
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._header_labels[section]
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def sort(self, column: int, order: QtCore.Qt.SortOrder = QtCore.Qt.AscendingOrder) -> None:
        self.layoutAboutToBeChanged.emit()
        self._data.sort(key=lambda x: getattr(x, list(x.get_attributes().keys())[column]))
        if order == QtCore.Qt.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()

    def update_data(self, new_data):
        """
        Update the underlying data of the model.

        Parameters
        ----------
        new_data: List[Clip]
            New data to replace the current data.

        Returns
        -------
        None
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
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        center_text_delegate = CenterTextDelegate(parent)
        self.setItemDelegate(center_text_delegate)


class ClipTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ClipTableWidget, self).__init__(parent)

        # Create a table widget
        header_labels = ['Clip', 'Shot', 'Episode', 'Season']
        self.table_model = TableModel(data=[], header_labels=header_labels)
        self.table_view = TableView(model=self.table_model)

        # Set up layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.table_view)
        self.setLayout(main_layout)

    def populate_table(self, data):
        """
        Populate the table with Clip objects.

        Parameters
        ----------
        data: List[Clip]
            List of Clip objects.

        Returns
        -------
        None
        """
        self.table_model.update_data(data)


class EdlViewer(QtWidgets.QWidget):
    window_name = 'EDL Viewer'

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.init_ui()
        self.connect_signals()
        self.resize(self.clipTableWdg.table_view.sizeHint())

    def init_ui(self):
        # Main Window
        self.setWindowTitle(self.window_name)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # File Picker Widget
        self.filePickerWdg = FileSelectionWidget(parent=self)
        self.main_layout.addWidget(self.filePickerWdg)

        # Table widget
        self.clipTableWdg = ClipTableWidget(parent=self)
        self.main_layout.addWidget(self.clipTableWdg)

        # Generate Folders Button
        self.generateBtn = QtWidgets.QPushButton(text="Generate Folders", parent=self)
        self.main_layout.addWidget(self.generateBtn, alignment=QtCore.Qt.AlignRight)

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

        # Resize
        header_width = self.clipTableWdg.table_view.horizontalHeader().length()
        self.clipTableWdg.setMinimumWidth(header_width+17)

    def _generate_folders(self):
        """
        Generate shot folders based on the Clip´s path.
        """
        edl_dir = os.path.dirname(self.edl_path)

        shot_paths = []
        for i in range(self.clipTableWdg.table_model.rowCount()):
            index = self.clipTableWdg.table_model.index(i, 0)
            clip = self.clipTableWdg.table_model.data(index, ITEM_DATA_ROLE)
            shot_path = f"{edl_dir}/{clip.season}/{clip.episode}/{clip.episode}{clip.shot}"
            shot_paths.append(shot_path)

        for path in set(shot_paths):
            os.makedirs(path, exist_ok=True)


def main():
    import qtawesome
    app = QtWidgets.QApplication(sys.argv)
    qtawesome.dark(app)
    widget = EdlViewer()
    widget.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
