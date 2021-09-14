from hardware_monitor.hardware_info import LinuxHardwareInfo

import psutil
from psutil._common import shwtemp, sfan

from collections import namedtuple

import pytest

cpu_usage = 50.0
ram_usage = 50.0
temps = {
    'acpitz': [shwtemp(label='', current=47.0, high=103.0, critical=103.0)],
    'asus': [shwtemp(label='', current=47.0, high=None, critical=None)],
    'coretemp': [shwtemp(label='Core 0', current=45.0, high=100.0, critical=100.0),
                shwtemp(label='Core 1', current=52.0, high=100.0, critical=100.0)]
}
fans = {
    'asus': [sfan(label='cpu_fan', current=3200)],
    'corefan': [sfan(label='Core 0', current=1600),
                sfan(label='Core 1', current=800)]
}
battery_charge = 50

@pytest.fixture
def mock_psutil(monkeypatch):
    def mock_cpu_percent():
        return cpu_usage
    def mock_virtual_memory():
        svmem = namedtuple('svmem', ['percent'])
        r = svmem(percent=ram_usage)
        return r
    def mock_sensors_temperatures():
        return temps
    def mock_sensors_fans():
        return fans
    def mock_sensors_battery():
        sbattery = namedtuple('sbattery', ['percent'])
        b = sbattery(percent=battery_charge)
        return b

    monkeypatch.setattr(psutil, "cpu_percent", mock_cpu_percent)
    monkeypatch.setattr(psutil, "virtual_memory", mock_virtual_memory)
    monkeypatch.setattr(psutil, "sensors_temperatures", mock_sensors_temperatures)
    monkeypatch.setattr(psutil, "sensors_fans", mock_sensors_fans)
    monkeypatch.setattr(psutil, "sensors_battery", mock_sensors_battery)

@pytest.fixture
def mock_psutil_some_empty(monkeypatch):
    def mock_cpu_percent():
        return cpu_usage
    def mock_virtual_memory():
        svmem = namedtuple('svmem', ['percent'])
        r = svmem(percent=ram_usage)
        return r
    def mock_sensors_temperatures():
        return {}
    def mock_sensors_fans():
        return {}
    def mock_sensors_battery():
        return None

    monkeypatch.setattr(psutil, "cpu_percent", mock_cpu_percent)
    monkeypatch.setattr(psutil, "virtual_memory", mock_virtual_memory)
    monkeypatch.setattr(psutil, "sensors_temperatures", mock_sensors_temperatures)
    monkeypatch.setattr(psutil, "sensors_fans", mock_sensors_fans)
    monkeypatch.setattr(psutil, "sensors_battery", mock_sensors_battery)

@pytest.fixture
def create_not_critical_config(tmp_path):
    config = tmp_path / "config.json"
    content = \
"""{
    "max_cpu_usage":      101,
    "max_ram_usage":      101,
    "max_temp":           101,
    "min_battery_charge": -1
}"""
    config.write_text(content)
    return config

@pytest.fixture
def create_critical_config(tmp_path):
    config = tmp_path / "config.json"
    content = \
"""{
    "max_cpu_usage":      -1,
    "max_ram_usage":      -1,
    "max_temp":           -1,
    "min_battery_charge": 101
}"""
    config.write_text(content)
    return config

def test_get_info(mock_psutil):
    hi = LinuxHardwareInfo()
    d = hi.get_info()

    assert d["cpu_usage"] == cpu_usage
    assert d["ram_usage"] == ram_usage
    assert d["temps"] == temps
    assert d["fans"] == fans
    assert d["battery_charge"] == battery_charge

def test_get_info_some_empty(mock_psutil_some_empty):
    hi = LinuxHardwareInfo()
    d = hi.get_info()
    
    assert d["cpu_usage"] == cpu_usage
    assert d["ram_usage"] == ram_usage
    assert "temps" not in d
    assert "fans" not in d
    assert "battery_charge" not in d

def test_get_validated_info_not_critical(mock_psutil, create_not_critical_config):
    hi = LinuxHardwareInfo(create_not_critical_config)
    d = hi.get_validated_info()
    
    assert d["cpu_usage"] == cpu_usage
    assert d["ram_usage"] == ram_usage
    assert d["temps"] == temps
    assert d["fans"] == fans
    assert d["battery_charge"] == battery_charge

def test_get_validated_info_critical(mock_psutil, create_critical_config):
    hi = LinuxHardwareInfo(create_critical_config)
    d = hi.get_validated_info()
    
    assert d["cpu_usage"] == f"{cpu_usage} (overload!)"
    assert d["ram_usage"] == f"{ram_usage} (overload!)"
    assert d["temps"] == temps
    assert d["fans"] == fans
    assert d["battery_charge"] == battery_charge
