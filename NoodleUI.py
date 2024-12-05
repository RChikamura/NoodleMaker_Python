import os
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import NoodleQR as nqr
from NoodleHandler import Handler as nhdl


# 色(すべての要素で統一するため、変数化)
bg_color = '#f7f6e7'  # 背景色
bg_color_sub = bg_color # サブウィンドウの背景色
bg_button = '#ffa726'  # ボタンの背景色
bg_button_sub = bg_button  # サブウィンドウのボタンの背景色
bg_button_active = '#ffcc80'  # アクティブ時のボタン背景色（少し明るめのオレンジ）
bg_button_active_sub = bg_button_active  # サブウィンドウのアクティブ時のボタン背景色
bg_button_disable = '#eeeeee'  # 無効化ボタンの背景色
fg_text = '#4e342e'  # 文字色（テキスト）
fg_text_sub = fg_text  # サブウィンドウの文字色（テキスト）
fg_button = '#4e342e'  # ボタン文字色
fg_button_sub = fg_button  # サブウィンドウのボタン文字色
fg_button_disable = '#999999'  # 無効化されたテキストの色
border_sub = fg_text  # サブウィンドウの枠線色

class NoodleInterface:
    # ウィンドウで使う変数の宣言
    def __init__(self, dir, csv_manager):
        self.current_dir = dir
        self.waterSpeed = 250 # 1mlを注ぐのにかかる時間(ミリ秒)
        self.waterAmount = 300 # 最終的な水量(デフォルト値は300ml)
        self.waterDispensingTime = 0 # 給湯時間
        self.remain = 0 # 残り時間
        self.startTime = None # 給湯開始時刻
        self.after_id = None # QRコードから待機画面に戻すタイマーのID
        self.productData = ['N/A', 'N/A', 'N/A', 'N/A'] # 商品データ
        self.root = self.setup_main_window() # ウィンドウの作成
        self.sub_window = None # サブウィンドウ(あとからコマンド実行で作成)
        self.handler = nhdl(self, csv_manager) # ハンドラの初期化
        self.mode = 0 # 念の為変数にする
        self.renderUI(self.root, 0) # 待機画面で開始する
        self.root.bind("<Map>", lambda event: self.commandEntry.focus_set())
        self.root.after(100, self.commandEntry.focus_set())  # 100ミリ秒後に focus_set を呼ぶ
        self.root.after(1000, lambda:print("Current focus:", self.root.focus_get()))
        self.root.mainloop() # ウィンドウを表示

    # メインウィンドウの作成と設定
    def setup_main_window(self):
        root = tk.Tk()
        root.title('NoodleMaker')

        # ウィンドウのサイズ設定
        root.geometry('1280x720+0+0')

        # ウィンドウの装飾をなくす（フチなしにする）
        root.overrideredirect(True)

        # ウィンドウの背景色
        root.configure(bg=bg_color)

        # カーソルを非表示に設定
        root.config(cursor="none")

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
        self.stateMessage = tk.Label(target, text='いらっしゃいませ。\nバーコードをリーダーに\nかざしてください', justify='left', fg=fg_text, bg=bg_color)

        # 商品情報ラベル
        self.janText = tk.Label(target, text='コード　：N/A', fg=fg_text, bg=bg_color)
        self.amountText = tk.Label(target, text='要求湯量：N/Aml', fg=fg_text, bg=bg_color)
        self.timeText = tk.Label(target, text='待ち時間：N/A秒', fg=fg_text, bg=bg_color)
        self.genreText = tk.Label(target, text='ジャンル：N/A', fg=fg_text, bg=bg_color)

        # 水量調整ボタンを動的に追加
        self.buttonLD = self.add_adjust_button(target, '--', -50)
        self.buttonSD = self.add_adjust_button(target, '-', -10)
        self.buttonSI = self.add_adjust_button(target, '+', +10)
        self.buttonLI = self.add_adjust_button(target, '++', +50)

        # 水量表示
        self.waterText = tk.Label(target, text=self.waterAmount, fg=fg_text, bg=bg_color)

        # submitボタン(次へ進む、給湯スタート)
        self.submitButton = tk.Button(target, text='注湯量決定', fg=fg_button, bg=bg_button, activebackground=bg_button_active, relief='flat', command=lambda:self.handler.on_submit_click(target))
        # Homeボタン(待機画面へ)
        self.homeButton = tk.Button(target, text='Home', fg=fg_button, bg=bg_button, activebackground=bg_button_active, relief='flat', font=('Noto Sans JP', 20), command=lambda:self.renderUI(target, 0))

        # 非表示のEntryを作成
        self.commandEntry = tk.Entry(target)
        self.commandEntry.place(x=-300, y=-100, width=200, height=50)  # ウィンドウ外に配置
        self.commandEntry.bind('<Return>', lambda event: self.handler.on_command_enter(target, self.commandEntry, tk.END, event)) # コマンド処理



    # 水量調整ボタンを動的に追加するための関数
    def add_adjust_button(self, target, label, amount):
        button = tk.Button(target, text=label, fg=fg_button, bg=bg_button, activebackground=bg_button_active, relief='flat', command=lambda:self.handler.on_waterAdjust_click(amount))
        return button

    # ボタンを無効化し、一定時間後に有効化する関数
    def disable_button_temporarily(self, target, button, delay):
        button.config(state=tk.DISABLED, fg=fg_button_disable, bg=bg_button_disable)  # ボタンを無効化
        target.after(delay, lambda: button.config(state=tk.NORMAL, fg=fg_text, bg=bg_button))  # delayミリ秒後にボタンを有効化

    # 各表示状況における表示の配置をする関数
    def renderUI(self, target, mode):
        match mode:
            case 1: # 水量調整
                # モーターを止める(一応)
                self.handler.gms.stopMotor()
                # 商品情報表示
                self.janText.place(x=10, y=4)
                self.amountText.place(x=10, y=60)
                self.timeText.place(x=10, y=116)
                self.genreText.place(x=10, y=172)
                # 各種ボタン等
                self.buttonLD.place(x=141, y=250, width=198, height=100)
                self.buttonSD.place(x=341, y=250, width=198, height=100)
                self.waterText.place(x=541, y=250, width=198, height=100)
                self.buttonSI.place(x=741, y=250, width=198, height=100)
                self.buttonLI.place(x=941, y=250, width=198, height=100)
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
                self.handler.gms.stopMotor()
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
                self.handler.gms.stopMotor()
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
                self.handler.gms.stopMotor()
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
        # 現在のモードを変数に
        self.mode = mode

    ###UIの機能###
    # csvから得た情報を反映する関数
    def setProductData(self, target):
        # 給湯中は反応しないようにする
        if self.handler.gms.motorStopped:
            # ラベルを更新
            self.janText.config(text='コード　：' + str(self.productData[0]))
            self.amountText.config(text='要求湯量：' + str(self.productData[1]) + 'ml')
            self.timeText.config(text='待ち時間：' + str(self.productData[2]) + '秒')
            self.genreText.config(text='ジャンル：' + str(self.productData[3]))
            if self.productData[1] == 'N/A': # データがなければ
                self.waterAmount = 300 # デフォルト値 300 に
            else: # データがあれば
                self.waterAmount = self.productData[1] # 代入

            # 水量表示を更新
            self.waterText.config(text=self.waterAmount)

            # 表示遷移を水量調整画面に
            self.renderUI(target, 1)

    # 水量から給湯時間を決定
    def calcTime(self):
        # 水量が20ml未満であれば、20mlに
        if self.waterAmount < 20:
            self.waterAmount = 20
        # 時間の計算(水量(ml) * 1mlを注ぐのにかかる時間(ミリ秒))
        self.waterDispensingTime = self.waterAmount * self.waterSpeed
        self.remain = self.waterDispensingTime

    ###サブウィンドウ(コマンド表示や警告など)###
    def open_sub_window(self, target, text, small_text=False):
        # サブウィンドウが既に存在する場合は一旦閉じる
        if self.sub_window is not None and self.sub_window.winfo_exists():
            self.sub_window.destroy()

        # サブウィンドウを作成
        self.sub_window = tk.Toplevel(target)
        self.sub_window.overrideredirect(True)  # 縁無しウィンドウ
        self.sub_window.geometry('300x200')  # サイズを設定

        # ウィンドウの背景色
        self.sub_window.configure(bg=bg_color_sub)

        # ウィンドウのフォントを変更
        sub_font = tkFont.Font(family='Noto Sans JP', size=32)
        self.sub_window.option_add('*Font', sub_font)

        # サブウィンドウの中央配置を計算
        root_x = target.winfo_x()  # メインウィンドウのX座標
        root_y = target.winfo_y()  # メインウィンドウのY座標
        root_width = target.winfo_width()  # メインウィンドウの幅
        root_height = target.winfo_height()  # メインウィンドウの高さ

        sub_width = 600  # サブウィンドウの幅
        sub_height = 400  # サブウィンドウの高さ
        border_width = 1  # 枠線の幅

        # メインウィンドウの中央位置を計算
        pos_x = root_x + (root_width // 2) - (sub_width // 2) - border_width
        pos_y = root_y + (root_height // 2) - (sub_height // 2) - border_width

        # サブウィンドウ全体のサイズ（枠線を含む）
        self.sub_window.geometry(f"{sub_width + border_width*2}x{sub_height + border_width*2}+{pos_x}+{pos_y}")

        # 枠線の背景色を設定
        self.sub_window.configure(bg=border_sub)  # 枠線の色

        # 内側の内容を表示するフレームを作成
        content_frame = tk.Frame(self.sub_window, bg=bg_color_sub)
        content_frame.place(x=border_width, y=border_width, width=sub_width, height=sub_height)

        # メッセージを表示
        if small_text:  # 小さいフォントサイズ
            message = tk.Label(content_frame, text=text, fg=fg_text_sub, bg=bg_color_sub, font=tkFont.Font(family='Noto Sans JP', size=20), justify='left')
        else:
            message = tk.Label(content_frame, text=text, fg=fg_text_sub, bg=bg_color_sub)
        message.pack(expand=True)
        # 閉じるボタンを配置
        close_button = tk.Button(content_frame, text='閉じる', fg=fg_button_sub, bg=bg_button_sub, activebackground=bg_button_active_sub, relief='flat', command=self.sub_window.destroy)
        close_button.pack(expand=True)
