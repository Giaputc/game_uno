import pgzrun
from settings import WIDTH, HEIGHT, TITLE
from Controller.app_manager import AppManager

# Khai báo biến app ở cấp độ toàn cục
app = None

def draw():
    global app
    # PGZero sẽ tự truyền 'screen' vào hàm draw này khi chạy
    if app is None:
        # Khởi tạo AppManager và truyền screen vào
        app = AppManager(screen) 
    
    app.draw()

def update(dt):
    if app:
        app.update()

def on_mouse_down(pos):
    if app:
        app.handle_mouse_down(pos)

# Bắt đầu chạy game
pgzrun.go()