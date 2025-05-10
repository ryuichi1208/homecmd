import datetime
import json

def log_json(level: str, message: str, **kwargs):
    """Outputs logs in JSON format"""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "level": level,
        "message": message,
    }
    if kwargs:
        log_entry.update(kwargs)
    print(json.dumps(log_entry, ensure_ascii=False))
