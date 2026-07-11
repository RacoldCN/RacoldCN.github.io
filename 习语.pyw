import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextBrowser, QVBoxLayout, 
                             QWidget, QSystemTrayIcon, QMenu, QAction, QStyle, QLabel)
from PyQt5.QtCore import QTimer, Qt, QDate, QRect
from PyQt5.QtGui import QIcon, QDesktopServices, QMouseEvent, QFont, QTextCursor
import re
import datetime
import webbrowser

class DailyXiYuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.article_content = {"title": "", "body": "", "url": ""}
        self.last_fetch_date = None  # 记录上次获取的日期
        self.initUI()
        # 启动时立即尝试获取一次内容
        self.fetch_daily_xiyu()
        # 设置定时器，每1小时检查一次（3600000毫秒）
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_daily_xiyu)
        self.timer.start(3600000)

    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle('每日习语')
        # 移除了置顶属性，只保留无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 获取屏幕尺寸并计算右上角位置
        screen_geometry = QApplication.desktop().screenGeometry()
        window_width = 500
        window_height = 400
        x = screen_geometry.width() - window_width - 20  # 距离右边20像素
        y = 50  # 距离顶部50像素
        
        self.setGeometry(x, y, window_width, window_height)

        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建标题区域（可点击）
        self.titleLabel = QLabel()
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                padding: 5px;
                color: #0066cc;
            }
            QLabel:hover {
                text-decoration: underline;
                cursor: pointer;
            }
        """)
        self.titleLabel.mousePressEvent = self.title_clicked
        layout.addWidget(self.titleLabel)
        
        # 添加分隔线
        line = QLabel()
        line.setFrameShape(QLabel.HLine)
        line.setStyleSheet("background-color: #cccccc;")
        line.setFixedHeight(1)
        layout.addWidget(line)
        
        # 使用QTextBrowser显示正文
        self.textBrowser = QTextBrowser()
        self.textBrowser.setReadOnly(True)
        # 设置字体为楷体，增大字号
        font = QFont("楷体", 12)  # 使用楷体，字号12
        self.textBrowser.setFont(font)
        # 禁用QTextBrowser内部的链接处理
        self.textBrowser.setOpenLinks(False)
        layout.addWidget(self.textBrowser)
        
        # 添加更新时间标签
        self.timeLabel = QLabel()
        self.timeLabel.setStyleSheet("color: #888888; font-size: 10px;")
        self.timeLabel.setAlignment(Qt.AlignRight)
        layout.addWidget(self.timeLabel)

        # 创建系统托盘图标
        self.createTrayIcon()

    def title_clicked(self, event):
        """标题被点击时在浏览器中打开文章"""
        if self.article_content['url']:
            webbrowser.open(self.article_content['url'])

    def createTrayIcon(self):
        """创建系统托盘图标和菜单"""
        self.trayIcon = QSystemTrayIcon(self)
        # 使用系统自带的图标
        self.trayIcon.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))

        # 创建托盘菜单
        trayMenu = QMenu()
        # 显示/隐藏窗口动作
        showAction = QAction("显示/隐藏", self, triggered=self.toggle_window)
        trayMenu.addAction(showAction)
        # 手动更新动作
        updateAction = QAction("立即更新", self, triggered=self.fetch_daily_xiyu)
        trayMenu.addAction(updateAction)
        # 移动到右上角动作
        moveAction = QAction("移动到右上角", self, triggered=self.move_to_top_right)
        trayMenu.addAction(moveAction)
        # 退出程序动作
        quitAction = QAction("退出", self, triggered=QApplication.quit)
        trayMenu.addAction(quitAction)

        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()
        # 点击托盘图标也可以显示/隐藏窗口
        self.trayIcon.activated.connect(self.on_tray_icon_activated)

    def move_to_top_right(self):
        """将窗口移动到桌面右上角"""
        screen_geometry = QApplication.desktop().screenGeometry()
        window_width = self.width()
        x = screen_geometry.width() - window_width - 20  # 距离右边20像素
        y = 50  # 距离顶部50像素
        self.move(x, y)

    def toggle_window(self):
        """切换窗口的显示和隐藏状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def on_tray_icon_activated(self, reason):
        """处理托盘图标被激活的信号"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_window()

    def fetch_daily_xiyu(self):
        """抓取每日习语内容 - 精确获取习语栏目"""
        # 直接访问习语栏目页
        column_url = "https://www.peopleweekly.cn/html/zt/xiyu/index.html"
        print(f"正在从习语栏目页抓取: {column_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(column_url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取当前日期
            today = datetime.datetime.now().strftime("%Y%m%d")
            
            # 如果今天已经获取过内容，并且不是手动更新，则跳过
            if self.last_fetch_date == today and not hasattr(self, 'manual_update'):
                print(f"今天已经获取过内容，跳过 ({today})")
                return
                
            # 精确查找习语文章链接
            article_link = None
            
            # 方法1: 查找所有包含"xiyu"的链接
            all_links = soup.find_all('a', href=re.compile(r'.*xiyu.*\.html'))
            
            # 优先查找包含今天日期的链接
            for link in all_links:
                href = link.get('href')
                if href and today in href:
                    article_link = href
                    print(f"通过日期匹配找到文章链接: {article_link}")
                    break
            
            # 方法2: 如果没有找到今天日期的链接，取第一个包含"xiyu"的链接
            if not article_link and all_links:
                article_link = all_links[0].get('href')
                print(f"日期匹配失败，选取首个习语链接: {article_link}")
            
            # 确保链接是绝对路径
            if article_link and not article_link.startswith('http'):
                if article_link.startswith('/'):
                    article_link = "https://www.peopleweekly.cn" + article_link
                else:
                    article_link = "https://www.peopleweekly.cn/" + article_link.lstrip('./')
            
            if not article_link:
                self.titleLabel.setText("无法找到习语文章链接")
                self.textBrowser.setPlainText("")
                return
                
            print(f"最终文章链接: {article_link}")
            
            # 抓取文章内容
            article_response = requests.get(article_link, headers=headers, timeout=10)
            article_response.encoding = 'utf-8'
            
            if article_response.status_code != 200:
                self.titleLabel.setText("无法访问文章页面")
                self.textBrowser.setPlainText(f"HTTP状态码: {article_response.status_code}")
                return
                
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # 提取标题
            title_selectors = ['h1', '.article-title', '.title', '.content-title', 'header h1']
            title = "今日习语"
            
            for selector in title_selectors:
                title_tag = article_soup.select_one(selector)
                if title_tag:
                    title_text = title_tag.get_text().strip()
                    if title_text:
                        title = title_text
                        break
            
            # 提取正文
            body_selectors = ['.article-content', '.content', 'article', '.text', '.article-body', '.content-body']
            body = None
            
            for selector in body_selectors:
                body_tag = article_soup.select_one(selector)
                if body_tag:
                    # 清理无关标签
                    for element in body_tag(["script", "style", "div", "span", "a"]):
                        element.decompose()
                    
                    # 获取文本内容
                    body_text = body_tag.get_text(separator='\n', strip=True)
                    # 简化多余的空行
                    body_text = re.sub(r'\n\s*\n', '\n\n', body_text)
                    
                    if body_text and len(body_text) > 50:  # 确保有足够的内容
                        body = body_text
                        break
            
            if not body:
                # 如果以上选择器都没找到，尝试提取所有段落
                paragraphs = article_soup.find_all('p')
                body_text = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                if body_text and len(body_text) > 50:
                    body = body_text
            
            if title and body:
                self.article_content = {
                    'title': title,
                    'body': body,
                    'url': article_link
                }
                # 更新最后获取日期
                self.last_fetch_date = today
                # 重置手动更新标志
                if hasattr(self, 'manual_update'):
                    delattr(self, 'manual_update')
            else:
                self.article_content = {
                    'title': title or "今日习语",
                    'body': body or "正在等待今日内容更新，或网页结构暂未识别。",
                    'url': article_link
                }

            # 更新显示
            self.display_article()

        except Exception as e:
            self.titleLabel.setText("获取内容时出错")
            self.textBrowser.setPlainText(f"错误: {str(e)}\n\n请检查网络连接或稍后重试。")
            print(f"错误详情: {str(e)}")

    def display_article(self):
        """在窗口中显示抓取到的文章"""
        # 设置标题
        self.titleLabel.setText(self.article_content['title'])
        
        # 设置正文
        self.textBrowser.setPlainText(self.article_content['body'])
        
        # 设置更新时间
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.timeLabel.setText(f"更新时间: {current_time}")

    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标点击事件，用于实现拖动无边框窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """处理鼠标移动事件，实现窗口拖动"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

    def closeEvent(self, event):
        """重写关闭事件，使其最小化到系统托盘而不是退出程序"""
        event.ignore()
        self.hide()
        self.trayIcon.showMessage(
            "每日习语",
            "程序已最小化到托盘，它将自动为您获取最新内容。",
            QSystemTrayIcon.Information,
            2000
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = DailyXiYuWindow()
    window.show()

    sys.exit(app.exec_())
