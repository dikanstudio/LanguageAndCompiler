import logging
import sys
import common.utils as utils
import lark

def _setupLogging(consoleLevel: int, logfile: str|None):
    log = logging.getLogger('minipy')
    _setupLoggingForLogger(log, consoleLevel, logfile)
    _setupLoggingForLogger(lark.logger, consoleLevel, logfile)
    return log

def _setupLoggingForLogger(log: logging.Logger, consoleLevel: int, logfile: str|None):
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter('[%(asctime)s %(levelname)s %(filename)s:%(lineno)d] %(message)s',
                            datefmt='%Y-%m-%dT%H:%M:%S')
    consoleH = logging.StreamHandler()
    consoleH.setLevel(consoleLevel)
    consoleH.setFormatter(fmt)
    log.addHandler(consoleH)
    if logfile is not None:
        fileH = logging.FileHandler(filename=logfile, mode='w', encoding='utf-8')
        fileH.setLevel(logging.DEBUG)
        fileH.setFormatter(fmt)
        log.addHandler(fileH)
    return log

_log = _setupLogging(logging.WARNING, None)

def resolveLevelName(s: str) -> int:
    s = s.lower()
    match s:
        case "debug": return logging.DEBUG
        case "info": return logging.INFO
        case "warn": return logging.WARNING
        case "error": return logging.ERROR
        case _:
            utils.abort(f"Invalid log level: {s}")

def removeAllHandlers(log: logging.Logger):
    for h in log.handlers[:]:
        log.removeHandler(h)

def init(level: int, filename: str):
    global _log
    if _log:
        removeAllHandlers(_log)
    removeAllHandlers(lark.logger)
    _log = _setupLogging(level, filename)

STACKLEVEL=2

def debug(s: str):
    _log.debug(s, stacklevel=STACKLEVEL)

def info(s: str):
    _log.info(s, stacklevel=STACKLEVEL)

def warn(s: str):
    _log.warn(s, stacklevel=STACKLEVEL)

def error(s: str):
    _log.error(s, stacklevel=STACKLEVEL)

def abort(s: str):
    _log.error(s, stacklevel=STACKLEVEL)
    sys.exit(1)
