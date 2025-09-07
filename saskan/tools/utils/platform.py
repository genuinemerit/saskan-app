# saskan/tools/utils/platform.py

import json
import logging
import platform
import re
import socket
import uuid

import psutil


def sys_info() -> str:
    try:
        info = {}
        info["platform"] = platform.system()
        info["platform-release"] = platform.release()
        info["platform-version"] = platform.version()
        info["architecture"] = platform.machine()
        info["python-version"] = platform.python_version()
        info["hostname"] = socket.gethostname()
        info["ip-address"] = socket.gethostbyname(socket.gethostname())
        info["mac-address"] = ":".join(re.findall("..", "%012x" % uuid.getnode()))
        info["processor"] = platform.processor()
        info["ram"] = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    except Exception as e:
        logging.exception(e)

    return json.dumps(info)
