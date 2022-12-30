from cfg import Config


config = Config()


def check_int(s:str)->bool:
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def encode_param(param: list)->str:
    copy = param.copy()
    for i in range(len(copy)):
        if type(copy[i]) is not str:
            copy[i] = str(param[i])
    return "_".join(copy)
