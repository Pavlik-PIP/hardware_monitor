import psutil

import json

class HardwareInfo():
    def __init__(self, config=None):
        self.is_configured = False
        if config:
            self.is_configured = True
            with open(config, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.max_cpu_usage      = data["max_cpu_usage"]
            self.max_ram_usage      = data["max_ram_usage"]
            self.max_temp           = data["max_temp"]
            self.min_battery_charge = data["min_battery_charge"]
    def get_info(self) -> dict:
        pass
    def get_validated_info(self) -> dict:
        pass

class WinHardwareInfo(HardwareInfo):
    pass

class LinuxHardwareInfo(HardwareInfo):
    def __init__(self, config=None):
        HardwareInfo.__init__(self, config)

    def get_info(self) -> dict:
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        temps = psutil.sensors_temperatures()
        fans = psutil.sensors_fans()
        battery = psutil.sensors_battery()
        battery_charge = battery.percent if battery else None

        d = {"cpu_usage": cpu_usage, "ram_usage": ram_usage}
        if temps:
            d["temps"] = temps
        if fans:
            d["fans"] = fans
        if battery_charge:
            d["battery_charge"] = battery_charge

        return d

    def get_validated_info(self) -> dict:
        d = self.get_info()
        if self.is_configured:
            if d["cpu_usage"] > self.max_cpu_usage:
                d["cpu_usage"] = f"{d['cpu_usage']} (overload!)"
            if d["ram_usage"] > self.max_ram_usage:
                d["ram_usage"] = f"{d['ram_usage']} (overload!)"

            if "temps" in d:
                names = d["temps"].keys()
                for name in names:
                    for entry in d["temps"][name]:
                        if entry.current > self.max_temp:
                            entry.current = f"{entry.current} (overheat!)"

            if "battery_charge" in d:
                if d["battery_charge"] < self.min_battery_charge:
                    d["battery_charge"] = f"{d['battery_charge']} (too low!)"
        return d
