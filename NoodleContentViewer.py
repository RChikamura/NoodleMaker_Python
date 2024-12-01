import time
import tkinter as tk
from PIL import Image, ImageTk
import tkinter.font as tkFont
import gpio_motor_sensor as gms
import qrcode
import io
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

###グローバル変数###
# デバッグ用出力の有効化
debug = False

# メインプログラムから転送されタデータ
productData = ["N/A","N/A","N/A","N/A"]

# 最終的な注水量(デフォルト値は300ml)
waterAmount = 300

# 1mlを注ぐのにかかる時間(ミリ秒)
waterSpeed = 250

# 現在の表示モード
mode = 0

# 30秒後に画面遷移する処理のid
after_id = None

# 色(すべての要素で統一するため、変数化)
bg_color = '#f7f7f7'
bg_button = '#afeeee'
bg_button_active = '#48d1cc'
bg_button_disable = '#eeeeee'
border_button = '#00afcc'
border_button_disable = '#cccccc'

# 給湯時間(ミリ秒)
waterDispensingTime = 0
# 残り時間(ミリ秒)
remain = 0
# ポンプのスタート時間
startTime = None

###ウィンドウの設定###
# メインウィンドウの作成
root = tk.Tk()
root.title("NoodleMaker")

# ウィンドウのサイズ設定
root.geometry("1280x720")

# ウィンドウの装飾をなくす（フチなしにする）
root.overrideredirect(True)

# ウィンドウの背景色(Java版を模倣)
root.configure(bg=bg_color)

# デフォルトのフォントを変更
default_font = tkFont.Font(family="Noto Sans JP", size=32)
root.option_add("*Font", default_font)

### ウィンドウに表示する部品 ###
# 営業中の画像を読み込む
Eigyo_png = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, "img", "Eigyo.png")))
# ラベルに画像を配置して表示する
image_label = tk.Label(root, image=Eigyo_png, bg=bg_color)

# 商品の情報を表示するラベル
janText = tk.Label(root, text="コード　：N/A", bg=bg_color)
amountText = tk.Label(root, text="要求湯量：N/Aml", bg=bg_color)
timeText = tk.Label(root, text="待ち時間：N/A秒", bg=bg_color)
genreText = tk.Label(root, text="ジャンル：N/A", bg=bg_color)

stateMessage = tk.Label(root, text="いらっしゃいませ。\nバーコードをリーダーに\nかざしてください", justify='left', bg=bg_color)

# ボタンを押したときの機能
# 水量調整
def on_waterAdjust_click(adjust):
    global waterAmount # グローバル変数 waterAmountの使用
    waterAmount += adjust # waterAmountにボタンごとの固有値(引数)を加算
    # 水量が20ml未満であれば、20mlに
    if waterAmount < 20:
        waterAmount = 20
    waterText["text"] = waterAmount # 水量表示を更新
# submit
def on_submit_click():
    global mode
    # 時間を計算
    calcTime()
    # 表示を給湯スタート画面に
    mode =renderUI(2)
# スタート
def on_start_click():
    global remain, startTime
    if gms.sensorInput() == False: # 扉が閉じていないことを検知した場合
        stateMessage ["text"] = "扉が開いています。\n閉じてください。"
    elif gms.motorStopped: # ポンプが動いていないとき
        global mode
        stateMessage ["text"] = f"給湯中 残り {int(remain/1000)}秒\n一時停止する場合は、\nStopボタンをタップ"
        # ポンプ起動
        startTime = time.time() * 1000
        startRemain = remain
        gms.startMotor()
        checkMotorState(startRemain)
        disable_button_temporarily(submit, 2000)  # 誤タップ防止のため2秒間無効化
        submit["text"] = "Stop"  # ボタンのラベルを変更
    else: # モーターが動いているとき
        # モーターを止める
        gms.stopMotor()
        stateMessage ["text"] = f"給湯中 残り {int(remain/1000)}秒\n再開する場合は、\nStartボタンをタップ"
        disable_button_temporarily(submit, 2000)  # 誤タップ防止のため2秒間無効化
        submit["text"] = "Start"  # ボタンのラベルを変更

# ポンプの状態をチェックする関数
def checkMotorState(startRemain):
    global mode, remain, startTime
    # 残り時間が 0 なら
    if remain <= 0:
        # モーターを止める
        gms.stopMotor()
        # 表示をQRコード表示に
        mode = renderUI(3)
    if not gms.sensorInput(): # ドアが開いていたら
        # モーターを止める
        gms.stopMotor()
        stateMessage ["text"] = f"給湯中 残り {int(remain/1000)}秒\n扉を閉じてから、\nStartボタンをタップ"
        disable_button_temporarily(submit, 2000)  # 誤タップ防止のため2秒間無効化
        submit["text"] = "Start"  # ボタンのラベルを変更 
    elif not gms.motorStopped:
        # 100ミリ秒後にもう一度チェック
        root.after(100, lambda:checkMotorState(startRemain))
        # 残り時間を計算
        remain = startRemain - (time.time()*1000 - startTime)
        stateMessage ["text"] = f"給湯中 残り {int(remain/1000)}秒\n一時停止する場合は、\nStopボタンをタップ"

