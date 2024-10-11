import os
import json
import shutil
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QListWidget, QPushButton, QFileDialog,
                             QMenuBar, QMessageBox, QInputDialog, QLabel,
                             QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from file_operations import get_subdirectories

class FileManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_path = ""
        self.last_left_path = ""
        self.presets = self.load_presets()  # 确保在init_ui之前加载预设
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("剑网3改键工具 by咕涌")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(self.get_style_sheet())
        self.set_icon()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.setup_menu_bar()
        self.setup_main_layout()

    def set_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anymm-x2yaz-001.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon file not found: {icon_path}")

    def setup_main_layout(self):
        main_layout = QHBoxLayout()
        self.layout.addLayout(main_layout)
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(self.create_panel("源账号", is_source=True), 4)
        main_layout.addWidget(self.create_vertical_line())
        main_layout.addWidget(self.create_panel("目标账号", is_source=False), 4)
        main_layout.addWidget(self.create_vertical_line())
        main_layout.addWidget(self.create_preset_panel(), 2)

        main_layout.setSpacing(5)

    def create_panel(self, title, is_source):
        group_box = QGroupBox(title)
        layout = QVBoxLayout(group_box)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 25, 15, 15)

        combos = []
        for label_text in ["账号", "大区", "区服", "角色"]:
            combo = self.create_combo(label_text)
            combos.append(combo)
            layout.addWidget(combo)

        layout.addStretch(1)

        button = QPushButton("保存预设" if is_source else "点击改键")
        button.setFixedHeight(40)
        button.setStyleSheet("font-size: 14px; font-weight: bold;")
        button.clicked.connect(self.save_preset if is_source else self.change_key)
        layout.addWidget(button)

        if is_source:
            self.source_combos = combos
        else:
            self.target_combos = combos

        return group_box

    def create_combo(self, label_text):
        layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333;")
        layout.addWidget(label)

        combo = QComboBox()
        combo.setStyleSheet("font-size: 13px; padding: 5px;")
        combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combo.setFixedHeight(35)
        layout.addWidget(combo)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def create_preset_panel(self):
        group_box = QGroupBox("预设配置")
        layout = QVBoxLayout(group_box)
        layout.setSpacing(5)

        self.preset_list = QListWidget()
        self.preset_list.itemClicked.connect(self.load_preset)
        layout.addWidget(self.preset_list)

        self.update_preset_list()
        return group_box

    def create_vertical_line(self):
        from PyQt5.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def get_style_sheet(self):
        return """
        QMainWindow {
            background-color: #F0F0F0;
        }
        QGroupBox {
            font-size: 16px;
            font-weight: bold;
            border: 2px solid #0078D7;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 16px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            color: #0078D7;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
            font-weight: bold;
            margin-bottom: 3px;
        }
        QComboBox {
            background-color: white;
            border: 1px solid #AAAAAA;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 13px;
            min-height: 30px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: #AAAAAA;
            border-left-style: solid;
        }
        QPushButton {
            background-color: #0078D7;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 15px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005A9E;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #AAAAAA;
            border-radius: 4px;
            font-size: 13px;
            padding: 5px;
        }
        """

    def load_data(self):
        self.load_last_path()

        if not self.base_path:
            self.first_time_setup()
        else:
            self.update_source_combos()
            self.update_target_combos()

    def first_time_setup(self):
        reply = QMessageBox.question(self, '首次设置', 
                                     "欢迎使用jx3改键小工具！是否现在选择游戏数据文件夹？文件夹路径确保设置到userdata路径下",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.select_base_folder()
        else:
            QMessageBox.information(self, '提示', 
                                    "您可以稍后通过菜单栏的'选择游戏数据文件夹'选项来设置。")

    def select_base_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择游戏数据文件夹")
        if folder:
            self.base_path = folder
            self.save_last_path()
            self.update_source_combos()
            self.update_target_combos()

    def update_source_combos(self):
        if hasattr(self, 'source_combos'):
            self.update_combos(self.base_path, self.source_combos)
            if self.last_left_path:
                self.set_path_in_combos(self.source_combos, self.last_left_path)

    def update_target_combos(self):
        if hasattr(self, 'target_combos'):
            self.update_combos(self.base_path, self.target_combos)

    def update_combos(self, path, combos):
        if not path:
            return
        
        for combo_widget in combos:
            combo = combo_widget.findChild(QComboBox)
            if combo:
                combo.clear()
        self.populate_combo(path, combos, 0)

    def populate_combo(self, path, combos, level):
        if level >= len(combos):
            return
        
        if not os.path.exists(path):
            print(f"路径不存在: {path}")
            return

        try:
            subdirs = get_subdirectories(path)
            if subdirs:
                combo = combos[level].findChild(QComboBox)
                combo.clear()
                combo.addItems(subdirs)
                
                try:
                    combo.currentIndexChanged.disconnect()
                except TypeError:
                    pass
                combo.currentIndexChanged.connect(lambda: self.on_combo_changed(self.base_path, combos, level))
                
                if level < len(combos) - 1 and combo.currentText():
                    next_path = os.path.join(path, combo.currentText())
                    self.populate_combo(next_path, combos, level + 1)
        except Exception as e:
            print(f"在填充下拉框时发生错误: {e}")

    def on_combo_changed(self, base_path, combos, level):
        if level >= len(combos) - 1:
            return
        
        selected_path = base_path
        for i in range(level + 1):
            combo = combos[i].findChild(QComboBox)
            if combo.currentText():
                selected_path = os.path.join(selected_path, combo.currentText())
            else:
                break

        # 清空当前级别之后的所有下拉框
        for combo in combos[level+1:]:
            combo.findChild(QComboBox).clear()
        
        # 更新下一级
        if os.path.exists(selected_path):
            self.populate_combo(selected_path, combos, level + 1)
        else:
            print(f"路径不存在: {selected_path}")

        if combos == self.source_combos:
            self.save_last_path()  # 保存左侧路径的变化

    def save_preset(self):
        name, ok = QInputDialog.getText(self, '保存预设', '请输入预设名称:')
        if ok and name:
            current_selections = self.get_current_selections()
            self.presets[name] = current_selections
            self.save_presets()
            self.update_preset_list()

    def change_key(self):
        source_path = self.get_selected_path(self.source_combos)
        target_path = self.get_selected_path(self.target_combos)

        if not source_path or not target_path:
            QMessageBox.warning(self, "警告", "请确保源路径和目标路径都已选择")
            return

        try:
            # 删除原目标路径的内容，但保留文件夹
            if os.path.exists(target_path):
                for item in os.listdir(target_path):
                    item_path = os.path.join(target_path, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            else:
                os.makedirs(target_path)  # 如果目标路径不存在，创建它
            
            # 复制源路径的内容到目标路径
            for item in os.listdir(source_path):
                s = os.path.join(source_path, item)
                d = os.path.join(target_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            
            QMessageBox.information(self, "成功", "改键操作完成")
            
            # 更新目标面板
            self.update_target_combos()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"改键操作失败: {str(e)}")

    def get_current_selections(self):
        selections = [self.base_path]
        for combo in self.source_combos:
            combo_widget = combo.findChild(QComboBox)
            selections.append(combo_widget.currentText())
        return selections

    def get_selected_path(self, combos):
        path = self.base_path
        for combo in combos:
            combo_widget = combo.findChild(QComboBox)
            if combo_widget.currentText():
                path = os.path.join(path, combo_widget.currentText())
            else:
                break
        return path

    def save_presets(self):
        with open('presets.json', 'w') as f:
            json.dump(self.presets, f)

    def update_preset_list(self):
        self.preset_list.clear()
        for name in self.presets:
            self.preset_list.addItem(name)

    def load_preset(self, item):
        preset_name = item.text()
        if preset_name in self.presets:
            selections = self.presets[preset_name]
            self.base_path = selections[0]
            self.update_source_combos()
            self.set_combo_selections(self.source_combos, selections[1:])

    def set_combo_selections(self, combos, selections):
        for combo, selection in zip(combos, selections):
            combo_widget = combo.findChild(QComboBox)
            index = combo_widget.findText(selection)
            if index >= 0:
                combo_widget.setCurrentIndex(index)
                self.on_combo_changed(self.base_path, combos, combos.index(combo))
            else:
                break

    def load_presets(self):
        try:
            with open('presets.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_last_path(self):
        with open('last_path.json', 'w') as f:
            json.dump({
                'base_path': self.base_path,
                'last_left_path': self.get_selected_path(self.source_combos)
            }, f)

    def load_last_path(self):
        try:
            with open('last_path.json', 'r') as f:
                data = json.load(f)
                self.base_path = data.get('base_path', '')
                self.last_left_path = data.get('last_left_path', self.base_path)
        except FileNotFoundError:
            self.base_path = ''
            self.last_left_path = ''

    def set_path_in_combos(self, combos, path):
        if not path.startswith(self.base_path):
            return
        relative_path = os.path.relpath(path, self.base_path)
        parts = relative_path.split(os.sep)
        for i, part in enumerate(parts):
            if i < len(combos):
                combo_widget = combos[i].findChild(QComboBox)
                index = combo_widget.findText(part)
                if index >= 0:
                    combo_widget.setCurrentIndex(index)
                    self.on_combo_changed(self.base_path, combos, i)
                else:
                    break

    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("设置")
        
        select_base = file_menu.addAction("选择游戏数据文件夹")
        select_base.triggered.connect(self.select_base_folder)