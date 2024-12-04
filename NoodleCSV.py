import pandas as pd

class NoodleCSV:
    def __init__(self, csv_path):
        # csvデータを格納しておく変数
        self.data = None
        self.csv_path = csv_path
        # インスタンスを初期化する際に、getCSVも実行しておく
        self.getCSV(self.csv_path)

    # csvファイルを読み込むか、新規作成する関数
    def getCSV(self, csv_path):
        # csvファイルが存在するか確認
        try:
            # pandasでcsvファイルを読み込む
            self.data = pd.read_csv(csv_path)
        except: # csvの読み込みに失敗した場合
            print('CSVの読み込みに失敗しました。cupData.csvが正しく配置されているか確認してください')



    # csvから商品を探し、情報を取得する関数
    def searchData(self, jan):
        if self.data is None:
            print("データが読み込まれていません。まずCSVファイルを読み込んでください。")
            return

        # キーを含む行をフィルタリング
        matching_rows = self.data[self.data['jan'] == jan]

        if not matching_rows.empty:
            # ヒットした最初の行の残り3つの列の値を取得
            amount = matching_rows.iloc[0]['water']
            time = matching_rows.iloc[0]['time']
            genre = matching_rows.iloc[0]['category']

            # NoodleContentViewに各種データを受け渡し
            return [jan, amount, time, genre]
        else:
            # もらってきたjanが無かった場合
            # GUI側にダミーの"N/A"を渡してあげる
            return ["N/A","N/A","N/A","N/A"]
