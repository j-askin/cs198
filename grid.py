import PyQt5.QtWidgets as qtw
from PyQt5 import uic
import sys
from PIL import Image

class Grid(qtw.QMainWindow):
    def __init__(self, parent):
        super(Grid, self).__init__(parent)

        uic.loadUi("grid.ui", self)

        self.notif = qtw.QMessageBox()
        self.submitSize.clicked.connect(self.create_grid)
        self.show()
    
    def create_grid(self):
        v_count = self.lineEdit.text()
        v_space = self.lineEdit_2.text()
        h_count = self.lineEdit_3.text()
        h_space = self.lineEdit_4.text()

        v_count, v_space, h_count, h_space = self.error_handling(v_count, v_space, h_count, h_space)
        if v_count == None:
            return
        height = v_count + (v_count * v_space) - v_space
        width = h_count + (h_count * h_space) - h_space
        img = Image.new(mode="RGBA", size=(width, height))
        actual_grid = []
        counter = 0
        for i in range(height):
            for j in range(width):
                if i == 0 or counter > v_space:
                    actual_grid.append((0,255,255,255))
                elif j == 0 or j%(h_space+1) == 0:
                    actual_grid.append((0,255,255,255))
                else:
                    actual_grid.append((0,0,0,0))
            if counter > v_space:
                counter = 1
            else:
                counter += 1
        img.putdata(actual_grid)
        img.save("grid.png", "PNG")
        self.close()

    def error_handling(self, v_count, v_space, h_count, h_space):
        if not (v_count and v_space and h_count and h_space):
            err = self.show_error(0)
            return err

        for i in v_count:
            if ord(i) < 48 or ord(i) > 57:
                err = self.show_error(0)
                return err
        v_count = int(v_count)

        for i in v_space:
            if ord(i) < 48 or ord(i) > 57:
                err = self.show_error(0)
                return err
        v_space = int(v_space)

        for i in h_count:
            if ord(i) < 48 or ord(i) > 57:
                err = self.show_error(0)
                return err
        h_count = int(h_count)

        for i in h_space:
            if ord(i) < 48 or ord(i) > 57:
                err = self.show_error(0)
                return err
        h_space = int(h_space)

        if not (v_count and v_space and h_count and h_space):
            err = self.show_error(0)
            return err
        
        return v_count, v_space, h_count, h_space

    def show_error(self, x):
        self.notif.setIcon(qtw.QMessageBox.Critical)
        self.notif.setText("All inputs must be greater than 0.")
        self.notif.setWindowTitle("Error")
        self.notf.exec()

        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        return None, None, None, None

# app = qtw.QApplication(sys.argv)
# window = Grid()
# app.exec_()