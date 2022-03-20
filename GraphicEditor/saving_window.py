from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SaveForm(object):
    def setupUi(self, SaveForm):
        SaveForm.setObjectName("SaveForm")
        SaveForm.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(SaveForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(SaveForm)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(SaveForm)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(SaveForm)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(SaveForm)
        QtCore.QMetaObject.connectSlotsByName(SaveForm)

    def retranslateUi(self, SaveForm):
        _translate = QtCore.QCoreApplication.translate
        SaveForm.setWindowTitle(_translate("SaveForm", "Сохранение"))
        self.label.setText(_translate("SaveForm", "Название файла:"))
        self.pushButton.setText(_translate("SaveForm", "Сохранить"))
