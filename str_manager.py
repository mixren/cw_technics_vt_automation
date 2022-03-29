class StrManager:
    def change_last_dash_to_dot(s: str) -> str:
        last_index = s.rfind("-")
        return s[:last_index] + "." + s[last_index+1:]

    def is_rasejumi_in_string(s: str) -> bool:
        return s.lower().find('raseju') is not -1
