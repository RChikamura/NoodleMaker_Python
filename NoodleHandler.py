import time
from gpio_motor_sensor import NoodleGPIO as nio

class Handler:
    def __init__(self, interface, csv_manager):
        self.UI = interface  # NoodleInterfaceのインスタンス
        self.csv = csv_manager  # NoodleCSVのインスタンス
        self.gms = nio(self.UI.root)

    # ボタンを押したときの機能
    # 水量調整
    def on_waterAdjust_click(self, adjust):
        self.UI.waterAmount += adjust # waterAmountにボタンごとの固有値(引数)を加算
        # 水量が20ml未満であれば、20mlに
        if self.UI.waterAmount < 20:
            self.UI.waterAmount = 20
        self.UI.waterText.config(text=self.UI.waterAmount) # 水量表示を更新

    # submit
    def on_submit_click(self, target):
        # 時間を計算
        self.UI.calcTime()
        # 表示を給湯スタート画面に
        self.UI.renderUI(target, 2)
    # スタート
    def on_start_click(self, target):
        # 扉が開いている場合
        if not self.gms.sensorInput():
            self.alert_open(target)
            self.UI.stateMessage.config(text="扉が開いています。\n閉じてください。")
            return  # ここで処理終了

        # ポンプが停止中の場合
        if self.gms.motorStopped:
            self.start_dispensing(target)
        else:
            self.stop_dispensing(target)

    # 給湯を開始する関数
    def start_dispensing(self, target):
        self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n一時停止する場合は、\nStopボタンをタップ")
        self.UI.startTime = time.time() * 1000
        startRemain = self.UI.remain

        self.gms.startMotor()  # モーター起動
        self.checkMotorState(target, startRemain)  # 状態を監視
        self.UI.disable_button_temporarily(target, self.UI.submitButton, 2000)
        self.UI.submitButton.config(text="Stop")  # ボタンを「Stop」に変更

    # 給湯を停止する関数
    def stop_dispensing(self, target):
        self.gms.stopMotor()  # モーター停止
        self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n再開する場合は、\nStartボタンをタップ")
        self.UI.disable_button_temporarily(target, self.UI.submitButton, 2000)
        self.UI.submitButton.config(text="Start")  # ボタンを「Start」に変更

    # モーターの状態を監視するための関数
    def checkMotorState(self, target, startRemain):
        # 残り時間が 0 なら終了処理
        if self.UI.remain <= 0:
            self.gms.stopMotor()
            self.setup_qr_screen(target)  # QRコード画面に遷移
            return

        # 扉が開いた場合
        if not self.gms.sensorInput():
            self.gms.stopMotor()
            self.alert_open(target)
            self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n扉を閉じてから、\nStartボタンをタップ")
            self.UI.submitButton.config(text="Start")  # ボタンを「Start」に戻す
            return

        # 給湯中の場合は次のチェックをスケジュール
        if not self.gms.motorStopped:
            self.UI.remain = startRemain - (time.time() * 1000 - self.UI.startTime)
            self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n一時停止する場合は、\nStopボタンをタップ")
            self.UI.root.after(100, lambda: self.checkMotorState(target, startRemain))

    # 扉が開いている警告を出す関数
    def alert_open(self, target):
        message = '扉が開いています。\n閉じてください。'
        self.UI.open_sub_window(target, message)

    # 待機画面に戻る処理
    def returnWelcome(self, target):
        if self.UI.mode == 3:
            self.UI.renderUI(target, 0)
        self.cleanup_qr_events(target)

    # QRコード画面のセットアップ
    def setup_qr_screen(self, target):
        target.bind("<Button-1>", lambda event: self.on_click(target, event))  # クリックイベントをバインド
        self.UI.renderUI(target, 3)
        self.after_id = target.after(30000, lambda: self.returnWelcome(target))  # 30秒後に戻る処理を設定

    # クリックイベントのハンドラ
    def on_click(self, target, event):
        self.returnWelcome(target)

    # QRコード画面のイベントを解除
    def cleanup_qr_events(self, target):
        target.unbind("<Button-1>")  # クリックイベントを解除
        if self.UI.after_id is not None:
            target.after_cancel(self.after_id)  # タイマーイベントを解除
            self.after_id = None

    # Enterキーが押されたときにEntryの値を取得
    def on_command_enter(self, target, entry, end, event): # end引数は、このファイルでtkinterをimportしておらず、tk.ENDが使えないために代理で使用
        # サブウィンドウが既に存在する場合は一旦閉じる
        if self.UI.sub_window is not None and self.UI.sub_window.winfo_exists():
            self.UI.sub_window.destroy()

        command = entry.get()
        entry.delete(0, end)  # 入力欄をクリア
        match command:
            case 'exit' | '99999995':
                # 終了
                target.destroy()
            case 'reload':
                self.csv.getCSV(self.csv.csv_path)
                # CSVを読み込み直したい時に reload コマンドで再読み込みさせる
                print('CSVの再読み込みに成功')
            case 'h' | 'help' | '?':
                # なんちゃってヘルプを表示
                message = 'exit - この アプリを終了します\nreload - CSVを再読み込みします\nqr - QRコードを再表示します\nbutton, b - スタートボタン画面に遷移し、\n              前回の設定時間で吐水します。\nsh - Startボタンを押すコマンド。\n       ボタンウィンドウ専用コマンドです。\nr - 強制的に待機画面に戻します\nh, help, ? - このヘルプを表示します'
                self.UI.open_sub_window(target, message, True)
            case 'qr':
                #qrコード表示
                self.setup_qr_screen(target)
            case 'b' | 'button':
                # スタートボタン
                self.UI.renderUI(target, 2)
                # 残り時間を前回実行時のデータから復元
                self.UI.remain = self.UI.waterDispensingTime
            case 'sh':
                if self.UI.mode == 2: # ボタンウィンドウなら
                    self.on_start_click(target)
                else:
                    message = 'ボタンウィンドウ専用コマンドです'
                    self.UI.open_sub_window(target, message)
            case 'speed':
                message = '注水速度を調整します。\nターミナルをアクティブにし、\n注水速度[ml/s]を入力して\nください。'
                self.UI.open_sub_window(target, message)
                #注水速度調整
                self.UI.waterSpeed = int(input(f'water speed({self.UI.waterSpeed})>'))
                message = f'注水速度: {self.UI.waterSpeed}[ml/s]'
                self.UI.open_sub_window(target, message)
            case 'r':
                # 強制的に待機画面へ
                self.UI.renderUI(target, 0)
            case '':
                # 何もしない
                pass
            case _:
                # ユーザー入力された文字列に対応する商品があるか検索
                try:
                    self.UI.productData = self.csv.searchData(int(command))
                    # 表示更新
                    self.UI.setProductData(target)
                except: # 何らかのエラーが出た場合
                    message = '入力にエラーがあります。'
                    self.UI.open_sub_window(target, message)

    # QRコードに対応するURLの作成(本来ここに置くべきかわからないが、timeモジュールのインポートがあるのでここに置く)
    def makeURL(self):
        url = 'https://noodle-timer.netlify.app/?'
        if self.UI.productData[2] == 'N/A': # 時間の設定がないとき
            # 開始時刻だけでも教える
            url += 'start=' + str(int(time.time()*1000))
        else: # 時間の設定があるとき
            # 開始時刻と終了時刻を自動で設定
            url += 'time=' + str(int(time.time()*1000) + (self.UI.productData[2] * 1000)) +'&start=' + str(int(time.time()*1000))
        if self.UI.productData[3] != 'N/A': # 種類の設定があるとき
            # 種類もURLに含める
            url += '&kinds=' + self.UI.productData[3]
        return url
