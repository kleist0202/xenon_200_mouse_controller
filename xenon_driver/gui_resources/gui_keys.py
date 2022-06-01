from PyQt5.QtCore import Qt
from xenon_driver.options import Options


class GuiKeys:
    keys_dict = {
            Qt.Key_A : ["A", Options.KEY_A],
            Qt.Key_B : ["B", Options.KEY_B],
            Qt.Key_C : ["C", Options.KEY_C],
            Qt.Key_D : ["D", Options.KEY_D],
            Qt.Key_E : ["E", Options.KEY_E],
            Qt.Key_F : ["F", Options.KEY_F],
            Qt.Key_G : ["G", Options.KEY_G],
            Qt.Key_H : ["H", Options.KEY_H],
            Qt.Key_I : ["I", Options.KEY_I],
            Qt.Key_J : ["J", Options.KEY_J],
            Qt.Key_K : ["K", Options.KEY_K],
            Qt.Key_L : ["L", Options.KEY_L],
            Qt.Key_M : ["M", Options.KEY_M],
            Qt.Key_N : ["N", Options.KEY_N],
            Qt.Key_O : ["O", Options.KEY_O],
            Qt.Key_P : ["P", Options.KEY_P],
            Qt.Key_Q : ["Q", Options.KEY_Q],
            Qt.Key_R : ["R", Options.KEY_R],
            Qt.Key_S : ["S", Options.KEY_S],
            Qt.Key_T : ["T", Options.KEY_T],
            Qt.Key_U : ["U", Options.KEY_U],
            Qt.Key_V : ["V", Options.KEY_V],
            Qt.Key_W : ["W", Options.KEY_W],
            Qt.Key_X : ["X", Options.KEY_X],
            Qt.Key_Y : ["Y", Options.KEY_Y],
            Qt.Key_Z : ["Z", Options.KEY_Z],
            Qt.Key_1 : ["1", Options.KEY_1],
            Qt.Key_2 : ["2", Options.KEY_2],
            Qt.Key_3 : ["3", Options.KEY_3],
            Qt.Key_4 : ["4", Options.KEY_4],
            Qt.Key_5 : ["5", Options.KEY_5],
            Qt.Key_6 : ["6", Options.KEY_6],
            Qt.Key_7 : ["7", Options.KEY_7],
            Qt.Key_8 : ["8", Options.KEY_8],
            Qt.Key_9 : ["9", Options.KEY_9],
            Qt.Key_Control : ["Ctrl", Options.LCTRL],
            Qt.Key_Shift   : ["Shift", Options.LSHIFT],
            Qt.Key_Alt     : ["Alt", Options.LALT],
            Qt.Key_Super_L : ["Super", Options.WIN]
    }

    MOUSE_KEYS = {
        "Left button" : Options.LEFT_BUTTON,
        "Right button" : Options.RIGHT_BUTTON,
        "Middle button" : Options.MIDDLE_BUTTON
    }
