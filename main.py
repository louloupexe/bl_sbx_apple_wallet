import sys
import os
import json
import subprocess
import signal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QMessageBox, QFrame, QFileDialog, QProgressBar, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QFont, QPixmap, QIcon, QDesktopServices
from pymobiledevice3 import usbmux
from pymobiledevice3.lockdown import create_using_usbmux

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVED_FILE_JSON = os.path.join(SCRIPT_DIR, "saved_cards.json")
LOCAL_CARD_FOLDER = os.path.join(SCRIPT_DIR, "Cards")
WORKER_SCRIPT = os.path.join(SCRIPT_DIR, "cli_worker.py")

LANGUAGES = {
    "EN": {
        "title": "WALLET MANAGER",
        "device_prefix": "Device:",
        "status_connected": "Connected",
        "status_disconnected": "Disconnected",
        "sec1_title": "1. CARD ID MANAGEMENT",
        "btn_scan": "SCAN CARD ID",
        "btn_scan_wait": "Waiting for card...",
        "ph_id": "Card ID (Hash)...",
        "ph_name": "Enter alias name...",
        "btn_save": "Save",
        "btn_del": "Del",
        "col_name": "Card Name",
        "col_id": "ID",
        "sec2_title": "2. IMAGE & PREVIEW",
        "btn_img": "Select or Drop Image",
        "lbl_no_img": "No image selected",
        "btn_run": "EXECUTE (INJECT)",
        "btn_info": "Info",
        "btn_donate": "Donate",
        "ready": "Ready",
        "msg_done": "Done!",
        "msg_success": "Success!\nPlease check your iPhone Wallet.",
        "err_no_card_folder": "Cards folder not found!",
        "err_no_connect": "Device not connected.",
        "confirm_del": "Are you sure you want to delete this?",
        "warn_risk": "WARNING: iOS version not supported (18.2-26.1). Use at your own risk!",
        "p_init": "Initializing connection...",
        "p_img": "Replacing Background...",
        "p_front": "Installing FrontFace...",
        "p_holder": "Installing PlaceHolder...",
        "p_preview": "Installing Preview...",
        "p_respring": "Respringing device...",
        "p_done": "Process Finished!",
        "info_title": "Project Info",
        "uuid_title": "BOOK DOWNLOAD REQUIRED",
        "uuid_msg": "Books UUID is missing.\n\nPlease open 'Books' app on iPhone.",
        "cred_dev": "Developer",
        "cred_log": "Wallet ID Logs Exploit",
        "cred_sbx": "bl_sbx Exploit"
    },
    "FR": {
        "title": "GESTIONNAIRE WALLET",
        "device_prefix": "Appareil :",
        "status_connected": "Connecté",
        "status_disconnected": "Déconnecté",
        "sec1_title": "1. GESTION ID DE CARTE",
        "btn_scan": "SCANNER ID CARTE",
        "btn_scan_wait": "Attente de la carte...",
        "ph_id": "ID Carte (Hash)...",
        "ph_name": "Nom de la carte...",
        "btn_save": "Sauver",
        "btn_del": "Suppr",
        "col_name": "Nom",
        "col_id": "ID",
        "sec2_title": "2. IMAGE & APPERÇU",
        "btn_img": "Choisir ou Déposer Image",
        "lbl_no_img": "Aucune image",
        "btn_run": "INJECTER (EXECUTE)",
        "btn_info": "Infos",
        "btn_donate": "Donate",
        "ready": "Prêt",
        "msg_done": "Terminé !",
        "msg_success": "Succès !\nVérifiez votre Wallet sur iPhone.",
        "err_no_card_folder": "Dossier Cards introuvable !",
        "err_no_connect": "Appareil non connecté.",
        "confirm_del": "Voulez-vous supprimer cet élément ?",
        "warn_risk": "ATTENTION : Version iOS non supportée (18.2-26.1). À vos risques et périls !",
        "p_init": "Initialisation...",
        "p_img": "Remplacement fond...",
        "p_front": "Installation FrontFace...",
        "p_holder": "Installation Placeholder...",
        "p_preview": "Installation Preview...",
        "p_respring": "Relance (Respring)...",
        "p_done": "Processus terminé !",
        "info_title": "Infos Projet",
        "uuid_title": "TÉLÉCHARGEMENT LIVRE REQUIS",
        "uuid_msg": "UUID Books manquant.\n\nOuvrez l'app 'Livres' sur iPhone.",
        "cred_dev": "Développeur",
        "cred_log": "Exploit Wallet ID Logs",
        "cred_sbx": "Exploit bl_sbx"
    },
    "VN": {
        "title": "QUẢN LÝ VÍ WALLET",
        "device_prefix": "Thiết bị:",
        "status_connected": "Đã kết nối",
        "status_disconnected": "Mất kết nối",
        "sec1_title": "1. QUẢN LÝ ID THẺ",
        "btn_scan": "BẮT ĐẦU DÒ TÌM ID",
        "btn_scan_wait": "Đang đợi thẻ...",
        "ph_id": "ID Thẻ (Dạng hash)...",
        "ph_name": "Đặt tên gợi nhớ...",
        "btn_save": "Lưu",
        "btn_del": "Xóa",
        "col_name": "Tên Thẻ",
        "col_id": "ID",
        "sec2_title": "2. HÌNH ẢNH & PREVIEW",
        "btn_img": "Chọn Ảnh Nền",
        "lbl_no_img": "Chưa chọn ảnh",
        "btn_run": "THỰC THI (INJECT)",
        "btn_info": "Thông tin",
        "btn_donate": "Donate",
        "ready": "Sẵn sàng",
        "msg_done": "Hoàn tất!",
        "msg_success": "Đã thay thế thẻ thành công!\nKiểm tra lại Wallet trên iPhone.",
        "err_no_card_folder": "Không tìm thấy thư mục Cards!",
        "err_no_connect": "Chưa kết nối thiết bị.",
        "confirm_del": "Bạn có chắc muốn xóa thẻ này?",
        "warn_risk": "CẢNH BÁO: Phiên bản iOS không hỗ trợ (18.2-26.1). Tự chịu rủi ro!",
        "p_init": "Đang khởi tạo kết nối...",
        "p_img": "Đang thay thế Ảnh nền...",
        "p_front": "Đang cài đặt Mặt trước...",
        "p_holder": "Đang cài đặt Giữ chỗ...",
        "p_preview": "Đang cài đặt Xem trước...",
        "p_respring": "Đang khởi động lại (Respring)...",
        "p_done": "Xử lý hoàn tất!",
        "info_title": "Thông tin dự án",
        "uuid_title": "YÊU CẦU TẢI SÁCH",
        "uuid_msg": "Tool chưa tìm thấy UUID của ứng dụng Sách.\n\nVui lòng mở iPhone, vào ứng dụng 'Sách'.",
        "cred_dev": "Nhà Phát Triển",
        "cred_log": "Khai Thác Logs ID Wallet",
        "cred_sbx": "Khai Thác bl_sbx"
    },
    "CN": {
        "title": "钱包卡片管理",
        "device_prefix": "设备:",
        "status_connected": "已连接",
        "status_disconnected": "未连接",
        "sec1_title": "1. 卡片 ID 管理",
        "btn_scan": "扫描 ID",
        "btn_scan_wait": "等待卡片...",
        "ph_id": "卡片 ID (哈希)...",
        "ph_name": "输入备注名称...",
        "btn_save": "保存",
        "btn_del": "删除",
        "col_name": "名称",
        "col_id": "ID",
        "sec2_title": "2. 图片 & 预览",
        "btn_img": "选择图片",
        "lbl_no_img": "未选择图片",
        "btn_run": "执行 (注入)",
        "btn_info": "信息",
        "btn_donate": "捐赠",
        "ready": "准备就绪",
        "msg_done": "完成!",
        "msg_success": "成功!\n请检查 iPhone 钱包。",
        "err_no_card_folder": "未找到 Cards 文件夹!",
        "err_no_connect": "设备未连接。",
        "confirm_del": "确定要删除吗？",
        "warn_risk": "警告：iOS 版本不受支持 (18.2-26.1)。风险自担！",
        "p_init": "正在初始化...",
        "p_img": "正在替换背景...",
        "p_front": "正在安装正面...",
        "p_holder": "正在安装占位符...",
        "p_preview": "正在安装预览...",
        "p_respring": "正在注销 (Respring)...",
        "p_done": "处理完成!",
        "info_title": "项目信息",
        "uuid_title": "需要下载书籍",
        "uuid_msg": "未找到 Books UUID。\n\n请在 iPhone 上打开“图书”应用。",
        "cred_dev": "开发者",
        "cred_log": "Wallet ID 日志漏洞",
        "cred_sbx": "bl_sbx 漏洞"
    },
    "KR": {
        "title": "월렛 관리자",
        "device_prefix": "장치:",
        "status_connected": "연결됨",
        "status_disconnected": "연결 끊김",
        "sec1_title": "1. 카드 ID 관리",
        "btn_scan": "카드 ID 스캔",
        "btn_scan_wait": "카드 대기 중...",
        "ph_id": "카드 ID (해시)...",
        "ph_name": "별칭 입력...",
        "btn_save": "저장",
        "btn_del": "삭제",
        "col_name": "카드 이름",
        "col_id": "ID",
        "sec2_title": "2. 이미지 및 미리보기",
        "btn_img": "이미지 선택 또는 드래그",
        "lbl_no_img": "선택된 이미지 없음",
        "btn_run": "실행 (주입)",
        "btn_info": "정보",
        "btn_donate": "기부",
        "ready": "준비 완료",
        "msg_done": "완료!",
        "msg_success": "성공!\niPhone 월렛을 확인하세요.",
        "err_no_card_folder": "Cards 폴더를 찾을 수 없습니다!",
        "err_no_connect": "장치가 연결되지 않았습니다.",
        "confirm_del": "정말 삭제하시겠습니까?",
        "warn_risk": "경고: 지원되지 않는 iOS 버전입니다 (18.2-26.1). 본인 책임하에 진행하십시오!",
        "p_init": "연결 초기화 중...",
        "p_img": "배경 교체 중...",
        "p_front": "FrontFace 설치 중...",
        "p_holder": "PlaceHolder 설치 중...",
        "p_preview": "미리보기 설치 중...",
        "p_respring": "리스프링 중 (Respring)...",
        "p_done": "프로세스 완료!",
        "info_title": "프로젝트 정보",
        "uuid_title": "도서 다운로드 필요",
        "uuid_msg": "Books UUID가 없습니다.\n\niPhone에서 '도서' 앱을 열어주세요.",
        "cred_dev": "개발자",
        "cred_log": "Wallet ID 로그 익스플로잇",
        "cred_sbx": "bl_sbx 익스플로잇"
    }
}

