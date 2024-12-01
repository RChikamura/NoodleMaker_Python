import pandas as pd
import os
import NoodleContentViewer as gui
import threading

# デバッグ用出力の有効化
debug = False

# cupData.csvのパス(このpyファイルと同一ディレクトリ)
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir,"cupData.csv")
data = None

# メインループを実行するかのフラグ
flg_loop = True

# csvファイルを読み込むか、新規作成する関数
def getCSV():
    global data
    # csvファイルが存在するか確認
    if not os.path.exists(csv_path):
        # 存在しなければファイルを作成
        with open(csv_path, 'w') as file:
            file.write("jan,water,time,category")  # ヘッダー行のみの空のファイルを作成
        if debug:
            print(f"ファイルを新しく作成しました: {csv_path}")
    else:
        # pandasでcsvファイルを読み込む
        data = pd.read_csv(csv_path)
        if debug:
            print(f"csvファイルが見つかりました: {csv_path}")
            # データを表示する（確認用）
            print(data)

# csvから商品を探し、情報を取得する関数
def searchData(jan):
    global data
    if data is None:
        print("データが読み込まれていません。まずCSVファイルを読み込んでください。")
        return

    # キーを含む行をフィルタリング
    matching_rows = data[data['jan'] == jan]

    if not matching_rows.empty:
        if debug:
            print(f'{jan}が見つかりました')
        # ヒットした最初の行の残り3つの列の値を取得
        amount = matching_rows.iloc[0]['water']
        time = matching_rows.iloc[0]['time']
        genre = matching_rows.iloc[0]['category']

        # NoodleContentViewに各種データを受け渡し
        gui.setProductData(jan, amount, time, genre)

        if debug:
            print(f'Janコード: {jan}')
            print(f'必要湯量(ml): {amount}')
            print(f'待ち時間(s): {time}')
            print(f'ジャンル: {genre}')
    else:
        # もらってきたjanが無かった場合
        if debug:
            print(f"キー '{jan}' は存在しません。")
        # GUI側にダミーの"N/A"を渡してあげる
        gui.setProductData("N/A","N/A","N/A","N/A")

# 初期設定
def initApp():
    # 起動時のcsv読み込み
    getCSV()

    # 待機画面を表示する準備
    gui.renderUI(0)

    # GUIを別スレッドで起動
    gui_thread = threading.Thread(target=gui.windowMainloop)
    gui_thread.daemon = True  # メインプログラムが終了したらGUIも終了するようにする


if __name__ == "__main__":
    # 起動時に初期化
    initApp()
    # メインループ
    while flg_loop:
        command = input("NoodleShell>")
        match command:
            case "99999995":
                # ウィンドウが非表示なら
                if gui.root.state() == "withdrawn":
                    # 無限ループを抜け、終了させる
                    flg_loop = False
                else:
                    # GUIを消す
                    gui.hide_window()
            case "exit":
                # 無限ループを抜け、終了させる
                flg_loop = False
            case "reload":
                getCSV()
                # CSVを読み込み直したい時に reload コマンドで再読み込みさせる
                print("CSVの再読み込みに成功")
            case "h" | "help" | "?":
                print("exit - このシェルを抜けます\nreload - CSVを再読み込みします\ngui, g - データ表示用ウィンドウを表示します\nnogui - データ表示用ウィンドウを閉じます\nqr - データ表示用ウィンドウにQRコードを表示します\nbutton, b - 強制的にスタートボタン画面に遷移し、前回の設定時間で吐水します。\nr - 強制的に待機画面に戻します\ndata - 読み込んだcsvの内容を表示します。デバッグ用です。\nh, help, ? - このヘルプを表示します")
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
            case "g" | "gui" | "99999988":
                # GUIを表示
                gui.show_window()
            case "nogui":
                # GUIを消す
                gui.hide_window()
            case "qr":
                #qrコード表示
                    gui.mode = gui.renderUI(3)
            #case "sh":
                #System.out.println(GPIOOutput(String.valueOf(gui.waterDispensingTimeText)));
                #continue;
            case "b" | "button":
                # スタートボタン
                gui.mode = gui.renderUI(2)
                # 残り時間を前回実行時のデータから復元
                gui.remain = gui.waterDispensingTime
                #continue;
            #case "control":
                #gui.addControl();
                #continue;
            case "data":
                # 読み込んだcsvの内容を表示
                from IPython.display import display
                dataframe = pd.DataFrame(data)
                display(dataframe)
            case "speed":
                #注水速度調整
                gui.waterSpeed = int(input(f"water speed({gui.waterSpeed})>"))
            case "r":
                # 強制的に待機画面へ
                gui.mode = gui.renderUI(0)
            case _:
                # ユーザー入力された文字列に対応する商品があるか検索
                searchData(int(command))

print("bye!")
