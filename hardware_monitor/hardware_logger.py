from .hardware_info import LinuxHardwareInfo, WinHardwareInfo
from .repeated_timer import RepeatedTimer

import os
import platform
import datetime

class HardwareLogger():
    STR_DATE_FT = "%Y-%m-%d"
    STR_DATETIME_FT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, interval, config, log_dir=None):
        self.repeated_timer = RepeatedTimer(interval, self._run)

        if platform.system() == "Windows":
            self.hardware_info = WinHardwareInfo(config)
        else:
            self.hardware_info = LinuxHardwareInfo(config)

        self.current_date = None
        self.is_running = False
        self.log_dir = log_dir if log_dir else "logs"

        header = f"{'Time':<20}|{'CPU usage [%]':<18}|{'RAM usage [%]':<18}|"
        d = self.hardware_info.get_info()
        if "temps" in d:
            names = d["temps"].keys()
            for name in names:
                for entry in d["temps"][name]:
                    temp_name = f"{name} {entry['label'].ljust()}temp [\u00B0C]"
                    header = f"{header}{temp_name:<20}|"
        if "fans" in d:
            names = d["fans"].keys()
            for name in names:
                for entry in d["fans"][name]:
                    fan_name = f"{name} {entry['label'].ljust()}fan speed [RPM]"
                    header = f"{header}{fan_name:<28}|"
        if "battery_charge" in d:
            header = f"{header}{'Battery charge [%]':<19}|"

        self.header = header

    def start(self):
        if not self.is_running:
            self.repeated_timer.start()
            self.is_running = True

    def stop(self):
        self.repeated_timer.stop()
        self.is_running = False

    def _run(self):
        self._setup_current_log()
        self._write()

    def _setup_current_log(self):
        if not os.path.isdir(self.log_dir):
            os.makedirs(self.log_dir)

        current_date = datetime.date.today()
        if self.current_date != current_date:
            self.current_date = current_date
            self.current_log = f"{self.current_date.strftime(self.STR_DATE_FT)}.txt"
            self.log_path = os.path.join(self.log_dir, self.current_log)
        if not os.path.isfile(self.log_path):
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write(f"{self.header}{os.linesep}")

    def _write(self):
        d = self.hardware_info.get_validated_info()
        current_datetime = datetime.datetime.now().strftime(self.STR_DATETIME_FT)
        line = f"{current_datetime:<20}|{d['cpu_usage']:<18}|{d['ram_usage']:<18}|"
        if "temps" in d:
            names = d["temps"].keys()
            for name in names:
                for entry in d["temps"][name]:
                    line = f"{line}{entry.current:<20}|"
        if "fans" in d:
            names = d["fans"].keys()
            for name in names:
                for entry in d["fans"][name]:
                    line = f"{line}{entry.current:<28}|"
        if "battery_charge" in d:
            line = f"{line}{d['battery_charge']:<19}|"

        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"{line}{os.linesep}")