# ボタンを無効化し、一定時間後に有効化する関数
def disable_button_temporarily(button, delay):
    button.config(state=tk.DISABLED, bg=bg_button_disable, highlightbackground=border_button_disable)  # ボタンを無効化
    root.after(delay, lambda: button.config(state=tk.NORMAL, bg=bg_button, highlightbackground=border_button))  # delayミリ秒後にボタンを有効化

# ボタンの追加と配置
# --ボタン(-50ml)
largeDecrease = tk.Button(root, text="--",bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief="flat", command=lambda:on_waterAdjust_click(-50))
# -ボタン(-10ml)
smallDecrease = tk.Button(root, text="-", bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief="flat", command=lambda:on_waterAdjust_click(-10))
# 水量表示
waterText = tk.Label(root, text=waterAmount, bg=bg_color)
# +ボタン(+10ml)
smallIncrease = tk.Button(root, text="+", bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief="flat", command=lambda:on_waterAdjust_click(10))
# ++ボタン(+50ml)
largeIncrease = tk.Button(root, text="++", bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief="flat", command=lambda:on_waterAdjust_click(50))
# submitボタン(次へ進む)
submit = tk.Button(root, text="注湯量決定", bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief="flat", command=on_submit_click)
# Homeボタン(待機画面へ)
home = tk.Button(root, text="Home", bg=bg_button, activebackground=bg_button_active, highlightbackground=border_button, relief="flat", font=("Noto Sans JP", 20), command=lambda:renderUI(0))

# QR画面のままなら、戻る関数
def returnWelcome():
    global mode
    if mode == 3:
        mode = renderUI(0)
    # クリックイベントをアンバインドしておく
    root.unbind("<Button-1>")
    # 時間経過での画面遷移処理をキャンセルしておく
    if after_id is not None:
        root.after_cancel(after_id)

def createQR(data):
    # QRコードを生成する
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=30,
        border=6,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def updateQR(data, target):
    # データを取得してQRコードを更新する
    img = createQR(data)

    # 画像をリサイズして720px四方にする
    img_resized = img.resize((720, 720), Image.Resampling.LANCZOS)
    # 画像をメモリ上に保存してtkinterで表示できるようにする
    with io.BytesIO() as output:
        img_resized.save(output, format="PNG")
        #img.save(output, format="PNG")
        img_data = output.getvalue()
    img_tk = ImageTk.PhotoImage(data=img_data)
    target.config(image=img_tk)
    target.image = img_tk  # 参照を保持してガベージコレクションを防ぐ

# クリックイベントのハンドラ
def on_click(event):
    # returnWelcome関数を実行
    returnWelcome()

