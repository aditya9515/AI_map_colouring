DEBUG = True

def log(stage: str, msg: str):
    if DEBUG:
        print(f"[DEBUG][{stage}] {msg}")