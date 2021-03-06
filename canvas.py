# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPolygon
from PyQt5.QtWidgets import QMenu,  QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QRect
import re
import copy

class Canvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(30, 30, 600, 400)

        self.show()
        self.rect_list = []
        self.code_string = ""
        self.error = 0
        self.intersect = 0
        self.forbidden_module_names = ["input", "output", "inout", "module", "endmodule", ""]

    # All canvas painting actions are handled here.
    def paintEvent(self, event):
        qp = QtGui.QPainter(self)

        for r in self.rect_list:
            qp.setBrush(QtGui.QBrush(QtGui.QColor(100, 10, 10, 40)))     # module color
            qp.drawRect(QtCore.QRect(r.rect_begin, r.rect_end))  # Draw module rectangle
            qp.drawText((r.rect_begin + r.rect_end) / 2, r.center_text)  # Write the name of module rectangle

            in_order = 0
            out_order = 0
            inout_order = 0

            # Draw input ports and their names
            for i in r.in_port_list:
                # Write the port name
                qp.drawText(r.rect_begin + QtCore.QPoint(5, int(r.Tri_In_F / 2 + r.Tri_In_F * in_order)), i.text)
                in_order = in_order + 1

                polygon = QPolygon(i.points)
                qp.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 255, 127)))     # input port color
                qp.drawPolygon(polygon)

            # Draw output ports and their names
            for i in r.out_port_list:
                # Write the port name
                qp.drawText(r.rect_end + QtCore.QPoint(int(r.Tri_In_H + 5), int(-(r.rect_end.y() - r.rect_begin.y()) + r.Tri_In_F / 2 + r.Tri_In_F * out_order)), i.text)
                out_order = out_order + 1

                polygon = QPolygon(i.points)
                qp.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 255, 127)))     # output port color
                qp.drawPolygon(polygon)

            # Draw inout ports and their names
            for i in r.inout_port_list:
                # Write the port name
                qp.drawText(QtCore.QPoint(int(r.rect_begin.x() + 5), int(r.rect_end.y() - r.Tri_In_F / 2 - r.Tri_In_F * inout_order)), i.text)
                inout_order = inout_order + 1

                polygon = QPolygon(i.points)
                qp.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 255, 127)))     # inout port color
                qp.drawPolygon(polygon)

    # When mouse is pressed, the top left corner of the rectangle being drawn is saved
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if len(self.rect_list) != 0:
                for i in self.rect_list:
                    # Drag condition when the click 10 units inside all the corners
                    if i.rect_begin.x() + 10 <= event.pos().x() <= i.rect_end.x() -10 and i.rect_begin.y() + 10 <= event.pos().y() <= i.rect_end.y() - 10:
                        i.relative_start = event.pos()
                        i.temp_rect_begin = i.rect_begin
                        i.temp_rect_end = i.rect_end
                        i.drag = 1
                        break
                    # Top left resize when the click inside top left corner and its 10 unit small rectangle
                    elif (i.rect_begin.x() < event.pos().x() < i.rect_begin.x() + 10 and
                          i.rect_begin.y() < event.pos().y() < i.rect_begin.y() + 10):
                        i.rect_begin = event.pos()
                        i.resize = 1
                        break
                    # Bottom left resize when the click inside bottom left corner and its 10 unit small rectangle
                    elif (i.rect_begin.x() < event.pos().x() < i.rect_begin.x() + 10 and
                          i.rect_end.y() - 10 < event.pos().y() < i.rect_end.y()):
                        i.rect_begin.setX(event.pos().x())
                        i.rect_end.setY(event.pos().y())
                        i.resize = 2
                        break
                    # Top right resize when the click inside top right corner and its 10 unit small rectangle
                    elif (i.rect_end.x() - 10 < event.pos().x() < i.rect_end.x() and
                          i.rect_begin.y() < event.pos().y() < i.rect_begin.y() + 10):
                        i.rect_begin.setY(event.pos().y())
                        i.rect_end.setX(event.pos().x())
                        i.resize = 3
                        break
                    # Bottom right resize when the click inside bottom right corner and its 10 unit small rectangle
                    elif (i.rect_end.x() - 10 < event.pos().x() < i.rect_end.x() and
                          i.rect_end.y() - 10 < event.pos().y() < i.rect_end.y()):
                        i.rect_end = event.pos()
                        i.resize = 4
                        break
                    else:
                        pass
        # elif event.button() == Qt.RightButton:

    # When mouse is pressed and moving, the bottom right corner of the rectangle also changes and shown in screen
    def mouseMoveEvent(self, event):
        self.intersect = 0
        for i in self.rect_list:
            # Drag condition
            if i.drag == 1:
                rect_begin_dragged = i.temp_rect_begin + event.pos() - i.relative_start
                rect_end_dragged = i.temp_rect_end + event.pos() - i.relative_start
                for j in self.rect_list:
                    if j != i:
                        rect_begin_x = j.rect_begin.x() - 2 * j.Tri_In_H
                        rect_begin_y = j.rect_begin.y() - 10
                        rect_width = j.width + 3 * j.Tri_In_H
                        rect_height = j.height + 20
                        rect_temp = QRect(rect_begin_x, rect_begin_y, rect_width, rect_height)
                        rect_dragged = QRect(rect_begin_dragged.x() - 2 * i.Tri_In_H, rect_begin_dragged.y() - 10, i.width + 3 * i.Tri_In_H, i.height + 20)
                        if rect_temp.intersects(rect_dragged):
                            self.intersect = 1
                            break

                if self.intersect == 0:
                    i.rect_begin = rect_begin_dragged
                    i.rect_end = rect_end_dragged
                    i.drag_release = 1
                    i.update()
                    self.update()  # To call paintEvent
                break

            # Top left resize
            elif i.resize == 1:
                rect_begin_dragged = event.pos()
                rect_end_dragged = copy.deepcopy(i.rect_end)
                for j in self.rect_list:
                    if j != i:
                        rect_begin_x = j.rect_begin.x() - 2 * j.Tri_In_H
                        rect_begin_y = j.rect_begin.y() - 10
                        rect_width = j.width + 3 * j.Tri_In_H
                        rect_height = j.height + 20
                        rect_temp = QRect(rect_begin_x, rect_begin_y, rect_width, rect_height)
                        rect_dragged = QRect(rect_begin_dragged.x() - 2 * i.Tri_In_H, rect_begin_dragged.y() - 10, i.width + 3 * i.Tri_In_H, i.height + 20)
                        if rect_temp.intersects(rect_dragged):
                            self.intersect = 1
                            break

                if self.intersect == 0:
                    i.rect_begin = rect_begin_dragged
                    i.rect_end = rect_end_dragged
                    i.resize_release = 1
                    i.update()
                    self.update()  # To call paintEvent
                break

            # Bottom left resize
            elif i.resize == 2:
                rect_begin_dragged = copy.deepcopy(i.rect_begin)
                rect_begin_dragged.setX(event.pos().x())
                rect_end_dragged = copy.deepcopy(i.rect_end)
                rect_end_dragged.setY(event.pos().y())
                for j in self.rect_list:
                    if j != i:
                        rect_begin_x = j.rect_begin.x() - 2 * j.Tri_In_H
                        rect_begin_y = j.rect_begin.y() - 10
                        rect_width = j.width + 3 * j.Tri_In_H
                        rect_height = j.height + 20
                        rect_temp = QRect(rect_begin_x, rect_begin_y, rect_width, rect_height)
                        rect_dragged = QRect(rect_begin_dragged.x() - 2 * i.Tri_In_H, rect_begin_dragged.y() - 10, i.width + 3 * i.Tri_In_H, i.height + 20)
                        if rect_temp.intersects(rect_dragged):
                            self.intersect = 1
                            break

                if self.intersect == 0:
                    i.rect_begin = rect_begin_dragged
                    i.rect_end = rect_end_dragged
                    i.resize_release = 2
                    i.update()
                    self.update()  # To call paintEvent
                break

            # Top right resize
            elif i.resize == 3:
                rect_begin_dragged = copy.deepcopy(i.rect_begin)
                rect_begin_dragged.setX(event.pos().y())
                rect_end_dragged = copy.deepcopy(i.rect_end)
                rect_end_dragged.setY(event.pos().x())
                for j in self.rect_list:
                    if j != i:
                        rect_begin_x = j.rect_begin.x() - 2 * j.Tri_In_H
                        rect_begin_y = j.rect_begin.y() - 10
                        rect_width = j.width + 3 * j.Tri_In_H
                        rect_height = j.height + 20
                        rect_temp = QRect(rect_begin_x, rect_begin_y, rect_width, rect_height)
                        rect_dragged = QRect(rect_begin_dragged.x() - 2 * i.Tri_In_H, rect_begin_dragged.y() - 10, i.width + 3 * i.Tri_In_H, i.height + 20)
                        if rect_temp.intersects(rect_dragged):
                            self.intersect = 1
                            break

                if self.intersect == 0:
                    i.rect_begin = rect_begin_dragged
                    i.rect_end = rect_end_dragged
                    i.resize_release = 3
                    i.update()
                    self.update()  # To call paintEvent
                break

            # Bottom right resize
            elif i.resize == 4:
                rect_begin_dragged = copy.deepcopy(i.rect_begin)
                rect_end_dragged = event.pos()
                for j in self.rect_list:
                    if j != i:
                        rect_begin_x = j.rect_begin.x() - 2 * j.Tri_In_H
                        rect_begin_y = j.rect_begin.y() - 10
                        rect_width = j.width + 3 * j.Tri_In_H
                        rect_height = j.height + 20
                        rect_temp = QRect(rect_begin_x, rect_begin_y, rect_width, rect_height)
                        rect_dragged = QRect(rect_begin_dragged.x() - 2 * i.Tri_In_H, rect_begin_dragged.y() - 10, i.width + 3 * i.Tri_In_H, i.height + 20)
                        if rect_temp.intersects(rect_dragged):
                            self.intersect = 1
                            break

                if self.intersect == 0:
                    i.rect_begin = rect_begin_dragged
                    i.rect_end = rect_end_dragged
                    i.resize_release = 4
                    i.update()
                    self.update()  # To call paintEvent
                break
            else:
                pass

    # After mouse has released, the bottom right corner of the rectangle is assigned and rectangle placed in screen
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if len(self.rect_list) != 0:
                for i in self.rect_list:
                    if i.drag_release == 1:
                        if self.intersect == 0:
                            i.rect_begin = i.temp_rect_begin + event.pos() - i.relative_start
                            i.rect_end = i.temp_rect_end + event.pos() - i.relative_start
                            i.update()
                            self.update()   # To call paintEvent
                        i.drag_release = 0
                        i.drag = 0
                        self.intersect = 0
                        break
                    # Top left resize
                    elif i.resize_release == 1:
                        if self.intersect == 0:
                            i.rect_begin = event.pos()
                            i.update()
                            self.update()   # To call paintEvent
                        i.resize_release = 0
                        i.resize = 0
                        self.intersect = 0
                        break
                    # Bottom left resize
                    elif i.resize_release == 2:
                        if self.intersect == 0:
                            i.rect_begin.setX(event.pos().x())
                            i.rect_end.setY(event.pos().y())
                            i.update()
                            self.update()   # To call paintEvent
                        i.resize_release = 0
                        i.resize = 0
                        self.intersect = 0
                        break
                    # Top right resize
                    elif i.resize_release == 3:
                        if self.intersect == 0:
                            i.rect_begin.setY(event.pos().y())
                            i.rect_end.setX(event.pos().x())
                            i.update()
                            self.update()   # To call paintEvent
                        i.resize_release = 0
                        i.resize = 0
                        self.intersect = 0
                        break
                    # Bottom right resize
                    elif i.resize_release == 4:
                        if self.intersect == 0:
                            i.rect_end = event.pos()
                            i.update()
                            self.update()   # To call paintEvent
                        i.resize_release = 0
                        i.resize = 0
                        self.intersect = 0
                        break
                    else:
                        pass

    def contextMenuEvent(self, event):
        module_area = 0
        for i in self.rect_list:
            if i.rect_begin.x() < event.pos().x() < i.rect_end.x() and i.rect_begin.y() < event.pos().y() < i.rect_end.y():
                module_area = 1
                contextMenu = QMenu(self)

                # Add Input Port action is used to add input port to both code and block
                portAction = contextMenu.addAction("Add Port")
                renameAction = contextMenu.addAction("Rename Module")
                removeModuleAction = contextMenu.addAction("Remove Module")

                action = contextMenu.exec_(self.mapToGlobal(event.pos()))

                if action == portAction:
                    self.myshow = AddPort(i)
                    self.myshow.setWindowTitle("Add Port")
                    self.myshow.show()
                    self.update()
                elif action == renameAction:
                    self.myshow = RenameModule(i, self.forbidden_module_names)
                    self.myshow.setWindowTitle("Rename Module")
                    self.myshow.show()
                    self.update()
                elif action == removeModuleAction:
                    self.forbidden_module_names.remove(i.center_text)
                    self.rect_list.remove(i)
                    self.update()

        port_area = "no_port"
        if module_area == 0:
            for r in self.rect_list:
                temp_port = 0
                for i in r.in_port_list:
                    polygon = QPolygon(i.points)
                    if polygon.containsPoint(event.pos(), Qt.OddEvenFill):
                        port_area = "input"
                        temp_port = i
                for i in r.inout_port_list:
                    polygon = QPolygon(i.points)
                    if polygon.containsPoint(event.pos(), Qt.OddEvenFill):
                        port_area = "inout"
                        temp_port = i
                for i in r.out_port_list:
                    polygon = QPolygon(i.points)
                    if polygon.containsPoint(event.pos(), Qt.OddEvenFill):
                        port_area = "output"
                        temp_port = i

                if port_area != "no_port":
                    contextMenu = QMenu(self)
                    removeAction = contextMenu.addAction("Remove")
                    renameAction = contextMenu.addAction("Rename Port")

                    action = contextMenu.exec_(self.mapToGlobal(event.pos()))

                    if action == removeAction:
                        if port_area == "input":
                            r.in_port_list.remove(temp_port)
                            r.update()
                            self.update()
                        elif port_area == "inout":
                            r.inout_port_list.remove(temp_port)
                            r.update()
                            self.update()
                        elif port_area == "output":
                            r.out_port_list.remove(temp_port)
                            r.update()
                            self.update()
                        r.update()
                    elif action == renameAction:
                        self.myshow = RenamePort(temp_port, r)
                        self.myshow.setWindowTitle("Rename Port")
                        self.myshow.show()
                    break



        if port_area == "no_port" and module_area == 0:
            contextMenu = QMenu(self)

            # Add Input Port action is used to add input port to both code and block
            addModuleAction = contextMenu.addAction("Add Module")

            action = contextMenu.exec_(self.mapToGlobal(event.pos()))
            if action == addModuleAction:
                intersect = 0
                rect_begin_dragged = event.pos()
                for j in self.rect_list:
                    rect_begin_x = j.rect_begin.x() - 2 * j.Tri_In_H
                    rect_begin_y = j.rect_begin.y() - 10
                    rect_width = j.width + 3 * j.Tri_In_H
                    rect_height = j.height + 20
                    rect_temp = QRect(rect_begin_x, rect_begin_y, rect_width, rect_height)
                    rect_dragged = QRect(rect_begin_dragged.x() - 2 * j.Tri_In_H, rect_begin_dragged.y() - 10, 200 + 3 * j.Tri_In_H, 200 + 20)
                    if rect_temp.intersects(rect_dragged):
                        intersect = 1
                        break

                if intersect == 0:
                    tempModule = Module()
                    i = 0
                    while 1:
                        if 'case_block_' + str(i) not in self.forbidden_module_names:
                            tempModule.center_text = 'case_block_' + str(i)
                            tempModule.rect_begin = event.pos()
                            tempModule.rect_end = event.pos() + QtCore.QPoint(200, 200)
                            tempModule.update()
                            self.rect_list.append(tempModule)
                            self.forbidden_module_names.append(tempModule.center_text)
                            # To call paintEvent method, update method is run.
                            # When module is created, to show it on canvas paintEvent must be called
                            self.update()
                            break
                        i = i + 1
                else:
                    self.myshow = ErrorMessage('Module cannot be created because it is too close to other modules')

    def add_input(self, module, text):
        tempClass = Port()
        tempClass.port_type = 'input'
        tempClass.text = text
        module.in_port_list.append(tempClass)
        module.update()
        self.update()

    def add_output(self, module, text):
        tempClass = Port()
        tempClass.port_type = 'output'
        tempClass.text = text
        module.out_port_list.append(tempClass)
        module.update()
        self.update()

    def add_inout(self, module, text):
        tempClass = Port()
        tempClass.port_type = 'inout'
        tempClass.text = text
        module.inout_port_list.append(tempClass)
        module.update()
        self.update()

    def update_code(self):
        self.code_string = ""
        for i in self.rect_list:
            for j in i.module_string_list:
                self.code_string = self.code_string + j


