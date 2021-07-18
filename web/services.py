import psutil
import GPUtil
import logging
from datetime import datetime
from settings import DT_FORMAT


logger = logging.getLogger(__name__)


def filter_keys(keys: list, str_from: str = None, str_to: str = None) -> list:
    """
    Возвращает ключи, ограниченные интервалом по дате

    :param keys: список со значениями bytes вида b'MM:DD:hh:mm:ss'
    :param str_from: строка даты "от"
    :param str_to: строка даты "до"
    :return: список
    """
    dt_from = None
    dt_to = None
    if str_from:
        dt_from = datetime.strptime(str_from, DT_FORMAT)
    if str_to:
        dt_to = datetime.strptime(str_to, DT_FORMAT)

    filtered = list()
    if dt_from or dt_to:
        for key in keys:
            str_key = key.decode()
            dt_key = datetime.strptime(str_key, DT_FORMAT)
            
            if dt_to and dt_from and dt_from < dt_key < dt_to:
                filtered.append(str_key)
            elif dt_from and dt_key > dt_from:
                filtered.append(str_key)
            elif dt_to and dt_key < dt_to:
                filtered.append(str_key)
    else:
        filtered = [key.decode() for key in keys]

    return filtered


def get_cpu():
    return psutil.cpu_percent()


def get_ram():
    return psutil.virtual_memory().percent


def get_gpu():
    percentage = None

    try:
        memory_used = 0
        memory_total = 0

        GPUs = GPUtil.getGPUs()
        for GPU in GPUs:
            memory_used += GPU.memoryUsed
            memory_total += GPU.memoryTotal

        percentage = round(memory_used * 100 / memory_total, 1)

    except (ValueError, ZeroDivisionError) as e:
        logger.warning(f"No gpu\n{e}", exc_info=True)

    return percentage
