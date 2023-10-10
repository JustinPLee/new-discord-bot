from datetime import datetime

from config import LOGGING

def log(msg: str, append_before="") -> None:
    if not LOGGING:
        return None

    log_msg = append_before + f"{datetime.now()} | Log: {msg}\n"
    with open("logs/logs.txt", "a") as logfile:
        logfile.write(log_msg)