class Port:
    def __init__(self):
        self.points = [QtCore.QPoint()]
        self.polygon = QPolygon(self.points)
        self.text = ''
        self.port_type = 'empty'


class Module:
    def __init__(self):
        self.rect_begin = QtCore.QPoint()   # Module rectangle top left corner
        self.rect_end = QtCore.QPoint()     # Module rectangle bottom right corner
        self.temp_rect_begin = QtCore.QPoint()
        self.temp_rect_end = QtCore.QPoint()
        self.relative_start = QtCore.QPoint()
        self.drag = 0
        self.resize = 0
        self.drag_release = 0
        self.resize_release = 0
        self.Tri_coef = 0.5
        self.Tri_In_H = 30
        self.Tri_In_F = self.Tri_coef * self.Tri_In_H
        self.center_text = ''               # Module name in the center of rectangle
        self.in_port_list = []
        self.out_port_list = []
        self.inout_port_list = []
        self.module_string_list = []
        self.forbidden_words = ["input", "output", "inout", "module", "endmodule",""]
        self.width = 0
        self.height = 0

    def update(self):
        self.width = self.rect_end.x() - self.rect_begin.x()
        self.height = self.rect_end.y() - self.rect_begin.y()
        temp_left = self.Tri_In_F
        temp_right = self.Tri_In_F
        if not (self.rect_end.y() - self.rect_begin.y() - 10 < self.Tri_In_F * (len(self.in_port_list) + len(self.inout_port_list)) + 5 < self.rect_end.y() - self.rect_begin.y() + 10):
            temp_left = int((self.rect_end.y() - self.rect_begin.y()) / ((len(self.in_port_list) + len(self.inout_port_list)) + 10))

        if not (self.rect_end.y() - self.rect_begin.y() - 10 < self.Tri_In_F * len(self.out_port_list) + 5 < self.rect_end.y() - self.rect_begin.y() + 10):
            temp_right = int((self.rect_end.y() - self.rect_begin.y()) / (len(self.out_port_list) + 10))

        self.Tri_In_F = min(temp_left, temp_right)
        self.Tri_In_H = int(self.Tri_In_F / self.Tri_coef)

        self.module_string_list = []
        self.module_string_list.append("module ")
        self.module_string_list.append(self.center_text)
        self.module_string_list.append("(" + "\n")

        in_order = 0
        for j in self.in_port_list:
            self.module_string_list.append("input ")
            self.module_string_list.append(j.text + ",\n")
            self.forbidden_words.append(j.text)

            j.points = [self.rect_begin + QtCore.QPoint(int(-self.Tri_In_H), int(self.Tri_In_F * in_order)),
                        self.rect_begin + QtCore.QPoint(0, int(self.Tri_In_F / 2 + self.Tri_In_F * in_order)),
                        self.rect_begin + QtCore.QPoint(int(-self.Tri_In_H),
                                                     int(self.Tri_In_F + self.Tri_In_F * in_order))]
            # Write the port name
            in_order = in_order + 1

        out_order = 0
        for j in self.out_port_list:
            self.module_string_list.append("output ")
            self.module_string_list.append(j.text + ",\n")
            self.forbidden_words.append(j.text)

            j.points = [self.rect_end + QtCore.QPoint(int(self.Tri_In_H + 1),
                                                   int(self.Tri_In_F / 2 - (
                                                               self.rect_end.y() - self.rect_begin.y()) + self.Tri_In_F * out_order)),
                        self.rect_end + QtCore.QPoint(1,
                                                   int(-(self.rect_end.y() - self.rect_begin.y()) + self.Tri_In_F * out_order)),
                        self.rect_end + QtCore.QPoint(1, int(
                            self.Tri_In_F - (self.rect_end.y() - self.rect_begin.y()) + self.Tri_In_F * out_order))]

            out_order = out_order + 1

        inout_order = 0
        for j in self.inout_port_list:
            self.module_string_list.append("inout ")
            self.module_string_list.append(j.text + ",\n")
            self.forbidden_words.append(j.text)

            j.points = [QtCore.QPoint(int(self.rect_begin.x() - self.Tri_In_H),
                                      int(self.rect_end.y() - self.Tri_In_F - self.Tri_In_F * inout_order)),
                        QtCore.QPoint(int(self.rect_begin.x()),
                                      int(self.rect_end.y() - self.Tri_In_F / 2 - self.Tri_In_F * inout_order)),
                        QtCore.QPoint(int(self.rect_begin.x() - self.Tri_In_H),
                                      int(self.rect_end.y() - self.Tri_In_F * inout_order)),
                        QtCore.QPoint(int(self.rect_begin.x() - 2 * self.Tri_In_H),
                                      int(self.rect_end.y() - self.Tri_In_F / 2 - self.Tri_In_F * inout_order))]
            inout_order = inout_order + 1

        self.module_string_list.append(");" + "\n")
        self.module_string_list.append("endmodule" + "\n\n")

