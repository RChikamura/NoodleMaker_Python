import os
from NoodleCSV import NoodleCSV as ncsv
from NoodleUI import NoodleInterface as nui

# パスの取得
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir,"cupData.csv")

# このプログラムを直接実行したとき
if __name__ == "__main__":
    noodle_csv  = ncsv(csv_path)
    noodleUI = nui(current_dir, noodle_csv)
