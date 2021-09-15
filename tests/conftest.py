import psutil
from psutil._common import shwtemp, sfan

from collections import namedtuple

import pytest

def pytest_configure():
    pytest.cpu_usage = 50.0
    pytest.ram_usage = 50.0
    pytest.temps = {
        'acpitz': [shwtemp(label='', current=47.0, high=103.0, critical=103.0)],
        'asus': [shwtemp(label='', current=47.0, high=None, critical=None)],
        'coretemp': [shwtemp(label='Core 0', current=45.0, high=100.0, critical=100.0),
                    shwtemp(label='Core 1', current=52.0, high=100.0, critical=100.0)]
    }
    pytest.fans = {
        'asus': [sfan(label='cpu_fan', current=3200)],
        'corefan': [sfan(label='Core 0', current=1600),
                    sfan(label='Core 1', current=800)]
    }
    pytest.battery_charge = 50.0

@pytest.fixture
def mock_psutil(monkeypatch, request):
    def mock_cpu_percent():
        return pytest.cpu_usage
    def mock_virtual_memory():
        svmem = namedtuple('svmem', ['percent'])
        r = svmem(percent=pytest.ram_usage)
        return r
    def mock_sensors_temperatures():
        return pytest.temps if request.param == 0 else {}
    def mock_sensors_fans():
        return pytest.fans if request.param == 0 else {}
    def mock_sensors_battery():
        sbattery = namedtuple('sbattery', ['percent'])
        b = sbattery(percent=pytest.battery_charge)
        return b if request.param == 0 else None

    monkeypatch.setattr(psutil, "cpu_percent", mock_cpu_percent)
    monkeypatch.setattr(psutil, "virtual_memory", mock_virtual_memory)
    monkeypatch.setattr(psutil, "sensors_temperatures", mock_sensors_temperatures)
    monkeypatch.setattr(psutil, "sensors_fans", mock_sensors_fans)
    monkeypatch.setattr(psutil, "sensors_battery", mock_sensors_battery)

@pytest.fixture
def create_config(tmp_path, request):
    config = tmp_path / "config.json"
    content = None
    # if not critical
    if request.param == 0: 
        content = \
"""{
    "max_cpu_usage":      101,
    "max_ram_usage":      101,
    "max_temp":           101,
    "min_battery_charge": -1
}"""
    # else critical
    else:
        content = \
"""{
    "max_cpu_usage":      -1,
    "max_ram_usage":      -1,
    "max_temp":           -1,
    "min_battery_charge": 101
}"""
    config.write_text(content)
    return config