class RenameModule(QtWidgets.QWidget):
    def __init__(self, module, forbidden_module_names):
        super(RenameModule, self).__init__()

        self.module = module
        self.forbidden_module_names = forbidden_module_names

        self.nametextbox = QtWidgets.QLineEdit(self)
        self.setButton = QPushButton('Okay', self)
        self.setButton.clicked.connect(self.okay_button)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self.nametextbox,   0, 0)
        mainLayout.addWidget(self.setButton,     0, 1)

        mainLayout.setRowMinimumHeight(2, 40)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnMinimumWidth(1, 200)
        mainLayout.setSpacing(5)

        self.setLayout(mainLayout)

    def okay_button(self):
        self.forbidden_module_names.remove(self.module.center_text)
        if not (re.search('\W', self.nametextbox.text()) or self.nametextbox.text() in self.forbidden_module_names):  # Search for non-word character
            self.module.center_text = self.nametextbox.text()
            self.forbidden_module_names.append(self.module.center_text)
            self.close()
        else:
            self.forbidden_module_names.append(self.module.center_text)
            self.myshow = ErrorMessage('Please enter a valid name')
        self.module.update()


class RenamePort(QtWidgets.QWidget):
    def __init__(self, port, module):
        super(RenamePort, self).__init__()

        self.port = port
        self.module = module

        label1 = QLabel("Port Name")
        label2 = QLabel("Signal Length")

        self.nametextbox = QtWidgets.QLineEdit(self)
        self.veclentextbox = QtWidgets.QLineEdit(self)
        self.setButton = QPushButton('Okay', self)
        self.setButton.clicked.connect(self.okay_button)

        mainLayout = QGridLayout()
        mainLayout.addWidget(label1,             0, 1)
        mainLayout.addWidget(label2,             0, 2)

        mainLayout.addWidget(self.nametextbox,   1, 1)
        mainLayout.addWidget(self.veclentextbox, 1, 2)
        mainLayout.addWidget(self.setButton,     2, 2)

        mainLayout.setRowMinimumHeight(2, 40)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnMinimumWidth(1, 200)
        mainLayout.setSpacing(5)

        self.setLayout(mainLayout)

    def okay_button(self):
        try:
            if int(self.veclentextbox.text()) - 1 >= 0:
                if int(self.veclentextbox.text()) - 1 == 0:
                    if not (re.search('\W', self.nametextbox.text()) or self.nametextbox.text() in self.module.forbidden_words):  # Search for non-word character
                        self.port.text = self.nametextbox.text()
                        self.close()
                    else:
                        self.myshow = ErrorMessage('Please enter a valid name')
                elif int(self.veclentextbox.text()) - 1 > 0:
                    if not (re.search('\W', self.nametextbox.text()) or self.nametextbox.text() in self.module.forbidden_words):  # Search for non-word character
                        self.port.text = self.nametextbox.text() + "[" + str(int(self.veclentextbox.text()) - 1) + ":0]"
                        self.close()
                    else:
                        self.myshow = ErrorMessage('Please enter a valid name')
            else:
                self.myshow = ErrorMessage('Please enter a valid signal length')
        except:
            self.myshow = ErrorMessage('Please enter a valid signal length')
        self.module.update()


