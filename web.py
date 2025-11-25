import eventlet #支援非同步與協程的函式庫，可以讓 Flask-SocketIO 以非同步（async）模式處理多重連線。
eventlet.monkey_patch()  # 必須在其他模組之前調用，是一種在程式執行前去修改（或替換）一些 Python 標準函式庫行為的技巧，用來讓標準庫能支援協程或非同步 I/O。
from flask import Flask, render_template #從 Flask 框架中匯入建立應用的 Flask 類別，以及渲染 HTML 模板的 render_template 函式。
from flask_socketio import SocketIO, emit #在 Flask 中整合 Socket.io 的主要類別，讓 Flask 可以處理 WebSocket 通訊。
import json #Python 內建的 JSON 解析套件，方便序列化與反序列化 JSON 格式資料
from sql import connect_to_db, create_db, drop_and_create_table
#從自訂的 sql.py 模組匯入資料庫連線與操作的函式
#connect_to_db()：用來跟資料庫建立連線。
#create_db()：用來建立資料庫。
#drop_and_create_table()：刪除後重建資料表，確保結構一致或清空表格內容。


app = Flask(__name__, template_folder='/home/allen/404',static_folder='/home/allen/404')  # 靜態資源設定
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')  # 允許跨域

# 初始化資料庫
create_db() #呼叫自訂函式，若沒有資料庫，就建立一個。
drop_and_create_table() #刪除並重新建立所需的資料表，於確保表的結構符合需求

# 儲存座標到資料庫
def save(x, y, delta_x, delta_y, direction): #負責將滑鼠座標和方向等資料，插入到 Coordinates 資料表中。
    try:
        db = connect_to_db()  # 每次操作都建立新的連線
        cursor = db.cursor() #從連線拿到 cursor（游標），用來執行 SQL。
        query = "INSERT INTO Coordinates (x, y, delta_x, delta_y, direction) VALUES (%s, %s, %s, %s, %s)" #要執行的 SQL 語句，插入一筆 (x, y, delta_x, delta_y, direction)。
        print(f"Executing query: {query} with values: {x}, {y}, {delta_x}, {delta_y}, {direction}")
        cursor.execute(query, (x, y, delta_x, delta_y, direction)) #使用參數化執行 SQL，避免 SQL injection。
        db.commit()  # 提交資料
    except Exception as e:
        print(f"資料庫操作發生錯誤: {e}")
    finally:
        if db:
            db.close()  # 確保連線在操作完成後關閉

@app.route('/') #設定 Flask 的路由：當使用者瀏覽 http://<伺服器IP>:<port>/ 時，就會觸發 index() 函式。
def index(): #直接回傳渲染後的 index.html。此檔案應位於 template_folder 指定的 /home/allen/404 路徑裡。
    return render_template('index.html')

# 監聽 WebSocket 連線 (Socket.IO)
@socketio.on('connect', namespace='/ws')
def handle_ws_connect():
    print("WebSocket 連接成功 (路徑 /ws)")
    socketio.emit('message', {"status": "connected"}, namespace='/ws')  # 回傳連接狀態


# 監聽前端傳來的座標資訊
@socketio.on('message', namespace='/ws') #監聽名為 message 的事件。前端若使用 socket.emit('message', someData, {namespace:'/ws'})，就會到達這個函式。
def handle_ws_message(data): #data 是前端發送的 JSON 資料，通常包含滑鼠座標、方向等資訊。
    print(f"接收到滑鼠座標資料: {data}")

    try:
        # 確保資料是有效的
        x = data.get('x')
        y = data.get('y')
        delta_x = data.get('deltaX')
        delta_y = data.get('deltaY')
        direction = data.get('direction')

        if None in [x, y, delta_x, delta_y, direction]:
            raise ValueError("缺少必要的座標或方向資料")

        # 儲存資料
        save(x, y, delta_x, delta_y, direction)

        # 回應前端
        socketio.emit("message", {"status": "success", "received_data": data}, namespace='/ws')

    except ValueError as ve: #資料本身格式或內容有問題 → 回傳 {"status": "error", "message": ...}
        print(f"資料驗證錯誤: {ve}")
        socketio.emit("message", {"status": "error", "message": str(ve)}, namespace='/ws')
    except Exception as e: #資料解析或資料庫操作失敗 → 回傳「內部伺服器錯誤」。
        print(f"資料解析或存儲錯誤: {e}")
        socketio.emit("message", {"status": "error", "message": "內部伺服器錯誤"}, namespace='/ws')

# 監聽 WebSocket 斷線
@socketio.on('disconnect', namespace='/ws') #當前端與此命名空間 /ws 的連線中斷時，就會呼叫 handle_ws_disconnect()。
def handle_ws_disconnect():
    print("WebSocket 連接已斷開 (路徑 /ws)") #在伺服器端 console 印出斷線訊息，用於紀錄連線狀態。

if __name__ == '__main__': #只有在直接執行 web.py 時，才會進入這個區塊。若是被其他程式 import，則不會執行這裡的程式碼。
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
#啟動 SocketIO + Flask 伺服器，並設定：
#host='0.0.0.0'：允許任何網卡 IP 連線（包括區網或本機）。
#port=8080：使用 8080 埠對外提供服務。
#debug=True：開啟 Flask 除錯模式，能自動重啟並在 console 顯示詳細錯誤資訊。