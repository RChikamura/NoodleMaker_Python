#Raspberry Pi実機ではないとき、GPIOライブラリの代わりに使用
import tkinter as tk
from tkinter import Toplevel
import tkinter.font as tkFont

class dummyGPIO:
    def __init__(self):
        self.BCM = 'BCM'
        self.IN = 'INPUT'
        self.OUT = 'OUTPUT'
        self.HIGH = True
        self.LOW = False

       # ピン情報を辞書で管理
        self.pin_data = {
            17: {'mode': 'INPUT', 'state': 'HIGH', 'modelabel': '', 'valuelabel': ''},
            18: {'mode': 'OUTPUT', 'state': 'LOW', 'modelabel': '', 'valuelabel': ''},
        }

    def open_IOwindow(self, target):
        # サブウィンドウを作成
        IOwindow = Toplevel(target)
        IOwindow.title('dummyGPIO')
        IOwindow.geometry('250x100')  # サイズを指定

        # デフォルトのフォントを変更
        default_font = tkFont.Font(family='Noto Sans JP', size=16)
        IOwindow.option_add('*Font', default_font)

        modeLabel = tk.Label(IOwindow, text='GPIO mode')
        modeLabel.grid(column=0, row=0)
        self.modeValue = tk.Label(IOwindow, text=self.BCM)
        self.modeValue.grid(column=1, row=0)

        pinLabel17 = tk.Label(IOwindow, text='Pin17')
        pinLabel17.grid(column=0, row=1)
        self.pinMode17 = tk.Label(IOwindow, text=self.pin_data[17]['mode'])
        self.pinMode17.grid(column=1, row=1)
        var = tk.BooleanVar(value=(self.pin_data[17]['state'] == 'HIGH'))
        # チェックボックスを作成
        self.pinValue17 = tk.Checkbutton(IOwindow, variable=var, onvalue=True, offvalue=False, command=lambda p=17, v=var: self.update_state(p, v))
        self.pinValue17.grid(column=2, row=1)

        pinLabel18 = tk.Label(IOwindow, text='Pin18')
        pinLabel18.grid(column=0, row=2)
        self.pinMode18 = tk.Label(IOwindow, text=self.pin_data[18]['mode'])
        self.pinMode18.grid(column=1, row=2)
        self.pinValue18 = tk.Label(IOwindow, text=self.pin_data[18]['state'])
        self.pinValue18.grid(column=2, row=2)

        self.pin_data[17]['modelabel'] = self.pinMode17
        self.pin_data[17]['valuelabel'] = self.pinValue17
        self.pin_data[18]['modelabel'] = self.pinMode18
        self.pin_data[18]['valuelabel'] = self.pinValue18

        # サブウィンドウを常に前面に表示
        IOwindow.attributes('-topmost', True)

    def setmode(self, mode):
        # GPIOのモード設定
        self.modeValue.config(text=mode)

    def setup(self, pin, mode):
        self.pin_data[pin]['mode'] = mode
        # 面倒なので両方更新
        self.pin_data[pin]['modelabel'].config(text=self.pin_data[pin]['mode'])

    def output(self, pin, state):
        if state:
            self.pin_data[pin]['state'] = 'HIGH'
        else:
            self.pin_data[pin]['state'] = 'LOW'
        self.pin_data[pin]['valuelabel'].config(text=self.pin_data[pin]['state'])

    def input(self, pin):
        if self.pin_data[pin]['state'] == 'HIGH':
            state = True
        else:
            state = False
        return state

    # inputピンの状態をチェックボックスから更新
    def update_state(self, pin, var):
        if var.get():
            self.pin_data[pin]['state'] = 'HIGH'
        else:
            self.pin_data[pin]['state'] = 'LOW'


dio = dummyGPIO()


if __name__ == '__main__':
    root = tk.Tk()
    dio.open_IOwindow(root)
    root.mainloop()