class AddPort(QtWidgets.QWidget):
    def __init__(self, module):
        super(AddPort, self).__init__()

        self.port = Port()
        self.module = module

        label1 = QLabel("Signal Type")
        label2 = QLabel("Port Name")
        label3 = QLabel("Signal Length")

        self.port_type = "input"
        self.combo_box = QtWidgets.QComboBox(self)              # creating a combo box widget
        self.combo_box.setGeometry(200, 150, 150, 30)           # setting geometry of combo box
        self.combo_box.addItems(["Input", "Output", "Inout"])   # adding list of items to combo box
        self.combo_box.activated.connect(self.determine_type)   # adding action to combo box

        self.nametextbox = QtWidgets.QLineEdit(self)
        self.veclentextbox = QtWidgets.QLineEdit(self)

        self.setButton = QPushButton('Add', self)
        self.setButton.clicked.connect(self.add_port)

        mainLayout = QGridLayout()
        mainLayout.addWidget(label1,             0, 0)
        mainLayout.addWidget(label2,             0, 1)
        mainLayout.addWidget(label3,             0, 2)

        mainLayout.addWidget(self.combo_box,     1, 0)
        mainLayout.addWidget(self.nametextbox,   1, 1)
        mainLayout.addWidget(self.veclentextbox, 1, 2)

        mainLayout.addWidget(self.setButton,     2, 2)

        mainLayout.setRowMinimumHeight(2, 40)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setColumnMinimumWidth(1, 200)
        mainLayout.setSpacing(5)

        self.setLayout(mainLayout)

    def add_port(self):
        self.port.port_type = self.port_type
        try:
            if int(self.veclentextbox.text()) - 1 >= 0:
                error = 0
                if int(self.veclentextbox.text()) - 1 == 0:
                    if not (re.search('\W', self.nametextbox.text()) or self.nametextbox.text() in self.module.forbidden_words):  # Search for non-word character
                        self.port.text = self.nametextbox.text()
                    else:
                        error = 1
                        self.myshow = ErrorMessage('Please enter a valid name')
                elif int(self.veclentextbox.text()) - 1 > 0:
                    if not (re.search('\W', self.nametextbox.text()) or self.nametextbox.text() in self.module.forbidden_words):  # Search for non-word character
                        self.port.text = self.nametextbox.text() + "[" + str(int(self.veclentextbox.text()) - 1) + ":0]"
                    else:
                        error = 1
                        self.myshow = ErrorMessage('Please enter a valid name')

                if error == 0:
                    if self.port_type == "output":
                        self.module.out_port_list.append(self.port)
                    elif self.port_type == "input":
                        self.module.in_port_list.append(self.port)
                    else:
                        self.module.inout_port_list.append(self.port)
                    self.module.update()
                    self.close()
            else:
                self.myshow = ErrorMessage('Please enter a valid signal length')
        except:
            self.myshow = ErrorMessage('Please enter a signal length')

    def determine_type(self):
        if str(self.combo_box.currentText()) == "Input":
            self.port_type = 'input'
        elif str(self.combo_box.currentText()) == "Output":
            self.port_type = 'output'
        elif str(self.combo_box.currentText()) == "Inout":
            self.port_type = 'inout'


class ErrorMessage(QtWidgets.QWidget):
    def __init__(self, error_message):
        super(ErrorMessage, self).__init__()

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(error_message)
        msg.setWindowTitle("Error")
        msg.exec_()