class InjectorProcess(QThread):
    progress_signal = pyqtSignal(str, int)
    error_signal = pyqtSignal(str)
    uuid_missing_signal = pyqtSignal()
    finished_signal = pyqtSignal()

    def __init__(self, udid, card_id, img_path, lang_code):
        super().__init__()
        self.udid = udid
        self.card_id = card_id
        self.img_path = img_path
        self.lang = LANGUAGES[lang_code]

    def run(self):
        cmd = [sys.executable, WORKER_SCRIPT, f"--udid={self.udid}", f"--card_id={self.card_id}", f"--image={self.img_path}"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            line = line.strip()
            if "GUI:UUID_MISSING" in line:
                self.uuid_missing_signal.emit()
                continue
            msg, pct = "", 0
            if "Starting Process" in line: msg = self.lang["p_init"]; pct = 10
            elif "cardBackgroundCombined" in line: msg = self.lang["p_img"]; pct = 25
            elif "FrontFace" in line: msg = self.lang["p_front"]; pct = 45
            elif "PlaceHolder" in line: msg = self.lang["p_holder"]; pct = 65
            elif "Preview" in line: msg = self.lang["p_preview"]; pct = 85
            elif "Respringing" in line: msg = self.lang["p_respring"]; pct = 95
            elif "All tasks finished" in line: msg = self.lang["p_done"]; pct = 100
            if msg: self.progress_signal.emit(msg, pct)
            if "[Err]" in line or "Error" in line: self.error_signal.emit(line)
        process.wait()
        self.finished_signal.emit()

class ScanWorker(QThread):
    found_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.running = True
    def run(self):
        try:
            from pymobiledevice3.services.os_trace import OsTraceService
            lockdown = create_using_usbmux()
            for entry in OsTraceService(lockdown=lockdown).syslog():
                if not self.running: break
                msg = entry.message
                if '/var/mobile/Library/Passes/Cards/' in msg:
                    parts = msg.split('/var/mobile/Library/Passes/Cards/')
                    if len(parts) > 1:
                        seg = parts[1].split()[0].rstrip('.,;:)"\'')
                        if '.pkpass' in seg:
                            self.found_signal.emit(seg.split('.pkpass')[0])
                            break
        except: pass
    def stop(self): self.running = False

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iOS Wallet Manager Pro")
        self.setGeometry(100, 100, 750, 600)
        self.setAcceptDrops(True)
        self.user_image_path, self.udid, self.current_lang = "", "", "EN"
        self.init_ui()
        self.apply_dark_theme()
        self.load_saved_data()
        self.retranslate_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(2000)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            path = files[0]
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.user_image_path = path
                self.lbl_img_path.setText(os.path.basename(path))
                self.lbl_preview.setPixmap(QPixmap(path).scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.check_ready()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        top_frame = QFrame(); top_frame.setObjectName("HeaderFrame")
        top_layout = QHBoxLayout(top_frame)
        self.lbl_title = QLabel("WALLET CUSTOMIZER"); self.lbl_title.setObjectName("AppTitle")
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["English", "Français", "Tiếng Việt", "中文", "한국어"])
        self.combo_lang.setFixedWidth(100); self.combo_lang.currentIndexChanged.connect(self.change_language)
        self.lbl_status = QLabel("Disconnected"); self.lbl_dev_name = QLabel("--")
        info_layout = QVBoxLayout(); info_layout.addWidget(self.lbl_status); info_layout.addWidget(self.lbl_dev_name)
        top_layout.addWidget(self.lbl_title); top_layout.addWidget(self.combo_lang); top_layout.addStretch(); top_layout.addLayout(info_layout)
        main_layout.addWidget(top_frame)
        content_layout = QHBoxLayout()
        left_frame = QFrame(); left_frame.setObjectName("Card"); left_layout = QVBoxLayout(left_frame)
        self.lbl_sec1 = QLabel("1. CARD ID MANAGEMENT"); self.lbl_sec1.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec1)
        self.btn_scan = QPushButton("SCAN CARD ID"); self.btn_scan.setObjectName("BtnPrimary")
        self.btn_scan.setEnabled(False); self.btn_scan.clicked.connect(self.toggle_scan)
        left_layout.addWidget(self.btn_scan)
        self.txt_id = QLineEdit(); left_layout.addWidget(self.txt_id)
        mgmt_layout = QHBoxLayout()
        self.txt_name = QLineEdit(); self.btn_save = QPushButton("Save"); self.btn_save.setObjectName("BtnSave")
        self.btn_save.setFixedWidth(60); self.btn_save.clicked.connect(self.save_card)
        self.btn_del = QPushButton("Del"); self.btn_del.setObjectName("BtnDelete")
        self.btn_del.setFixedWidth(60); self.btn_del.clicked.connect(self.delete_card)
        mgmt_layout.addWidget(self.txt_name); mgmt_layout.addWidget(self.btn_save); mgmt_layout.addWidget(self.btn_del)
        left_layout.addLayout(mgmt_layout)
        self.table = QTableWidget(0, 2)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionsClickable(False)
        self.table.horizontalHeader().setSectionsMovable(False)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellClicked.connect(self.on_table_click)
        left_layout.addWidget(self.table)
        right_frame = QFrame(); right_frame.setObjectName("Card"); right_layout = QVBoxLayout(right_frame)
        self.lbl_sec2 = QLabel("2. IMAGE & PREVIEW"); self.lbl_sec2.setObjectName("SectionTitle")
        right_layout.addWidget(self.lbl_sec2)
        self.btn_img = QPushButton("Select Image"); self.btn_img.setObjectName("BtnSecondary")
        self.btn_img.clicked.connect(self.choose_image)
        right_layout.addWidget(self.btn_img)
        self.lbl_preview = QLabel("Preview"); self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lbl_preview.setMinimumSize(250, 150)
        self.lbl_preview.setStyleSheet("border: 2px dashed #444; border-radius: 8px; background-color: #222;")
        right_layout.addWidget(self.lbl_preview)
        self.lbl_img_path = QLabel(""); self.lbl_img_path.setStyleSheet("color: gray; font-size: 10px;")
        right_layout.addWidget(self.lbl_img_path)
        content_layout.addWidget(left_frame, 55); content_layout.addWidget(right_frame, 45)
        main_layout.addLayout(content_layout)
        bottom_frame = QFrame(); bottom_frame.setObjectName("Card"); bottom_layout = QVBoxLayout(bottom_frame)
        self.btn_run = QPushButton("EXECUTE"); self.btn_run.setObjectName("BtnSuccess")
        self.btn_run.setFixedHeight(50); self.btn_run.setEnabled(False); self.btn_run.clicked.connect(self.start_process)
        self.lbl_process_status = QLabel(""); self.progress = QProgressBar()
        bottom_layout.addWidget(self.btn_run); bottom_layout.addWidget(self.lbl_process_status); bottom_layout.addWidget(self.progress)
        main_layout.addWidget(bottom_frame)
        footer_layout = QHBoxLayout(); self.btn_info = QPushButton("Info"); self.btn_donate = QPushButton("Donate")
        footer_layout.addStretch(); footer_layout.addWidget(self.btn_info); footer_layout.addWidget(self.btn_donate)
        main_layout.addLayout(footer_layout)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #E0E0E0; font-family: 'Helvetica Neue', sans-serif; }
            #HeaderFrame { background-color: #1E1E1E; border-bottom: 1px solid #333; }
            #AppTitle { font-size: 20px; font-weight: bold; color: white; }
            #Card { background-color: #1E1E1E; border-radius: 10px; border: 1px solid #333; }
            QLineEdit { background-color: #2C2C2E; border: 1px solid #3A3A3C; color: white; padding: 5px; }
            QPushButton { font-weight: bold; padding: 5px; border-radius: 5px; }
            #BtnPrimary { background-color: #0A84FF; color: white; border: none; }
            #BtnSecondary { background-color: #3A3A3C; color: white; border: 1px solid #555; }
            #BtnSuccess { background-color: #30D158; color: white; border: none; }
            #BtnSave { background-color: #FF9F0A; color: black; border: none; }
            #BtnDelete { background-color: #FF453A; color: white; border: none; }
            QTableWidget { background-color: #121212; color: white; gridline-color: #333; border: 1px solid #333; }
            QHeaderView::section { background-color: #2C2C2E; color: white; border: none; padding: 5px; font-weight: bold; }
            QComboBox { background-color: #2C2C2E; color: white; border: 1px solid #3A3A3C; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2C2C2E; color: white; selection-background-color: #0A84FF; }
        """)

    def change_language(self, index):
        order = ["EN", "FR", "VN", "CN", "KR"]
        self.current_lang = order[index]; self.retranslate_ui()

    def retranslate_ui(self):
        t = LANGUAGES[self.current_lang]
        self.lbl_title.setText(t["title"]); self.lbl_sec1.setText(t["sec1_title"]); self.lbl_sec2.setText(t["sec2_title"])
        self.btn_scan.setText(t["btn_scan"]); self.btn_save.setText(t["btn_save"]); self.btn_del.setText(t["btn_del"])
        self.btn_img.setText(t["btn_img"]); self.btn_run.setText(t["btn_run"]); self.btn_info.setText(t["btn_info"])
        self.btn_donate.setText(t["btn_donate"]); self.table.setHorizontalHeaderLabels([t["col_name"], t["col_id"]])

    def check_connection(self):
        t = LANGUAGES[self.current_lang]
        try:
            lockdown = create_using_usbmux()
            ver = lockdown.get_value(key="ProductVersion")
            self.lbl_status.setText(t["status_connected"]); self.lbl_status.setStyleSheet("color: #30D158;")
            self.lbl_dev_name.setText(f"{lockdown.get_value(key='DeviceName')} | iOS {ver}")
            self.udid = lockdown.udid; self.btn_scan.setEnabled(True)
            if self.user_image_path and self.txt_id.text(): self.btn_run.setEnabled(True)
        except:
            self.lbl_status.setText(t["status_disconnected"]); self.lbl_status.setStyleSheet("color: #FF453A;")
            self.btn_scan.setEnabled(False); self.btn_run.setEnabled(False)

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.user_image_path = path; self.lbl_img_path.setText(os.path.basename(path))
            self.lbl_preview.setPixmap(QPixmap(path).scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.check_ready()

    def check_ready(self):
        if self.txt_id.text() and self.user_image_path: self.btn_run.setEnabled(True)

    def save_card(self):
        n, c = self.txt_name.text(), self.txt_id.text()
        if not n or not c: return
        data = {}
        if os.path.exists(SAVED_FILE_JSON):
            with open(SAVED_FILE_JSON, 'r') as f: data = json.load(f)
        data[n] = c
        with open(SAVED_FILE_JSON, 'w') as f: json.dump(data, f, indent=4)
        self.load_saved_data()

    def delete_card(self):
        r = self.table.currentRow()
        if r < 0: return
        n = self.table.item(r, 0).text()
        with open(SAVED_FILE_JSON, 'r') as f: data = json.load(f)
        if n in data: del data[n]
        with open(SAVED_FILE_JSON, 'w') as f: json.dump(data, f, indent=4)
        self.load_saved_data()

    def load_saved_data(self):
        if not os.path.exists(SAVED_FILE_JSON): return
        with open(SAVED_FILE_JSON, 'r') as f:
            data = json.load(f); self.table.setRowCount(len(data))
            for i, (k, v) in enumerate(data.items()):
                self.table.setItem(i, 0, QTableWidgetItem(k)); self.table.setItem(i, 1, QTableWidgetItem(v))

    def on_table_click(self, r, c): self.txt_id.setText(self.table.item(r, 1).text()); self.check_ready()

    def toggle_scan(self):
        self.sw = ScanWorker(); self.sw.found_signal.connect(self.on_id_found); self.sw.start()

    def on_id_found(self, cid): self.txt_id.setText(cid); self.check_ready()

    def start_process(self):
        t = LANGUAGES[self.current_lang]
        try:
            lockdown = create_using_usbmux()
            v_parts = [int(x) for x in lockdown.get_value(key="ProductVersion").split('.')]
            if not (18.2 <= float(f"{v_parts[0]}.{v_parts[1]}") <= 26.1):
                if QMessageBox.warning(self, "Warning", t["warn_risk"], QMessageBox.Yes | QMessageBox.No) == QMessageBox.No: return
        except: pass
        self.btn_run.setEnabled(False)
        self.worker = InjectorProcess(self.udid, self.txt_id.text(), self.user_image_path, self.current_lang)
        self.worker.progress_signal.connect(lambda m, v: (self.lbl_process_status.setText(m), self.progress.setValue(v)))
        self.worker.finished_signal.connect(lambda: (self.btn_run.setEnabled(True), QMessageBox.information(self, "OK", t["msg_success"])))
        self.worker.start()

if __name__ == "__main__":
    if os.geteuid() != 0: os.execvp('sudo', ['sudo', sys.executable] + sys.argv)
    app = QApplication(sys.argv); app.setStyle("Fusion")
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    w = AppWindow(); w.show(); sys.exit(app.exec_())