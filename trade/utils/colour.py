class ColourTxtUtil:
    @staticmethod
    def red(txt: str):
        return "\033[1;31m{}\033[0m".format(txt)

    @staticmethod
    def green(txt: str):
        return "\033[1;32m{}\033[0m".format(txt)

    @staticmethod
    def orange(txt: str):
        return "\033[1;33m{}\033[0m".format(txt)

    @staticmethod
    def blue(txt: str):
        return "\033[1;34m{}\033[0m".format(txt)

    @staticmethod
    def purple(txt: str):
        return "\033[1;35m{}\033[0m".format(txt)

    @staticmethod
    def cyan(txt: str):
        return "\033[1;36m{}\033[0m".format(txt)
