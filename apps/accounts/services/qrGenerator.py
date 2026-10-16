import qrcode
import io
import base64

def generate_group_qr(request,group_code):

    hostPort = request.get_host()
    scheme=request.scheme

    join_url = f"{scheme}://{hostPort}/accounts/join/{group_code}"
    
    img = qrcode.make(join_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{qr_base64}"