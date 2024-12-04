import io
import qrcode
from PIL import Image, ImageTk

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
