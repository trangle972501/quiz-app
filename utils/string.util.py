class StringUtil:
    @staticmethod
    def is_empty(string: str) -> bool:
        return string is None or string.strip() == ""

    @staticmethod
    def to_upper(string: str) -> str:
        if StringUtil.is_empty(string):
            return ""
        return string.upper()

    @staticmethod
    def to_lower(string: str) -> str:
        if StringUtil.is_empty(string):
            return ""
        return string.lower()