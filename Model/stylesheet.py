STYLE_QGROUPBOX = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    border: 2px solid rgba(0, 0, 0, 255);
    margin-top: 1px;
    padding-top: $PADDING_TOP;
    padding-bottom: 2px;
    padding-left: 5px;
    padding-right: 5px;
    font-size: 8pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: rgba(255, 255, 255, 180);
    padding: 0px;
    left:-4px;
}
'''


STYLE_QCOMBOBOX = '''
QComboBox {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 4px;
    padding-right: 4px;
}
QComboBox:hover {
    border: 1px solid rgba(255, 255, 255, 80);
}
QComboBox:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(10, 10, 10, 80);
}
QComboBox:!editable,
QComboBox::drop-down:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(80, 80, 80, 80);
}
/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on,
QComboBox::drop-down:editable:on {
    background: rgba(150, 150, 150, 150);
}
QComboBox::drop-down {
    background: rgba(80, 80, 80, 80);
    border-left: 1px solid rgba(80, 80, 80, 255);
    width: 20px;
}
QComboBox::down-arrow {
    image: url("Resources/down_arrow.png");
}
QComboBox::down-arrow:on {
    /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}'''

STYLE_QLISTVIEW = '''
QListView {
    background: rgba(80, 80, 80, 255);
    border: 0px solid rgba(0, 0, 0, 0);
}
QListView::item {
    color: rgba(255, 255, 255, 120);
    background: rgba(60, 60, 60, 255);
    border-bottom: 1px solid rgba(0, 0, 0, 0);
    border-radius: 0px;
    margin: 0px;
    padding: 2px;
}
QListView::item:selected {
    color: rgba(98, 68, 10, 255);
    background: rgba(219, 158, 0, 255);
    border-bottom: 1px solid rgba(255, 255, 255, 5);
    border-radius: 0px;
    margin:0px;
    padding: 2px;
}
'''

STYLE_QCHECKBOX = '''
QCheckBox {
    color: rgba(255, 255, 255, 255);
    background-color: transparent;
    font-size: 8px;
    spacing: 0px 0px;
    padding-top: 0px;
    padding-bottom: 0px;
    height: 8px;
}
QCheckBox::indicator {
    width: 12px;
    height: 12px;
}
'''

STYLE_QTEXTEDIT = '''
QTextEdit {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 5px;
    color: rgba(255, 255, 255, 150);
    background: rgba(0, 0, 0, 80);
    selection-background-color: rgba(255, 198, 10, 155);
}
'''

STYLE_QMENU = '''
QMenu {
    background-color: rgba(153, 230, 255, 128); /* sets background of the menu */
    border: 1px solid black;
}
QMenu::item {
    background-color: transparent;
}
QMenu::item:selected {
    background-color: rgba(0, 115, 153, 255);
}
'''