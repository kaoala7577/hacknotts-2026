from PyQt6 import QtCore, QtGui, QtWidgets

from cv_engine import SignRecognitionEngine
from database.database import DatabaseManager
from ui.add_sign_view import AddSignView


class Ui_MainWindow:
    """Builds the main window form and its application-level view actions."""

    def setupUi(self, main_window) -> None:
        self.main_window = main_window
        self._configure_window()
        self._create_services()
        self._create_central_widget()
        self._create_menus()
        self._create_status_bar()
        self._create_toolbar()
        self._connect_actions()
        self._translate_ui()
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def _configure_window(self) -> None:
        self.main_window.setObjectName("MainWindow")
        self.main_window.resize(616, 601)

    def _create_services(self) -> None:
        self.DB = DatabaseManager()
        self.cv_engine = SignRecognitionEngine()

    def _create_central_widget(self) -> None:
        self.centralwidget = QtWidgets.QWidget(parent=self.main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.main_window.setCentralWidget(self.centralwidget)

        self._create_home_panel()

    def _create_home_panel(self) -> None:
        self.widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(0, 100, 576, 120))
        self.widget.setObjectName("widget")

        self.mainHomeWidget = QtWidgets.QVBoxLayout(self.widget)
        self.mainHomeWidget.setContentsMargins(0, 0, 0, 0)
        self.mainHomeWidget.setObjectName("mainHomeWidget")

        self._create_card_summary()
        self._create_study_button()

    def _create_card_summary(self) -> None:
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainHomeWidget.addLayout(self.horizontalLayout)

        self.verticalLayout = self._create_summary_column(
            "label",
            "label_2",
        )
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = self._create_summary_column(
            "label_3",
            "label_4",
        )
        self.horizontalLayout.addLayout(self.verticalLayout_2)

    def _create_summary_column(
        self,
        title_object_name: str,
        count_object_name: str,
    ) -> QtWidgets.QVBoxLayout:
        layout = QtWidgets.QVBoxLayout()
        layout.setObjectName(
            f"{title_object_name}_{count_object_name}_layout"
        )

        title = self._create_summary_label(title_object_name)
        count = self._create_summary_label(count_object_name)
        layout.addWidget(title)
        layout.addWidget(count)
        return layout

    def _create_summary_label(self, object_name: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(parent=self.widget)
        label.setFont(self._summary_font())
        label.setObjectName(object_name)
        setattr(self, object_name, label)
        return label

    @staticmethod
    def _summary_font() -> QtGui.QFont:
        font = QtGui.QFont()
        font.setFamily("Inter")
        font.setPointSize(20)
        return font

    def _create_study_button(self) -> None:
        self.studyNowButton = QtWidgets.QPushButton(parent=self.widget)
        self.studyNowButton.setObjectName("studyNowButton")
        self.mainHomeWidget.addWidget(self.studyNowButton)

    def _create_menus(self) -> None:
        self.menubar = QtWidgets.QMenuBar(parent=self.main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 616, 31))
        self.menubar.setObjectName("menubar")
        self.main_window.setMenuBar(self.menubar)

        self.menuFile = self._create_menu("menuFile")
        self.menuEdit = self._create_menu("menuEdit")
        self.menuView = self._create_menu("menuView")
        self.menuTools = self._create_menu("menuTools")
        self.menuHelp = self._create_menu("menuHelp")

        self._create_actions()
        self._populate_menus()

    def _create_menu(self, object_name: str) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu(parent=self.menubar)
        menu.setObjectName(object_name)
        self.menubar.addAction(menu.menuAction())
        return menu

    def _create_actions(self) -> None:
        action_names = (
            "actionImport",
            "actionExport",
            "actionExit",
            "actionToggle_Full_Screen",
            "actionZoom_In",
            "actionZoom_Out",
            "actionReset_Zoom",
            "actionPreferences",
            "actionGuide",
            "actionHome",
            "actionAdd",
            "actionBrowse",
            "actionStats",
        )

        for name in action_names:
            action = QtGui.QAction(parent=self.main_window)
            action.setObjectName(name)
            setattr(self, name, action)

        for name in ("actionHome", "actionAdd", "actionBrowse", "actionStats"):
            getattr(self, name).setMenuRole(
                QtGui.QAction.MenuRole.NoRole
            )

    def _populate_menus(self) -> None:
        self.menuFile.addActions([self.actionImport, self.actionExport])
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        self.menuView.addAction(self.actionToggle_Full_Screen)
        self.menuView.addSeparator()
        self.menuView.addActions(
            [
                self.actionZoom_In,
                self.actionZoom_Out,
                self.actionReset_Zoom,
            ]
        )
        self.menuTools.addAction(self.actionPreferences)
        self.menuHelp.addAction(self.actionGuide)

        self.toolBarActions = (
            self.actionHome,
            self.actionAdd,
            self.actionBrowse,
            self.actionStats,
        )

    def _create_status_bar(self) -> None:
        self.statusbar = QtWidgets.QStatusBar(parent=self.main_window)
        self.statusbar.setObjectName("statusbar")
        self.main_window.setStatusBar(self.statusbar)

    def _create_toolbar(self) -> None:
        self.toolBar = QtWidgets.QToolBar(parent=self.main_window)
        self.toolBar.setObjectName("toolBar")
        self.main_window.addToolBar(
            QtCore.Qt.ToolBarArea.TopToolBarArea,
            self.toolBar,
        )
        self.toolBar.addActions(list(self.toolBarActions))

    def _connect_actions(self) -> None:
        self.actionAdd.triggered.connect(self._open_add_sign_view)
        self.actionExit.triggered.connect(self.main_window.close)

    def _open_add_sign_view(self) -> None:
        self.switch_to_view(1)

    def switch_to_view(self, view_index: int) -> None:
        if view_index != 1:
            return

        sign_view = AddSignView(
            db_manager=self.DB,
            cv_engine=self.cv_engine,
        )
        self.mainHomeWidget.addWidget(sign_view)

    def _translate_ui(self) -> None:
        translate = QtCore.QCoreApplication.translate
        self.main_window.setWindowTitle(translate("MainWindow", "MainWindow"))

        labels = {
            self.label: "Text to sign cards due",
            self.label_2: "20",
            self.label_3: "Sign to text cards due",
            self.label_4: "20",
            self.studyNowButton: "Study Now!",
        }
        for widget, text in labels.items():
            widget.setText(translate("MainWindow", text))

        menu_titles = {
            self.menuFile: "File",
            self.menuEdit: "Edit",
            self.menuView: "View",
            self.menuTools: "Tools",
            self.menuHelp: "Help",
        }
        for menu, title in menu_titles.items():
            menu.setTitle(translate("MainWindow", title))

        action_titles = {
            self.actionImport: "Import",
            self.actionExport: "Export",
            self.actionExit: "Exit",
            self.actionToggle_Full_Screen: "Toggle Full Screen",
            self.actionZoom_In: "Zoom In",
            self.actionZoom_Out: "Zoom Out",
            self.actionReset_Zoom: "Reset Zoom",
            self.actionPreferences: "Preferences",
            self.actionGuide: "Guide",
            self.actionHome: "Home",
            self.actionAdd: "Add",
            self.actionBrowse: "Browse",
            self.actionStats: "Stats",
        }
        for action, title in action_titles.items():
            action.setText(translate("MainWindow", title))

        self.toolBar.setWindowTitle(translate("MainWindow", "toolBar"))
