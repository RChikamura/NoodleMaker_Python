import os
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
from functools import partial
import gpio_motor_sensor as gms
import NoodleQR as nqr
from NoodleHandler import Handler as nhdl


# 色(すべての要素で統一するため、変数化)
bg_color = '#f7f7f7'
bg_button = '#afeeee'
bg_button_active = '#48d1cc'
bg_button_disable = '#eeeeee'
border_button = '#00afcc'
border_button_disable = '#cccccc'

class NoodleInterface:
    # ウィンドウで使う変数の宣言
    def __init__(self, dir, csv_manager):
        self.current_dir = dir
        self.mode = 3 # 現在の表示モード
        self.waterSpeed = 250 # 1mlを注ぐのにかかる時間(ミリ秒)
        self.waterAmount = 300 # 最終的な水量(デフォルト値は300ml)
        self.waterDispensingTime = 0 # 給湯時間
        self.remain = 0 # 残り時間
        self.startTime = None # 給湯開始時刻
        self.after_id = None # QRコードから待機画面に戻すタイマーのID
        self.productData = ['N/A', 'N/A', 'N/A', 'N/A'] # 商品データ
        self.root = self.setup_main_window()
        self.handler = nhdl(self, csv_manager)
        self.renderUI(self.root, 0)
        self.root.mainloop()

    # メインウィンドウの作成と設定
    def setup_main_window(self):
        root = tk.Tk()
        root.title('NoodleMaker')

        # ウィンドウのサイズ設定
        root.geometry('1280x720')

        # ウィンドウの装飾をなくす（フチなしにする）
        #root.overrideredirect(True)

        # ウィンドウの背景色(Java版を模倣)
        root.configure(bg=bg_color)

        # デフォルトのフォントを変更
        default_font = tkFont.Font(family='Noto Sans JP', size=32)
        root.option_add('*Font', default_font)

        # 部品を追加
        self.setup_window_parts(root)

        return root

    # ウィンドウに部品を追加
    def setup_window_parts(self, target):
        # 営業中の画像を読み込む
        self.Eigyo_png = ImageTk.PhotoImage(Image.open(os.path.join(self.current_dir, 'img', 'Eigyo.png')))
        # ラベルに画像を配置して表示する
        self.image_label = tk.Label(target, image=self.Eigyo_png, bg=bg_color)

        # メッセージ
        self.stateMessage = tk.Label(target, text='いらっしゃいませ。\nバーコードをリーダーに\nかざしてください', justify='left', bg=bg_color)

        # 商品情報ラベル
        self.janText = tk.Label(target, text='コード　：N/A', bg=bg_color)
        self.amountText = tk.Label(target, text='要求湯量：N/Aml', bg=bg_color)
        self.timeText = tk.Label(target, text='待ち時間：N/A秒', bg=bg_color)
        self.genreText = tk.Label(target, text='ジャンル：N/A', bg=bg_color)

        # 水量調整ボタンを動的に追加
        self.buttonLD = self.add_adjust_button(target, '--', -50)
        self.buttonSD = self.add_adjust_button(target, '-', -10)
        self.buttonSI = self.add_adjust_button(target, '+', +10)
        self.buttonLI = self.add_adjust_button(target, '++', +50)

        # 水量表示
        self.waterText = tk.Label(target, text=self.waterAmount, bg=bg_color)

        # submitボタン(次へ進む、給湯スタート)
        self.submitButton = tk.Button(target, text='注湯量決定', bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief='flat', command=lambda:self.handler.on_submit_click(target))
        # Homeボタン(待機画面へ)
        self.homeButton = tk.Button(target, text='Home', bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief='flat', font=('Noto Sans JP', 20), command=lambda:self.renderUI(target, 0))

        # 非表示のEntryを作成
        commandEntry = tk.Entry(target)
        commandEntry.place(x=1080, y=50, width=200, height=50)  # ウィンドウ外に配置
        commandEntry.bind("<Return>", lambda event: self.handler.on_command_enter(target, commandEntry, event)) # コマンド処理



    # 水量調整ボタンを動的に追加するための関数
    def add_adjust_button(self, target, label, amount):
        button = tk.Button(target, text=label,bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief='flat', command=lambda:self.handler.on_waterAdjust_click(amount))
        return button

    # ボタンを無効化し、一定時間後に有効化する関数
    def disable_button_temporarily(self, target, button, delay):
        button.config(state=tk.DISABLED, bg=bg_button_disable, highlightbackground=border_button_disable)  # ボタンを無効化
        target.after(delay, lambda: button.config(state=tk.NORMAL, bg=bg_button, highlightbackground=border_button))  # delayミリ秒後にボタンを有効化

    # 各表示状況における表示の配置をする関数
    def renderUI(self, target, mode):
        match mode:
            case 1: # 水量調整
                # モーターを止める(一応)
                gms.stopMotor()
                # 商品情報表示
                self.janText.place(x=10, y=4)
                self.amountText.place(x=10, y=60)
                self.timeText.place(x=10, y=116)
                self.genreText.place(x=10, y=172)
                # 各種ボタン等
                self.buttonLD.place(x=140, y=250, width=200, height=100)
                self.buttonSD.place(x=340, y=250, width=200, height=100)
                self.waterText.place(x=540, y=250, width=200, height=100)
                self.buttonSI.place(x=740, y=250, width=200, height=100)
                self.buttonLI.place(x=940, y=250, width=200, height=100)
                self.submitButton.config(text='注湯量決定', command=lambda:self.handler.on_submit_click(target))
                self.submitButton.place(x=440, y=375, width=400, height=125)
                self.homeButton.place(x=1180, y=0, width=100, height=50)
                # 画像は消す
                self.image_label.place_forget()
                # メッセージ
                if self.productData == ['N/A','N/A','N/A','N/A']: # データがないとき
                    self.stateMessage.config(text= '商品リストにない商品です。\n給湯が必要な場合、手動で\n湯量を選択してください。')
                    self.stateMessage.place(x=10, y=520)
                else: # データがあるとき
                    # メッセージは表示しない
                    self.stateMessage.place_forget()
            case 2: # 給湯スタート画面
                # モーターを止める(一応)
                gms.stopMotor()
                # 商品情報表示
                self.janText.place(x=10, y=4)
                self.amountText.place(x=10, y=60)
                self.timeText.place(x=10, y=116)
                self.genreText.place(x=10, y=172)
                # 調整ボタンは消す
                self.buttonLD.place_forget()
                self.buttonSD.place_forget()
                self.waterText.place_forget()
                self.buttonSI.place_forget()
                self.buttonLI.place_forget()
                # メッセージは置くだけ置いておく(扉が開いているとき、警告を表示するため)
                self.stateMessage.config(text='')
                self.stateMessage.place(x=10, y=520)
                # submitボタンをスタートボタンとして流用
                self.submitButton.config(text='Start', command=lambda:self.handler.on_start_click(target))
                self.submitButton.place(x=480, y=500, width=320, height=160)
                # ホームボタンはおいておく
                self.homeButton.place(x=1180, y=0, width=100, height=50)
                # 画像は消す
                self.image_label.place_forget()
            case 3: #QRコード表示
                # モーターを止める(一応)
                gms.stopMotor()
                # メッセージ表示
                self.stateMessage ['text'] = '画面タッチ、又は\n30秒で最初の画面に\n戻ります。'
                self.stateMessage.place(x=10, y=520)
                # QRコードにするURLを設定
                url = self.handler.makeURL()
                # URLをQRコード化し、画像ラベルに設定する
                nqr.updateQR(url, self.image_label)
                self.image_label.place(x=560, y=0)
                # それ以外のボタンやラベル等はすべて消す
                self.janText.place_forget()
                self.amountText.place_forget()
                self.timeText.place_forget()
                self.genreText.place_forget()
                self.buttonLD.place_forget()
                self.buttonSD.place_forget()
                self.waterText.place_forget()
                self.buttonSI.place_forget()
                self.buttonLI.place_forget()
                self.submitButton.place_forget()
                self.homeButton.place_forget()

            case _: # デフォルト(待機状態)
                # モーターを止める(一応)
                gms.stopMotor()
                # いらっしゃいませ
                self.stateMessage.config(text='いらっしゃいませ。\nバーコードをリーダーに\nかざしてください')
                self.stateMessage.place(x=10, y=520)
                # 営業中の画像を表示
                self.image_label['image'] = self.Eigyo_png
                self.image_label.place(x=560, y=0)
                # それ以外のボタンやラベル等はすべて消す
                self.janText.place_forget()
                self.amountText.place_forget()
                self.timeText.place_forget()
                self.genreText.place_forget()
                self.buttonLD.place_forget()
                self.buttonSD.place_forget()
                self.waterText.place_forget()
                self.buttonSI.place_forget()
                self.buttonLI.place_forget()
                self.submitButton.place_forget()
                self.homeButton.place_forget()
        self.mode = mode # modeをインスタンスの変数に出力しておく(待機画面に戻す処理で使う)

    ###UIの機能###
    # csvから得た情報を反映する関数
    def setProductData(self, target):
        # 給湯中は反応しないようにする
        if gms.motorStopped:
            # ラベルを更新
            self.janText["text"] = "コード　：" + str(self.productData[0])
            self.amountText["text"] = "要求湯量：" + str(self.productData[1]) + "ml"
            self.timeText["text"] = "待ち時間：" + str(self.productData[2]) + "秒"
            self.genreText["text"] = "ジャンル：" + str(self.productData[3])
            if self.productData[1] == "N/A": # データがなければ
                self.waterAmount = 300 # デフォルト値 300 に
            else: # データがあれば
                self.waterAmount = self.productData[1] # 代入

            # 水量表示を更新
            self.waterText["text"] = self.waterAmount

            # 表示遷移を水量調整画面に
            self.mode = self.renderUI(target, 1)

    # 水量から給湯時間を決定
    def calcTime(self):
        # 水量が20ml未満であれば、20mlに
        if self.waterAmount < 20:
            self.waterAmount = 20
        # 時間の計算(水量(ml) * 1mlを注ぐのにかかる時間(ミリ秒))
        self.waterDispensingTime = self.waterAmount * self.waterSpeed
        self.remain = self.waterDispensingTime
