import time
import gpio_motor_sensor as gms

class Handler:
    def __init__(self, interface, csv_manager):
        self.UI = interface  # NoodleInterfaceのインスタンス
        self.csv = csv_manager  # NoodleCSVのインスタンス

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
        self.UI.mode = self.UI.renderUI(target, 2)
    # スタート
    def on_start_click(self, target):
        # 扉が開いている場合
        if not gms.sensorInput():
            self.UI.stateMessage.config(text="扉が開いています。\n閉じてください。")
            return  # ここで処理終了

        # ポンプが停止中の場合
        if gms.motorStopped:
            self.start_dispensing(target)
        else:
            self.stop_dispensing()

    # 給湯を開始する関数
    def start_dispensing(self, target):
        self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n一時停止する場合は、\nStopボタンをタップ")
        self.UI.startTime = time.time() * 1000
        startRemain = self.UI.remain

        gms.startMotor()  # モーター起動
        self.checkMotorState(target, startRemain)  # 状態を監視
        self.UI.disable_button_temporarily(target, self.UI.submitButton, 2000)
        self.UI.submitButton.config(text="Stop")  # ボタンを「Stop」に変更

    # 給湯を停止する関数
    def stop_dispensing(self):
        gms.stopMotor()  # モーター停止
        self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n再開する場合は、\nStartボタンをタップ")
        self.UI.disable_button_temporarily(self.UI.submitButton, 2000)
        self.UI.submitButton.config(text="Start")  # ボタンを「Start」に変更

    # モーターの状態を監視するための関数
    def checkMotorState(self, target, startRemain):
        # 残り時間が 0 なら終了処理
        if self.UI.remain <= 0:
            gms.stopMotor()
            self.setup_qr_screen(target)  # QRコード画面に遷移
            return

        # 扉が開いた場合
        if not gms.sensorInput():
            gms.stopMotor()
            self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n扉を閉じてから、\nStartボタンをタップ")
            self.UI.submitButton.config(text="Start")  # ボタンを「Start」に戻す
            return

        # 給湯中の場合は次のチェックをスケジュール
        self.UI.remain = startRemain - (time.time() * 1000 - self.UI.startTime)
        self.UI.stateMessage.config(text=f"給湯中 残り {int(self.UI.remain / 1000)}秒\n一時停止する場合は、\nStopボタンをタップ")
        self.UI.root.after(100, lambda: self.checkMotorState(target, startRemain))

    # 待機画面に戻る処理
    def returnWelcome(self, target):
        if self.UI.mode == 3:
            self.UI.renderUI(target, 0)
            self.cleanup_qr_events(target)

    # QRコード画面のセットアップ
    def setup_qr_screen(self, target):
        self.UI.renderUI(target, 3)
        target.bind("<Button-1>", lambda:self.on_click(target))  # クリックイベントをバインド
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
    def on_command_enter(self, target, entry, event):
        command = entry.get()
        match command:
            case '99999995':
                # ウィンドウが非表示なら
                if target.state() == 'withdrawn':
                    # 終了
                    target.destroy()
                else:
                    # GUIを消す
                    target.withdraw()
            case 'exit':
                # 終了
                target.destroy()
            case 'reload':
                self.csv.getCSV(self.csv.csv_path)
                # CSVを読み込み直したい時に reload コマンドで再読み込みさせる
                print('CSVの再読み込みに成功')
            case 'h' | 'help' | '?':
                print('exit - このシェルを抜けます\nreload - CSVを再読み込みします\ngui, g - データ表示用ウィンドウを表示します\nnogui - データ表示用ウィンドウを閉じます\nqr - データ表示用ウィンドウにQRコードを表示します\nbutton, b - 強制的にスタートボタン画面に遷移し、前回の設定時間で吐水します。\nr - 強制的に待機画面に戻します\ndata - 読み込んだcsvの内容を表示します。デバッグ用です。\nh, help, ? - このヘルプを表示します')
                # 削除した内容
                '''
                button, b - 状況に関わらず強制的にスタートボタンをデータ表示用ウィンドウに表示させます。\n
                sh - 直近に取得した商品データに対応した時間吐水させるスクリプトを実行します。~/Documents/jp.ac.uClub/にOutGPIO.shというシェルスクリプトが必要です\n
                    buttonコマンドに統合
                control(説明なし) よくわからなかったし、たぶんなくても動きはするのでとりあえず無視
                '''
                # 追加した内容
                '''
                r - 強制的に待機画面に戻します\n    説明はなかったが実装されていたので、移植して説明書きを追加
                '''

                # なんちゃってヘルプを表示
            case 'g' | 'gui' | '99999988':
                # GUIを表示
                target.deiconify()
            case 'nogui':
                # GUIを消す
                target.withdraw()
            case 'qr':
                #qrコード表示
                self.UI.mode = self.UI.renderUI(target, 3)
            #case 'sh':
                #System.out.println(GPIOOutput(String.valueOf(waterDispensingTimeText)));
                #continue;
            case 'b' | 'button':
                # スタートボタン
                self.UI.mode = self.UI.renderUI(target, 2)
                # 残り時間を前回実行時のデータから復元
                self.UI.remain = self.UI.waterDispensingTime
                #continue;
            #case 'control':
                #addControl();
                #continue;
            #case 'data':
                # 読み込んだcsvの内容を表示
                #from IPython.display import display
                #dataframe = pd.DataFrame(data)
                #display(dataframe)
            case 'speed':
                #注水速度調整
                waterSpeed = int(input(f'water speed({waterSpeed})>'))
            case 'r':
                # 強制的に待機画面へ
                self.UI.mode = self.UI.renderUI(target, 0)
            case _:
                # ユーザー入力された文字列に対応する商品があるか検索
                try:
                    self.UI.productData = self.csv.searchData(int(command))
                    # 表示更新
                    self.UI.setProductData(target)
                except: # 何らかのエラーが出た場合
                    self.UI.stateMessage.config(text='入力にエラーがあります。')
                    print('入力にエラーがあります。')

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
