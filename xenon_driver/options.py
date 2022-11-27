class Options:

    STEADY = 0x18
    NEON = 0x14
    BREATH = 0x22
    OFF = 0x11

    DEFAULT = 0x00

    REPORT_RATE_1000MHZ = 0x40
    REPORT_RATE_500MHZ = 0x30
    REPORT_RATE_250MHZ = 0x20

    NORMAL_DIRECTION = 0x00
    INVERSE_DIRECTION = 0x03

    MODE1 = 0x01
    MODE2 = 0x02
    MODE3 = 0x03

    BLOCKED_DPI_LEVEL_MASK = 0x80

    # ---------- BUTTONS BINDINGS ------------

    CLICK_MASK = 0x10
    FIRE_MASK = 0x20
    LEFT_BUTTON = 0xf0
    RIGHT_BUTTON = 0xf1
    MIDDLE_BUTTON = 0xf2
    BACK_BUTTON = 0xf3
    FORWARD_BUTTON = 0xf4

    # ------------------
    MODE_MASK = 0x50
    MODE_ACTION = 0x06

    # ------------------
    DPI_LOOP_MASK = 0x40
    DPI_LOOP = 0x00
    DPI_PLUS = 0x20
    DPI_MINUS = 0x40

    # ------------------
    THREE_CLICK_MASK = 0x30
    THREE_CLICK_ACTION = 0x01 # ? - must be checked

    # ------------------
    # doesn't work
    # MULTIMEDIA_MASK = 0x70
    # MEDIAPLAYER = 0x00
    # PLAYPAUSE = 0x08
    # NEXT = 0x01
    # PREVIOUS = 0x02
    # STOP = 0x04
    # MUTE = 0x10
    # VOLUMEUP = 0x40
    # VOLUMEDOWN = 0x80
    # EMAIL = 0x00 # ? - same as MEDIAPLAYER
    # CALCULATOR = 0x00 # ?
    # EXPLORER = 0x00 # ?
    # HOMEPAGE = 0x00 # ?

    # ------------------
    SNIPE_BUTTON_MASK = 0x40
    SNIPE_DPI500 = 0x81
    SNIPE_DPI750 = 0x82
    SNIPE_DPI1000 = 0x83
    SNIPE_DPI1250 = 0x84
    SNIPE_DPI1375 = 0x85
    SNIPE_DPI1500 = 0x86
    SNIPE_DPI1750 = 0x87
    SNIPE_DPI2000 = 0x88
    SNIPE_DPI2500 = 0x89
    SNIPE_DPI2750 = 0x8a
    SNIPE_DPI3200 = 0x8b

    # ------------------
    DISABLE_MASK = 0x50
    DISABLE_ACTION = 0x01

    # ------------------
    KEY_COMBINATION_MASK = 0x60

    # ----------- keys ------------

    # first byte after KEY_COMBINATION_MASK
    LCTRL = 0x01
    LSHIFT = 0x02
    LALT = 0x04
    WIN = 0x08

    RSHIFT = 0x20
    RCTRL = 0x10
    RALT = 0x40

    # second and third byte after KEY_COMBINATION_MASK
    KEY_A = 0x04
    KEY_B = 0x05
    KEY_C = 0x06
    KEY_D = 0x07
    KEY_E = 0x08
    KEY_F = 0x09
    KEY_G = 0x0a
    KEY_H = 0x0b
    KEY_I = 0x0c
    KEY_J = 0x0d
    KEY_K = 0x0e
    KEY_L = 0x0f
    KEY_M = 0x10
    KEY_N = 0x11
    KEY_O = 0x12
    KEY_P = 0x13
    KEY_Q = 0x14
    KEY_R = 0x15
    KEY_S = 0x16
    KEY_T = 0x17
    KEY_U = 0x18
    KEY_V = 0x19
    KEY_W = 0x1a
    KEY_X = 0x1b
    KEY_Y = 0x1c
    KEY_Z = 0x1d

    KEY_1 = 0x1e
    KEY_2 = 0x1f
    KEY_3 = 0x20
    KEY_4 = 0x21
    KEY_5 = 0x22
    KEY_6 = 0x23
    KEY_7 = 0x24
    KEY_8 = 0x25
    KEY_9 = 0x26
    KEY_0 = 0x27

    KEY_BACKSPACE = 0x28
    KEY_ESCAPE = 0x29
    KEY_ENTER = 0x2a
    KEY_TAB = 0x2b
    KEY_SPACE = 0x2c
    KEY_MINUS = 0x2d
    KEY_EQUAL = 0x2e
    KEY_LBRACKET = 0x2f
    KEY_RBRACKET = 0x30
    KEY_BACKSLASH = 0x31

    KEY_SEMICOLON = 0x33
    KEY_QUOTE = 0x34
    KEY_TILDA = 0x35
    KEY_COMMA = 0x36
    KEY_DOT = 0x37
    KEY_SLASH = 0x38
    KEY_CAPSLOCK = 0x39

    KEY_F1 = 0x3a
    KEY_F2 = 0x3b
    KEY_F3 = 0x3c
    KEY_F4 = 0x3d
    KEY_F5 = 0x3e
    KEY_F6 = 0x3f
    KEY_F7 = 0x40
    KEY_F8 = 0x41
    KEY_F9 = 0x42
    KEY_F10 = 0x43
    KEY_F11 = 0x44
    KEY_F12 = 0x45

    KEY_PAUSE = 0x48

    KEY_INSERT = 0x4c

    KEY_RIGHT = 0x4f
    KEY_LEFT = 0x50
    KEY_DOWN = 0x51
    KEY_UP = 0x52
    KEY_NUMLOCK = 0x53
    KEY_NUMSLASH = 0x54
    KEY_NUMSTAR = 0x55
    KEY_NUMMINUS = 0x56
    KEY_NUMPLUS = 0x57
    KEY_DELETE = 0x58
    KEY_NUM1 = 0x59
    KEY_NUM2 = 0x5a
    KEY_NUM3 = 0x5b
    KEY_NUM4 = 0x5c
    KEY_NUM5 = 0x5d
    KEY_NUM6 = 0x5e
    KEY_NUM7 = 0x5f
    KEY_NUM8 = 0x60
    KEY_NUM9 = 0x61
    KEY_NUM0 = 0x62
    KEY_NUMDOT = 0x63

    KEY_APP = 0x65

    # my mutlimedia keys
    MEDIAPLAYER = 0x99
    PLAYPAUSE = 0xa0
    NEXT = 0xa1
    PREVIOUS = 0xa2
    STOP = 0xa3
    MUTE = 0xa4
    VOLUMEUP = 0xa5
    VOLUMEDOWN = 0xa6
    EMAIL = 0xa7
    CALCULATOR = 0xa8
    EXPLORER = 0xa9
    HOMEPAGE = 0xaa

    # macros
    MACRO_MASK = 0x90
    MACRO_DELAY_LOOP = 0x03
