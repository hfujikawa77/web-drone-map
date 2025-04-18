from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import socket
from pymavlink import mavutil
import threading

# Flask アプリケーションの初期化
app = Flask(__name__, static_folder="public")
socketio = SocketIO(app)

# HTTP サーバーの設定
HTTP_PORT = 3000

# MAVLink UDP ポート
UDP_PORT = 14551
UDP_HOST = "0.0.0.0"

# グローバルな状態
global_run = True


# 静的ファイルの配信
@app.route("/")
def serve_index():
    return send_from_directory("public", "index.html")


@app.route("/<path:filename>")
def serve_static_files(filename):
    # public フォルダ内のファイルを提供
    return send_from_directory("public", filename)


# WebSocket 接続イベント
@socketio.on("connect")
def handle_connect():
    print("Web client connected.")
    socketio.emit("status", {"message": "Connected to server."})


@socketio.on("disconnect")
def handle_disconnect():
    print("Web client disconnected.")


# UDP メッセージ受信スレッド
def udp_listener():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_HOST, UDP_PORT))
    print(f"[UDP Server] Listening on {UDP_HOST}:{UDP_PORT}")

    mavlink = mavutil.mavlink.MAVLink(None)  # MAVLink インスタンスを作成
    mavlink.robust_parsing = True  # エラーに強いパースモード

    while global_run:
        try:
            msg, addr = udp_socket.recvfrom(1024)
            # MAVLink メッセージのパース
            mav_message = mavlink.parse_char(msg)

            if mav_message:
                # `GLOBAL_POSITION_INT` メッセージを処理
                if mav_message.get_type() == "GLOBAL_POSITION_INT":
                    position_data = {
                        "lat": mav_message.lat / 1e7,  # 緯度を度に変換
                        "lon": mav_message.lon / 1e7,  # 経度を度に変換
                        "alt": mav_message.alt / 1000,  # 高度をメートルに変換
                        "speed": (
                            mav_message.vx**2 + mav_message.vy**2 + mav_message.vz**2
                        )
                        ** 0.5
                        / 100,  # 速度を m/s に変換
                        "heading": mav_message.hdg / 100,  # 方角を度に変換
                    }
                    print("Global Position:", position_data)

                    # WebSocketクライアントに送信
                    socketio.emit("position", position_data)

                if mav_message.get_type() == "ATTITUDE":
                    attitude_data = {
                        "roll": mav_message.roll * 180 / 3.14159,  # ラジアンを度に変換
                        "pitch": mav_message.pitch * 180 / 3.14159,
                        "yaw": mav_message.yaw * 180 / 3.14159,
                    }
                    print("Attitude:", attitude_data)

                    # WebSocketクライアントに送信
                    socketio.emit("attitude", attitude_data)

        except Exception as e:
            print(f"[UDP Server Error] {e}")


# メイン関数
if __name__ == "__main__":
    # UDPリスナースレッドの開始
    udp_thread = threading.Thread(target=udp_listener, daemon=True)
    udp_thread.start()

    # Flask サーバーの開始
    print(f"[HTTP Server] Listening on http://localhost:{HTTP_PORT}")
    socketio.run(app, port=HTTP_PORT, host="0.0.0.0")
