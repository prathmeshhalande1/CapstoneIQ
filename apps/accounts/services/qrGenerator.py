import qrcode
import io
import base64

def generate_group_qr(request,group_code):

    protocol = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    joinUrl = f"{protocol}://{host}/accounts/join/{group_code}/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(joinUrl)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qrBase64 = base64.b64encode(buffer.getvalue()).decode()

    return qrBase64, joinUrl