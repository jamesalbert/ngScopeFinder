class font:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def funcName(s):
        return '%s%s%s' % (font.BOLD,s,font.END)

    @staticmethod
    def fileName(s):
        return '%s%s%s%s%s' % (font.UNDERLINE,font.BOLD,font.GREEN,s,font.END)

    @staticmethod
    def lineNumber(s):
        return '%s%s%s%s' % (font.BOLD,font.CYAN,s,font.END)

    @staticmethod
    def badName(s):
        return '%s%s%s%s' % (font.BOLD,font.RED,s,font.END)

    @staticmethod
    def underline(s):
        return '%s%s%s%s' % (font.UNDERLINE,font.YELLOW,s,font.END)
