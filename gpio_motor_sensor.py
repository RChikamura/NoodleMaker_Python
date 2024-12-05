# gpioが関係するコード
# ダミーのGPIOを使用しているかどうか
isDummy = False
# RPi.GPIOライブラリをインポートして、GPIOを操作しようとしてみる
try:
    import RPi.GPIO as GPIO
    # BCMモードを使用(GPIO番号でピンを指定)
    GPIO.setmode(GPIO.BCM)
except: # Raspberry Pi 実機でなければエラーが出るはずなので、その場合はダミーファイルを使う
    from dummyGPIO import dio as GPIO
    isDummy = True

class NoodleGPIO:
    def __init__(self, windowTarget):
        if isDummy:
            GPIO.open_IOwindow(windowTarget) # ダミーの場合、サブウィンドウ表示
        # ピン番号の指定
        self.signalPin = 18
        self.sensorPin = 17

        # 給湯完了を伝えるためのフラグ
        self.motorStopped = True

        # pinModeの設定
        GPIO.setup(self.signalPin, GPIO.OUT) # モーター制御ピン
        GPIO.setup(self.sensorPin, GPIO.IN) # ドアセンサーピン

    # ポンプを回す関数。
    def startMotor(self):
        # 給湯完了フラグをFalseに
        self.motorStopped = False
        # モーターON
        GPIO.output(self.signalPin, GPIO.HIGH)

    # ポンプを停止する関数
    def stopMotor(self):
        #規定量のお湯(水)が注げたらモーターOFF
        GPIO.output(self.signalPin, GPIO.LOW)
        # 給湯完了フラグをTrueに
        self.motorStopped = True

    # センサーを読む関数
    def sensorInput(self):
        # プルアップのセンサーなので、HIGHの時開いている状態
        if GPIO.input(self.sensorPin) == GPIO.HIGH:
            return False # Falseを返す
        else:
            return True
