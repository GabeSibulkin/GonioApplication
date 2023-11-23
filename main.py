import sys

# Assuming your main.py is in a directory that has Backend and Frontend as subdirectories
sys.path.append('./Backend')
sys.path.append('./Frontend')

from PyQt5 import QtWidgets, QtCore, QtGui
from servo_control import Ui_ControlPanelWindow
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow
from RunPopUp import Ui_RunOptionsDialog
from ModeRun import handle_start_button_click, RunManager
from Connection import StartingRunChecks

run_manager = RunManager()
class RunOptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RunOptionsDialog, self).__init__(parent)
        self.ui = Ui_RunOptionsDialog()
        self.ui.setupUi(self)
        self.applyStylingRunOptions()
        self.ui.pushButtonStart.clicked.connect(lambda: handle_start_button_click(self))


    def handleFileSelectionChanged(self, item):
        if item.checkState() == QtCore.Qt.Checked:
            print(f"File {item.text()} selected")
            # Add logic to handle file selection
        else:
            print(f"File {item.text()} deselected")
            # Add logic to handle file deselection

    def applyStylingRunOptions(self):
        try:
            with open('Frontend/RunPopUpStyle.css', 'r') as f:
                style = f.read()
                self.setStyleSheet(style)
                print("Stylesheet applied successfully.")
        except Exception as e:
            print("Error applying stylesheet:", e)


class ControlPanelApp(QtWidgets.QWidget, Ui_ControlPanelWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.applyStyling()
        self.importedFiles = []  # This will store the file paths
        self.load_file_paths()
        self.populate_file_management_list()
        self.setFocusPolicy(Qt.StrongFocus)

        # Get the screen resolution
        screen = QtWidgets.QApplication.primaryScreen()
        rect = screen.availableGeometry()

        # Calculate half the screen size and convert them to integers
        width = int(rect.width() * 0.5)
        height = int(rect.height() * 0.5)

        # Set the window size
        self.resize(width, height)

        # Optionally center the window
        self.move(rect.center() - self.rect().center())
        screen_height = self.screen().size().height()
        font_size = screen_height * 0.02  # Example: 2% of screen height

        # Create the QLineEdit and set the calculated font size
        line_edit = QLineEdit(self)
        font = QFont()
        font.setPointSizeF(font_size)
        line_edit.setFont(font)
        self.runButton.clicked.connect(self.show_run_options)
        self.importButton.clicked.connect(self.import_csv_files)

    def load_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as f:
                self.importedFiles = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("No previously imported files found.")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            print("key pressed left")
            run_manager.adjust_angle_if_indefinite(-10)
        elif event.key() == QtCore.Qt.Key_Right:
            run_manager.adjust_angle_if_indefinite(10)
            print("key pressed right")


    def populate_file_management_list(self):
        self.fileList.clear()
        for file_path in self.importedFiles:
            file_name = QtCore.QFileInfo(file_path).fileName()

            # Create the list item with a widget
            list_widget_item = QtWidgets.QListWidgetItem(self.fileList)
            file_widget = QtWidgets.QWidget()
            file_layout = QtWidgets.QHBoxLayout(file_widget)
            file_layout.setContentsMargins(10, 10, 10, 10)  # Adjust margins as needed

            # Create and add the label for the file name
            label = QtWidgets.QLabel(file_name)
            file_layout.addWidget(label, 1)  # Ensure label takes up available space

            # Create and add the 'X' button
            remove_button = QtWidgets.QPushButton()
            remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            remove_button.setObjectName("removeButton")
            remove_button.setText("✕")  # Unicode character for 'X' symbol
            remove_button.setFlat(True)  # Remove button styling
            remove_button.clicked.connect(lambda checked, i=list_widget_item: self.remove_file(i))

            file_layout.addWidget(remove_button, 0)  # Ensure button doesn't expand

            file_widget.setLayout(file_layout)
            list_widget_item.setSizeHint(file_widget.sizeHint())
            self.fileList.addItem(list_widget_item)
            self.fileList.setItemWidget(list_widget_item, file_widget)

    def import_csv_files(self):
        # Open file dialog to select CSV files
        options = QtWidgets.QFileDialog.Options()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, 
            "Import CSV files", 
            "", 
            "CSV Files (*.csv)", 
            options=options
        )
        for file in files:
            # Assuming this is part of a function within your UI class
            self.importedFiles.append(file)  # Add the full path to the list

            file_name = QtCore.QFileInfo(file).fileName()
            list_widget_item = QtWidgets.QListWidgetItem(self.fileList)

            file_widget = QtWidgets.QWidget()
            file_layout = QtWidgets.QHBoxLayout(file_widget)
            file_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding

            # Create and add the label for the file name
            label = QtWidgets.QLabel(file_name)
            file_layout.addWidget(label, 1)  # The 1 ensures the label takes up the available space, pushing the button right

            # Create and add the 'X' button
            remove_button = QtWidgets.QPushButton()
            remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Changes the cursor to a pointer
            remove_button.setObjectName("removeButton")
            remove_button.setText("✕")  # Unicode character for multiplication sign (commonly used as close or remove button)
            remove_button.setFlat(True)  # This will remove the button styling
            remove_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # Changes the cursor to a pointer
            remove_button.clicked.connect(lambda checked, i=list_widget_item: self.remove_file(i))

            file_layout.addWidget(remove_button, 0)  # The 0 here ensures that the button does not expand

            file_widget.setLayout(file_layout)
            list_widget_item.setSizeHint(file_widget.sizeHint())
            self.fileList.addItem(list_widget_item)
            self.fileList.setItemWidget(list_widget_item, file_widget)



    def remove_file(self, item):
        # Get the file name from the item
        file_name = self.fileList.itemWidget(item).findChild(QtWidgets.QLabel).text()

        # Remove the item from the QListWidget
        row = self.fileList.row(item)
        self.fileList.takeItem(row)

        # Find and remove the file path from the importedFiles list
        for file_path in self.importedFiles:
            if QtCore.QFileInfo(file_path).fileName() == file_name:
                self.importedFiles.remove(file_path)
                break

        # Update the imported_files.txt file
        self.save_file_paths()

        # If the run options dialog is open, update its file list
        if hasattr(self, 'run_options_dialog'):
            self.run_options_dialog.ui.fileListWidget.clear()
            for file_path in self.importedFiles:
                item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.run_options_dialog.ui.fileListWidget.addItem(item)


    def save_file_paths(self):
        with open('imported_files.txt', 'w') as f:
            for file_path in self.importedFiles:
                f.write(f"{file_path}\n")


    def applyStyling(self):
        try:
            with open('Frontend/MainPageStyle.css', 'r') as f:
                style = f.read()
                self.setStyleSheet(style)
                print("Stylesheet applied successfully.")  # Debugging line
        except Exception as e:
            print("Error applying stylesheet:", e)

    def closeEvent(self, event):
        self.save_file_paths()
        super().closeEvent(event)

    def load_file_paths(self):
        try:
            with open('imported_files.txt', 'r') as f:
                self.importedFiles = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            print("No previously imported files found.")

    def show_run_options(self):
        self.run_options_dialog = RunOptionsDialog(self)
        # Populate the file list in the RunOptionsDialog
        self.run_options_dialog.ui.fileListWidget.clear()
        for file_path in self.importedFiles:
            item = QtWidgets.QListWidgetItem(QtCore.QFileInfo(file_path).fileName())
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.run_options_dialog.ui.fileListWidget.addItem(item)
        self.run_options_dialog.show()

    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = ControlPanelApp()
    mainWindow.show()
    sys.exit(app.exec_())