from PySide2.QtWidgets import QMenuBar


def create_menus(self):
    """Define menus and menu items."""
    self.menu_bar = QMenuBar(self)
    self.menu_bar.setGeometry(0, 0, 225, 25)
    # self.menu_bar.setStyleSheet(SS.get_style('menu'))

    for catg in ["File", "Edit", "Window", "Help"]:
        self.menu_file = self.menu_bar.addMenu(catg)
        for key, obj in self.tool_actions[catg].items():
            self.menu_file.addAction(self.tool_actions[catg][key]["w"])
        self.menu_bar.addMenu(self.menu_file)
