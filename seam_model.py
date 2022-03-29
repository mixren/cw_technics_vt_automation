from xmlrpc.client import boolean

class Seam:
    def __init__(self, id, vt, pt, rt):
        self.id = id
        self.vt = vt
        self.pt = pt
        self.rt = rt

    def __check_percents(self, t: str) -> boolean:
        return t == "100%"

    def with_xray(self) -> boolean:
        return all((self.__check_percents(self.pt), self.__check_percents(self.rt)))

    def is_flange_stop(self) -> boolean:
        return "S" in self.id
