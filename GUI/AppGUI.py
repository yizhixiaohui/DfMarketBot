# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(449, 550)  # Increased window height
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # --- Buying Group ---
        self.buySettingsGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.buySettingsGroup.setGeometry(QtCore.QRect(10, 10, 431, 201))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.buySettingsGroup.setFont(font)
        self.buySettingsGroup.setObjectName("buySettingsGroup")

        self.label_ideal_price = QtWidgets.QLabel(self.buySettingsGroup)
        self.label_ideal_price.setGeometry(QtCore.QRect(10, 30, 71, 31))
        font.setPointSize(11)
        font.setBold(True)
        self.label_ideal_price.setFont(font)
        self.label_ideal_price.setObjectName("label_ideal_price")

        self.textEdit_ideal_price = QtWidgets.QTextEdit(self.buySettingsGroup)
        self.textEdit_ideal_price.setGeometry(QtCore.QRect(80, 30, 121, 31))
        self.textEdit_ideal_price.setFont(font)
        self.textEdit_ideal_price.setObjectName("textEdit_ideal_price")

        self.label_unacceptable_price = QtWidgets.QLabel(self.buySettingsGroup)
        self.label_unacceptable_price.setGeometry(QtCore.QRect(10, 80, 71, 31))
        self.label_unacceptable_price.setFont(font)
        self.label_unacceptable_price.setObjectName("label_unacceptable_price")

        self.textEdit_unacceptable_price = QtWidgets.QTextEdit(self.buySettingsGroup)
        self.textEdit_unacceptable_price.setGeometry(QtCore.QRect(80, 80, 121, 31))
        self.textEdit_unacceptable_price.setFont(font)
        self.textEdit_unacceptable_price.setObjectName("textEdit_unacceptable_price")

        self.label_loop_gap = QtWidgets.QLabel(self.buySettingsGroup)
        self.label_loop_gap.setGeometry(QtCore.QRect(10, 130, 71, 31))
        self.label_loop_gap.setFont(font)
        self.label_loop_gap.setObjectName("label_loop_gap")

        self.textEdit_loop_gap = QtWidgets.QTextEdit(self.buySettingsGroup)
        self.textEdit_loop_gap.setGeometry(QtCore.QRect(80, 130, 121, 31))
        self.textEdit_loop_gap.setFont(font)
        self.textEdit_loop_gap.setObjectName("textEdit_loop_gap")

        self.is_convertiable = QtWidgets.QCheckBox(self.buySettingsGroup)
        self.is_convertiable.setGeometry(QtCore.QRect(230, 30, 121, 31))
        self.is_convertiable.setFont(font)
        self.is_convertiable.setObjectName("is_convertiable")

        self.is_key_mode = QtWidgets.QCheckBox(self.buySettingsGroup)
        self.is_key_mode.setGeometry(QtCore.QRect(230, 80, 121, 31))
        self.is_key_mode.setFont(font)
        self.is_key_mode.setObjectName("is_key_mode")

        self.is_half_coin_mode = QtWidgets.QCheckBox(self.buySettingsGroup)
        self.is_half_coin_mode.setGeometry(QtCore.QRect(230, 130, 191, 31))
        self.is_half_coin_mode.setFont(font)
        self.is_half_coin_mode.setObjectName("is_half_coin_mode")
        
        self.label_use = QtWidgets.QLabel(self.buySettingsGroup)
        self.label_use.setGeometry(QtCore.QRect(10, 160, 221, 31))
        self.label_use.setFont(font)
        self.label_use.setObjectName("label_use")

        # --- Selling Group ---
        self.sellSettingsGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.sellSettingsGroup.setGeometry(QtCore.QRect(10, 220, 431, 151))
        font.setPointSize(10)
        self.sellSettingsGroup.setFont(font)
        self.sellSettingsGroup.setObjectName("sellSettingsGroup")

        self.label_sell_time = QtWidgets.QLabel(self.sellSettingsGroup)
        self.label_sell_time.setGeometry(QtCore.QRect(10, 30, 131, 31))
        font.setPointSize(11)
        self.label_sell_time.setFont(font)
        self.label_sell_time.setObjectName("label_sell_time")

        self.textEdit_sell_time = QtWidgets.QTextEdit(self.sellSettingsGroup)
        self.textEdit_sell_time.setGeometry(QtCore.QRect(140, 30, 101, 31))
        self.textEdit_sell_time.setFont(font)
        self.textEdit_sell_time.setObjectName("textEdit_sell_time")

        self.label_sell_price = QtWidgets.QLabel(self.sellSettingsGroup)
        self.label_sell_price.setGeometry(QtCore.QRect(10, 80, 81, 31))
        self.label_sell_price.setFont(font)
        self.label_sell_price.setObjectName("label_sell_price")

        self.textEdit_sell_price = QtWidgets.QTextEdit(self.sellSettingsGroup)
        self.textEdit_sell_price.setGeometry(QtCore.QRect(140, 80, 101, 31))
        self.textEdit_sell_price.setFont(font)
        self.textEdit_sell_price.setObjectName("textEdit_sell_price")

        self.button_start_selling = QtWidgets.QPushButton(self.sellSettingsGroup)
        self.button_start_selling.setGeometry(QtCore.QRect(260, 30, 151, 31))
        self.button_start_selling.setFont(font)
        self.button_start_selling.setObjectName("button_start_selling")

        self.button_stop_selling = QtWidgets.QPushButton(self.sellSettingsGroup)
        self.button_stop_selling.setGeometry(QtCore.QRect(260, 70, 151, 31))
        self.button_stop_selling.setFont(font)
        self.button_stop_selling.setObjectName("button_stop_selling")

        self.button_test_sell = QtWidgets.QPushButton(self.sellSettingsGroup)
        self.button_test_sell.setGeometry(QtCore.QRect(260, 110, 151, 31))
        self.button_test_sell.setFont(font)
        self.button_test_sell.setObjectName("button_test_sell")

        # --- Log Browser ---
        self.log_browser = QtWidgets.QTextBrowser(self.centralwidget)
        self.log_browser.setGeometry(QtCore.QRect(10, 380, 431, 141))
        self.log_browser.setObjectName("log_browser")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Add thousand separators listener
        self.textEdit_ideal_price.textChanged.connect(lambda: self.format_price_input(self.textEdit_ideal_price))
        self.textEdit_unacceptable_price.textChanged.connect(lambda: self.format_price_input(self.textEdit_unacceptable_price))
        self.textEdit_sell_price.textChanged.connect(lambda: self.format_price_input(self.textEdit_sell_price))


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DFMarketBot"))
        
        # Buying Group
        self.buySettingsGroup.setTitle(_translate("MainWindow", "自动购买设置"))
        self.label_ideal_price.setText(_translate("MainWindow", "理想价格"))
        self.label_unacceptable_price.setText(_translate("MainWindow", "最高价格"))
        self.label_loop_gap.setText(_translate("MainWindow", "循环间隔"))
        self.is_convertiable.setText(_translate("MainWindow", "物品可兑换"))
        self.is_key_mode.setText(_translate("MainWindow", "钥匙卡模式"))
        self.is_half_coin_mode.setText(_translate("MainWindow", "使用哈夫币余额计算价格"))
        self.label_use.setText(_translate("MainWindow", "按 F8 开始循环   按 F9 停止循环"))

        # Selling Group
        self.sellSettingsGroup.setTitle(_translate("MainWindow", "自动售卖设置"))
        self.label_sell_time.setText(_translate("MainWindow", "售卖间隔(分钟)"))
        self.label_sell_price.setText(_translate("MainWindow", "期望售价"))
        self.button_start_selling.setText(_translate("MainWindow", "开始自动售卖"))
        self.button_stop_selling.setText(_translate("MainWindow", "停止自动售卖"))
        self.button_test_sell.setText(_translate("MainWindow", "测试单次售卖"))


    def format_price_input(self, textEdit: QtWidgets.QTextEdit):
        cursor = textEdit.textCursor()
        pos = cursor.position()
        old_text = textEdit.toPlainText()
        raw_text = old_text.replace(',', '')
        if not raw_text.isdigit() and raw_text != "":
            clean_text = ''.join(filter(str.isdigit, raw_text))
            if clean_text:
                 formatted = "{:,}".format(int(clean_text))
            else:
                 formatted = ""
        else:
            if raw_text:
                formatted = "{:,}".format(int(raw_text))
            else:
                formatted = ""

        if formatted == old_text:
            return

        textEdit.blockSignals(True)
        textEdit.setPlainText(formatted)
        textEdit.blockSignals(False)

        if old_text and raw_text:
            old_commas_before_cursor = old_text[:pos].count(',')
            new_commas_before_cursor = formatted[:pos].count(',') if pos > 0 else 0
            delta = new_commas_before_cursor - old_commas_before_cursor
            new_pos = pos + delta
        elif formatted:
             new_pos = len(formatted)
        else:
             new_pos = 0

        new_pos = max(0, min(len(formatted), new_pos))
        cursor.setPosition(new_pos)
        textEdit.setTextCursor(cursor)

    def get_plain_number(self, textEdit: QtWidgets.QTextEdit) -> int:
        text = textEdit.toPlainText().replace(",", "")
        return int(text) if text.isdigit() else 0
