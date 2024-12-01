# gpioが関係するコード
#import wiringpi as wpi
#import time

# RPi.GPIOライブラリをインポートして、GPIOを操作しようとしてみる
try:
    import RPi.GPIO as GPIO
    # BCMモードを使用(GPIO番号でピンを指定)
    GPIO.setmode(GPIO.BCM)
except: # Raspberry Pi 実機でなければエラーが出るはずなので、その場合はダミーファイルを使う
    import dummyGPIO as GPIO


# ピン番号の指定
signalPin = 18
sensorPin = 17

# 給湯完了を伝えるためのフラグ
motorStopped = True

# pinModeの設定
GPIO.setup(signalPin, GPIO.OUT) # モーター制御ピン
GPIO.setup(sensorPin, GPIO.IN) # ドアセンサーピン

# ポンプを回す関数。
def startMotor():
    global motorStopped
    # 給湯完了フラグをFalseに
    motorStopped = False
    # モーターON
    GPIO.output(signalPin, GPIO.HIGH)

# ポンプを停止する関数
def stopMotor():
    #規定量のお湯(水)が注げたらモーターOFF
    GPIO.output(signalPin, GPIO.LOW)
    # 給湯完了フラグをTrueに
    global motorStopped
    motorStopped = True

# センサーを読む関数
def sensorInput():
    # プルアップのセンサーなので、HIGHの時開いている状態
    if GPIO.input(sensorPin) == GPIO.HIGH:
        return False # Falseを返す
    else:
        return True

