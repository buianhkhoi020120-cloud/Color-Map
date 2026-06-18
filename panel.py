import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QSlider, QLabel, QListWidget, QGraphicsView, QGraphicsScene, 
                             QFrame, QGraphicsDropShadowEffect, QListWidgetItem, QButtonGroup)
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPolygonF

from algorithms.backtracking import solve_backtracking
from algorithms.forward_checking import solve_forward_checking

COLORS_MAP = {"Đỏ": "#ff7675", "Xanh": "#55efc4", "Xanh dương": "#74b9ff", "Vàng": "#ffeaa7", "Tím": "#a29bfe"}

HCMC_POLYGONS = {
    "Củ Chi": [(0, 0), (120, 0), (150, 80), (80, 120), (0, 80)],
    "Hóc Môn": [(80, 120), (150, 80), (180, 140), (120, 180)],
    "Q12": [(150, 80), (220, 80), (250, 130), (180, 140)],
    "Gò Vấp": [(180, 140), (250, 130), (260, 160), (210, 170)],
    "Bình Thạnh": [(250, 130), (300, 140), (310, 190), (260, 190), (260, 160)],
    "Thủ Đức": [(220, 80), (380, 80), (400, 180), (310, 190), (300, 140), (250, 130)],
    "Phú Nhuận": [(210, 170), (260, 160), (260, 190), (230, 190)],
    "Tân Bình": [(180, 140), (210, 170), (230, 190), (200, 220), (160, 190)],
    "Tân Phú": [(120, 180), (180, 140), (160, 190), (130, 220)],
    "Bình Tân": [(80, 230), (120, 180), (130, 220), (150, 280), (90, 300)],
    "Q11": [(160, 190), (200, 220), (190, 240), (150, 230)],
    "Q10": [(200, 220), (230, 190), (240, 220), (210, 240)],
    "Q3": [(230, 190), (260, 190), (270, 220), (240, 220)],
    "Q1": [(260, 190), (310, 190), (300, 240), (270, 220)],
    "Q6": [(130, 220), (150, 230), (180, 260), (150, 280)],
    "Q5": [(150, 230), (190, 240), (210, 240), (220, 260), (180, 260)],
    "Q4": [(240, 220), (270, 220), (300, 240), (280, 260), (240, 250)],
    "Q8": [(150, 280), (180, 260), (220, 260), (240, 250), (280, 260), (260, 300), (160, 310)],
    "Q7": [(280, 260), (300, 240), (360, 260), (340, 320), (260, 300)],
    "Bình Chánh": [(0, 150), (80, 120), (120, 180), (80, 230), (90, 300), (160, 310), (260, 300), (240, 350), (150, 380), (0, 300)],
    "Nhà Bè": [(260, 300), (340, 320), (360, 260), (400, 300), (350, 400), (240, 350)],
    "Cần Giờ": [(350, 400), (400, 300), (500, 350), (550, 500), (400, 550)]
}

HCMC_EDGES = [
    ("Củ Chi", "Hóc Môn"), ("Củ Chi", "Bình Chánh"), ("Củ Chi", "Q12"),
    ("Hóc Môn", "Q12"), ("Hóc Môn", "Bình Chánh"), ("Hóc Môn", "Tân Bình"), ("Hóc Môn", "Tân Phú"), ("Hóc Môn", "Gò Vấp"),
    ("Q12", "Gò Vấp"), ("Q12", "Bình Thạnh"), ("Q12", "Thủ Đức"), ("Q12", "Tân Bình"),
    ("Gò Vấp", "Bình Thạnh"), ("Gò Vấp", "Phú Nhuận"), ("Gò Vấp", "Tân Bình"),
    ("Bình Thạnh", "Thủ Đức"), ("Bình Thạnh", "Phú Nhuận"), ("Bình Thạnh", "Q1"),
    ("Thủ Đức", "Q1"), 
    ("Phú Nhuận", "Q1"), ("Phú Nhuận", "Q3"), ("Phú Nhuận", "Tân Bình"),
    ("Tân Bình", "Q3"), ("Tân Bình", "Q10"), ("Tân Bình", "Q11"), ("Tân Bình", "Tân Phú"),
    ("Tân Phú", "Bình Tân"), ("Tân Phú", "Q6"), ("Tân Phú", "Q11"),
    ("Bình Tân", "Bình Chánh"), ("Bình Tân", "Q6"), ("Bình Tân", "Q8"),
    ("Q11", "Q10"), ("Q11", "Q5"), ("Q11", "Q6"),
    ("Q10", "Q3"), ("Q10", "Q5"),
    ("Q3", "Q1"), 
    ("Q1", "Q4"), ("Q1", "Q5"),
    ("Q5", "Q6"), ("Q5", "Q8"), ("Q5", "Q4"),
    ("Q6", "Q8"), 
    ("Q4", "Q8"), ("Q4", "Q7"),
    ("Q8", "Bình Chánh"), ("Q8", "Q7"), ("Q8", "Nhà Bè"),
    ("Bình Chánh", "Nhà Bè"),
    ("Q7", "Nhà Bè"),
    ("Nhà Bè", "Cần Giờ")
]

class PanelSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSP Algorithm - HCMC Modern Map Simulator")
        self.setGeometry(50, 50, 1450, 800)
        
        self.setStyleSheet("QMainWindow { background-color: #f0f2f5; }")
        
        self.nodes = list(HCMC_POLYGONS.keys())
        self.adj = {n: [] for n in self.nodes}
        for u, v in HCMC_EDGES:
            self.adj[u].append(v)
            self.adj[v].append(u)
            
        self.algo_generator = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        
        self.init_ui()

    def create_card_frame(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 15px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        frame.setGraphicsEffect(shadow)
        return frame

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # ================= PANEL TRÁI (CONTROLS) =================
        left_frame = self.create_card_frame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 25, 20, 25)
        left_layout.setSpacing(15)

        title_lbl1 = QLabel("⚙️ BẢNG ĐIỀU KHIỂN")
        title_lbl1.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: bold; color: #2c3e50;")
        left_layout.addWidget(title_lbl1)
        
        algo_lbl = QLabel("📌 Chọn thuật toán:")
        algo_lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; color: #636e72; margin-top: 10px;")
        left_layout.addWidget(algo_lbl)

        # ---- GIAO DIỆN CHỌN THUẬT TOÁN (SELECTABLE CARDS) ----
        self.algo_btn_bt = QPushButton("Backtracking")
        self.algo_btn_fc = QPushButton("Backtracking + FC")
        
        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.algo_btn_bt)
        self.btn_group.addButton(self.algo_btn_fc)
        self.btn_group.buttonClicked.connect(self.reset_sim)

        for btn in [self.algo_btn_bt, self.algo_btn_fc]:
            btn.setCheckable(True)
            btn.setFixedHeight(55)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 2px solid #dfe6e9;
                    border-radius: 10px;
                    text-align: left;
                    padding-left: 15px;
                    color: #636e72;
                    font-weight: bold;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #f1f2f6;
                    border: 2px solid #b2bec3;
                }
                QPushButton:checked {
                    background-color: #e8f4fd;
                    border: 2px solid #0984e3;
                    color: #0984e3;
                }
            """)
            left_layout.addWidget(btn)
        
        # Mặc định chọn thuật toán đầu tiên
        self.algo_btn_bt.setChecked(True)
        # --------------------------------------------------------

        left_layout.addSpacing(15)
        
        # Nhóm Nút Bấm Thực Thi
        self.btn_start = QPushButton("▶ Bắt Đầu / Tiếp Tục")
        self.btn_pause = QPushButton("⏸ Tạm Dừng")
        self.btn_reset = QPushButton("↺ Chạy Lại (Reset)")
        
        btn_styles = {
            self.btn_start: ("#00b894", "#55efc4"),
            self.btn_pause: ("#f39c12", "#f1c40f"),
            self.btn_reset: ("#d63031", "#ff7675")
        }
        for btn, (bg, hover) in btn_styles.items():
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg}; color: white; font-weight: bold; 
                    font-size: 14px; font-family: 'Segoe UI'; border-radius: 8px;
                }}
                QPushButton:hover {{ background-color: {hover}; }}
            """)
        
        self.btn_start.clicked.connect(self.start_sim)
        self.btn_pause.clicked.connect(self.timer.stop)
        self.btn_reset.clicked.connect(self.reset_sim)
        
        left_layout.addWidget(self.btn_start)
        left_layout.addWidget(self.btn_pause)
        left_layout.addWidget(self.btn_reset)
        
        speed_lbl = QLabel("⚡ Tốc độ mô phỏng:")
        speed_lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; color: #2c3e50; margin-top: 15px;")
        
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(1, 20)
        self.fps_slider.setValue(8)
        self.fps_slider.setCursor(Qt.PointingHandCursor)
        self.fps_slider.setStyleSheet("""
            QSlider::groove:horizontal { border-radius: 4px; height: 8px; background: #dfe6e9; }
            QSlider::handle:horizontal { background: #0984e3; width: 18px; height: 18px; margin: -5px 0; border-radius: 9px; }
        """)

        left_layout.addWidget(speed_lbl)
        left_layout.addWidget(self.fps_slider)
        left_layout.addStretch()

        # ================= PANEL GIỮA (CANVAS) =================
        center_frame = self.create_card_frame()
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(15, 15, 15, 15)

        title_lbl2 = QLabel("🗺️ BẢN ĐỒ TP. HỒ CHÍ MINH")
        title_lbl2.setStyleSheet("font-family: 'Segoe UI'; font-size: 18px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;")
        
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setStyleSheet("border: none; background-color: transparent;")
        
        center_layout.addWidget(title_lbl2)
        center_layout.addWidget(self.view)

        # ================= PANEL PHẢI (LOG) =================
        right_frame = self.create_card_frame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        title_lbl3 = QLabel("📝 NHẬT KÝ THUẬT TOÁN")
        title_lbl3.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;")
        
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                background-color: #2d3436; 
                color: #dfe6e9; 
                font-family: 'Consolas', 'Courier New', monospace; 
                font-size: 13px; 
                border-radius: 8px; 
                padding: 10px;
                border: none;
            }
            QListWidget::item { padding: 5px 0; border-bottom: 1px solid #353b48; }
            QListWidget::item:selected { background-color: transparent; color: inherit; }
        """)
        
        right_layout.addWidget(title_lbl3)
        right_layout.addWidget(self.log_list)

        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(center_frame, 5)
        main_layout.addWidget(right_frame, 3)

        self.draw_graph({})

    def log(self, text, type="normal"):
        item = QListWidgetItem(text)
        if type == "error":
            item.setForeground(QColor("#ff7675"))
        elif type == "success":
            item.setForeground(QColor("#55efc4"))
        elif type == "highlight":
            item.setForeground(QColor("#ffeaa7"))
            
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

    def draw_graph(self, assignment, highlight_node=None, testing_color_name=None):
        self.scene.clear()
        
        SCALE = 1.6
        OFFSET_X, OFFSET_Y = 50, 50 
        
        for node, points in HCMC_POLYGONS.items():
            poly = QPolygonF([QPointF(x * SCALE + OFFSET_X, y * SCALE + OFFSET_Y) for x, y in points])
            poly_item = self.scene.addPolygon(poly)
            
            if node in assignment:
                poly_item.setBrush(QBrush(QColor(COLORS_MAP[assignment[node]])))
            elif node == highlight_node and testing_color_name:
                poly_item.setBrush(QBrush(QColor(COLORS_MAP[testing_color_name])))
                poly_item.setPen(QPen(Qt.red, 3, Qt.DashLine))
            else:
                poly_item.setBrush(QBrush(QColor("#f1f2f6")))
                
            if node == highlight_node and not testing_color_name:
                poly_item.setPen(QPen(QColor("#0984e3"), 3))
            elif node not in assignment and node != highlight_node:
                poly_item.setPen(QPen(QColor("#b2bec3"), 1.5))
                
            cx = sum([p[0] for p in points]) / len(points) * SCALE + OFFSET_X
            cy = sum([p[1] for p in points]) / len(points) * SCALE + OFFSET_Y
            
            txt = self.scene.addText(node, QFont("Segoe UI", 8, QFont.Bold))
            txt.setDefaultTextColor(QColor("#2d3436"))
            rect = txt.boundingRect()
            txt.setPos(cx - rect.width()/2, cy - rect.height()/2)

    def start_sim(self):
        if not self.algo_generator:
            # Đọc xem nút thẻ nào đang được check
            if self.algo_btn_bt.isChecked():
                algo_func = solve_backtracking 
            else:
                algo_func = solve_forward_checking
                
            self.algo_generator = algo_func(self.nodes, self.adj, list(COLORS_MAP.keys()))
            self.log_list.clear()
            
        self.timer.start(1000 // self.fps_slider.value())

    def reset_sim(self):
        self.timer.stop()
        self.algo_generator = None
        self.log_list.clear()
        self.draw_graph({})

    def next_step(self):
        try:
            step = next(self.algo_generator)
            
            if "log" in step:
                for line in step["log"].split("\n"):
                    if "ko hợp lệ" in line or "Lỗi" in line or "Quay lui" in line:
                        self.log("🔴 " + line, "error")
                    elif "hợp lệ" in line:
                        self.log("🟢 " + line, "success")
                    elif "Chọn biến" in line or "Bước" in line:
                        self.log("⭐ " + line, "highlight")
                    else:
                        self.log(line)
            
            action = step.get("action")
            node = step.get("node")
            color = step.get("color")
            assignment = step.get("assignment", {})
            
            if action in ["init", "select_var", "valid", "backtrack", "fc_wipeout", "fc_update", "done"]:
                self.draw_graph(assignment, highlight_node=node)
            elif action == "try_color" or action == "invalid":
                self.draw_graph(assignment, highlight_node=node, testing_color_name=color)
                
            if action == "done":
                self.log("\n🎉 ĐÃ TÌM THẤY LỜI GIẢI ĐÚNG CHO BẢN ĐỒ!", "success")
                self.timer.stop()
                
        except StopIteration:
            self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = PanelSimulator()
    window.show()
    sys.exit(app.exec_())