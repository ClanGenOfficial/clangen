import os

from scripts.housekeeping.datadir import get_log_dir


def prune_logs(logs_to_keep: int, retain_empty_logs: bool):
    log_files = os.listdir(get_log_dir())
    log_files.sort()
    log_files.reverse()

    log_list: dict[str] = {}

    for log_file in log_files:
        log_type = log_file.split('_')[0]

        if not log_list.__contains__(log_type):
            log_list[log_type] = 1
        else:
            if log_list[log_type] >= logs_to_keep or not retain_empty_logs and os.stat(f"{get_log_dir()}/{log_file}").st_size == 0:
                os.remove(f"{get_log_dir()}/{log_file}")
            else:
                log_list[log_type] += 1