# 各表示状況における表示の配置をする関数
def renderUI(mode):
    match mode:
        case 1: # 水量調整
            # モーターを止める(一応)
            gms.stopMotor()
            # 商品情報表示
            janText.place(x=10, y=4)
            amountText.place(x=10, y=60)
            timeText.place(x=10, y=116)
            genreText.place(x=10, y=172)
            # 各種ボタン等
            largeDecrease.place(x=140, y=250, width=200, height=100)
            smallDecrease.place(x=340, y=250, width=200, height=100)
            waterText.place(x=540, y=250, width=200, height=100)
            smallIncrease.place(x=740, y=250, width=200, height=100)
            largeIncrease.place(x=940, y=250, width=200, height=100)
            submit["text"] = "注湯量決定"
            submit["command"] = on_submit_click
            submit.place(x=440, y=375, width=400, height=125)
            home.place(x=1180, y=0, width=100, height=50)
            # 画像は消す
            image_label.place_forget()
            # メッセージ
            if productData == ["N/A","N/A","N/A","N/A"]: # データがないとき
                stateMessage["text"] = "商品リストにない商品です。\n給湯が必要な場合、手動で\n湯量を選択してください。"
                stateMessage.place(x=10, y=520)
            else: # データがあるとき
                # メッセージは表示しない
                stateMessage.place_forget()
        case 2: # 給湯スタート画面
            # モーターを止める(一応)
            gms.stopMotor()
            # 商品情報表示
            janText.place(x=10, y=4)
            amountText.place(x=10, y=60)
            timeText.place(x=10, y=116)
            genreText.place(x=10, y=172)
            # 調整ボタンは消す
            largeDecrease.place_forget()
            smallDecrease.place_forget()
            waterText.place_forget()
            smallIncrease.place_forget()
            largeIncrease.place_forget()
            # メッセージは置くだけ置いておく(扉が開いているとき、警告を表示するため)
            stateMessage ["text"] = ""
            stateMessage.place(x=10, y=520)
            # submitボタンをスタートボタンとして流用(大きさが違うため、背景画像も交換)
            submit["text"] = "Start"
            submit["command"] = on_start_click
            submit.place(x=480, y=500, width=320, height=160)
            # ホームボタンはおいておく
            home.place(x=1180, y=0, width=100, height=50)
            # 画像は消す
            image_label.place_forget()
        case 3: #QRコード表示
            global after_id
            # モーターを止める(一応)
            gms.stopMotor()
            # メッセージ表示
            stateMessage ["text"] = "画面タッチ、又は\n30秒で最初の画面に\n戻ります。"
            stateMessage.place(x=10, y=520)
            # QRコードを用意
            url = "https://noodle-timer.netlify.app/?"
            if productData[2] == 'N/A':
                url += "start=" + str(int(time.time()*1000)) + "&kinds=" + productData[3]
            else:
                url += "time=" + str(int(time.time()*1000) + (productData[2] * 1000)) +"&start=" + str(int(time.time()*1000))
            if productData[3] != 'N/A':
                 url += "&kinds=" + productData[3]
            updateQR(url, image_label)
            image_label.place(x=560, y=0)
            # それ以外のボタンやラベル等はすべて消す
            janText.place_forget()
            amountText.place_forget()
            timeText.place_forget()
            genreText.place_forget()
            largeDecrease.place_forget()
            smallDecrease.place_forget()
            waterText.place_forget()
            smallIncrease.place_forget()
            largeIncrease.place_forget()
            submit.place_forget()
            home.place_forget()
            # クリックイベントをバインド
            root.bind("<Button-1>", on_click)
            # 30秒経過後、待機画面になっていなければ戻す
            after_id = root.after(30000, returnWelcome)  # 30000ミリ秒 = 30秒

        case _: # デフォルト(待機状態)
            # モーターを止める(一応)
            gms.stopMotor()
            # いらっしゃいませ
            stateMessage ["text"] = "いらっしゃいませ。\nバーコードをリーダーに\nかざしてください"
            stateMessage.place(x=10, y=520)
            # 営業中の画像を表示
            image_label["image"] = Eigyo_png
            image_label.place(x=560, y=0)
            # それ以外のボタンやラベル等はすべて消す
            janText.place_forget()
            amountText.place_forget()
            timeText.place_forget()
            genreText.place_forget()
            largeDecrease.place_forget()
            smallDecrease.place_forget()
            waterText.place_forget()
            smallIncrease.place_forget()
            largeIncrease.place_forget()
            submit.place_forget()
            home.place_forget()
    return mode # modeを出力しておく(待機画面に戻す処理で使う)


def setProductData(jan, amount, time, genre):
    # グローバル変数の使用
    global productData
    global waterAmount
    global mode
    # 給湯中は反応しないようにする
    if gms.motorStopped:
        # メインプログラムから送信されたデータを保存
        productData = [jan, amount, time, genre]

        # ラベルを更新
        janText["text"] = "コード　：" + str(jan)
        amountText["text"] = "要求湯量：" + str(amount) + "ml"
        timeText["text"] = "待ち時間：" + str(time) + "秒"
        genreText["text"] = "ジャンル：" + str(genre)
        if amount == "N/A": # データがなければ
            waterAmount = 300 # デフォルト値 300 に
        else: # データがあれば
            waterAmount = amount # 代入

        # 水量表示を更新
        waterText["text"] = waterAmount

        # 表示遷移を水量調整画面に
        mode =renderUI(1)

def calcTime():
    global waterAmount
    global waterDispensingTime
    global remain
    # 水量が20ml未満であれば、20mlに
    if waterAmount < 20:
        waterAmount = 20
    # 時間の計算(水量(ml) * 1mlを注ぐのにかかる時間(ミリ秒))
    waterDispensingTime = waterAmount * waterSpeed
    remain = waterDispensingTime

    # デバッグ用
    if debug:
        print(f'給湯時間: {waterDispensingTime / 1000} 秒')

# ウィンドウを非表示にする関数
def hide_window():
    root.withdraw()

# ウィンドウを再表示する関数
def show_window():
    root.deiconify()

# ウィンドウのメインループを開始する関数
def windowMainloop():
    root.mainloop()

# このプログラムを直接実行したとき
if __name__ == "__main__":
    import threading
    # とりあえず待機画面を出す。ただし、何もできない
    mode =renderUI(0)
    # GUIを別スレッドで起動
    gui_thread = threading.Thread(target=windowMainloop)
    gui_thread.daemon = True  # メインプログラムが終了したらGUIも終了するようにする
    while True:
        str_test = input('終了するにはexitと入力\n続行する場合はなにか入力\n>>>')
        if str_test == 'exit':
            break
        else:
            # 表示遷移を水量調整画面に
            mode =renderUI(1)
            
