from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QPushButton, QLineEdit, QDateEdit, QComboBox, QMessageBox, QCheckBox
from PySide6.QtCore import Qt, QDate

import main as mn
import sys

# For heatmap
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Inputs:
# Enter the stock name(ticker symbol)
# Strike price
# The durration of the stock option(Date)

#Constants
HEAT_MAP_SIZE_X = 11
HEAT_MAP_SIZE_Y = 10

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Trading Application")

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QGridLayout(container)

        self.line_stockName = QLineEdit()
        self.line_stockName.setPlaceholderText("APPL")

        # combo box(drop down menu)
        self.stock_combo_box = QComboBox()
        self.stock_combo_box.addItems(["APPL", "NVDA", "MSFT", "AMZN", "TSLA"])
        self.stock_combo_box.setEditable(False)
        self.stock_combo_box.currentIndexChanged.connect(self.onComboBoxChanged)

        # Price input
        self.line_strike_price = QLineEdit()
        self.line_strike_price.setPlaceholderText("$100.25")

        # Check box
        self.check_box = QCheckBox("Put Option", self)
        self.check_box.setChecked(False)

        # label
        label_header = QLabel("Stock Options(B.S.F): ")
        label_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label1 = QLabel("Stock Name:")
        label_price = QLabel("Strike Price:")
        label_durration = QLabel("The Durration:")
        self.label_result = QLabel("Black Scholes Result:")
        
        date_info = QDate().currentDate()
        self.date = QDateEdit(date_info)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.sumbitBtn)

        # Assemble grid for widgets
        main_layout.addWidget(label_header, 0, 0)
        #labels
        main_layout.addWidget(label1, 1, 0)
        main_layout.addWidget(label_price, 2, 0)
        main_layout.addWidget(label_durration, 3, 0)
        main_layout.addWidget(self.check_box, 4, 0)

        #inputs
        main_layout.addWidget(self.line_stockName, 1, 1)
        main_layout.addWidget(self.line_strike_price, 2, 1)
        main_layout.addWidget(self.date, 3, 1)

        main_layout.addWidget(self.stock_combo_box, 1, 2)
        main_layout.addWidget(submit_btn, 5, 0)
        main_layout.addWidget(self.label_result, 6, 0)


    def sumbitBtn(self):
        # validiation of forum inputs
        inputStr = self.line_stockName.text()
        isValidTicker = mn.validTicker(inputStr)
        enteredDate = self.date
        call_option = self.check_box.isChecked() # if checked it is a put option
        call_option = not call_option            # flip boolean value for the correct value
       
        try:
            strikePrice = float(self.line_strike_price.text())
        except ValueError:
            QMessageBox.information(self, "ERROR", "Strike price Must be a Number")
            return None
        
        # Ticker is not valid stock name
        if not isValidTicker:
            QMessageBox.information(self, "ERROR", "Stock Name Must Be a Valid Ticker Symbol on the NASDAQ-listed companies")
            return None

        # Strike Price is not valid
        if strikePrice <= 0:
            QMessageBox.information(self, "ERROR", "Strike price Must be a Postive Value")
            return None

        # Date is in the future
        if enteredDate.date() < QDate().currentDate():
            QMessageBox.information(self, "ERROR", "Date Is In The Past")
            return None

        # Convert the amount of days between end date and the current date on the option
        endDate = enteredDate.date()
        currentDate = QDate().currentDate()
        duration = currentDate.daysTo(endDate)
   
        # Setup for the Heatmap 
        current_price = mn.getCurrentPrice(inputStr)
        mn.time.sleep(1)
        intrestRateTicker = mn.yf.Ticker("^IRX") # Downloads the ticker data once

        # Range of 20% of the stock price
        lower_bound_price = current_price * 0.80
        upper_bound_price = current_price * 1.2

        # Right now should be 15%-60%(y-axis range)
        volatility = mn.np.round(mn.np.linspace(0.6, 0.15, 10), 2)    # 10 volatility levels

        # Has to get calcualted at runtime
        # Range of the stock prices +10 each interval
        # Creates 11 element NDArray with the middle value being current_price
        stock_price = mn.np.round(mn.np.linspace(lower_bound_price, upper_bound_price, 11),2)

        stock_price_list = stock_price.tolist()
        volatility_list = volatility.tolist()

        # This creates a 10x10 - rowsxcol
        # random 2d array(need to make the actual data)
        # y - rows, x - col
        array = [[0 for _ in range(HEAT_MAP_SIZE_X)] for _ in range(HEAT_MAP_SIZE_Y)]

        # a cell is determined by the stock price and violtility (x,y)
        # Assign values
        for i in range(HEAT_MAP_SIZE_Y):
            for j in range(HEAT_MAP_SIZE_X):
                #assign
                array[i][j] = mn.quickTheoreticalFairValue(intrestRateTicker, stock_price_list[j], volatility_list[i], strikePrice, duration, call_option)

        heatmap_data = pd.DataFrame(array, index=volatility, columns=stock_price)
        heatmap_data.index.name = "Volatility(Annually)"      #label y-axis
        heatmap_data.columns.name = "Stock Price"   #label x-axis

        plt.figure(figsize=(12, 6))
        sns.heatmap(
            heatmap_data,
            annot=True,        # show numbers in each cell
            fmt=".2f",         # display with 2 decimal places
            cmap="RdYlGn"

        )
        plt.title("Black-Scholes Fair Value Heatmap")
        plt.xlabel("Stock Price")
        plt.ylabel("Volatility")
        
        # Display the plot
        plt.tight_layout()
        plt.show()

       
    def onComboBoxChanged(self, index):
        print("onComboBoxChanged")
        value = self.stock_combo_box.itemText(index)
        self.line_stockName.setText(value)

app = QApplication()
window = MainWindow()
window.show()
sys.exit(app.exec())