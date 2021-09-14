from hardware_monitor.hardware_info import LinuxHardwareInfo
from hardware_monitor.utils import sensors_dict_to_usual_dict

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
def mock_psutil(monkeypatch, request):
    def mock_cpu_percent():
        return cpu_usage
    def mock_virtual_memory():
        svmem = namedtuple('svmem', ['percent'])
        r = svmem(percent=ram_usage)
        return r
    def mock_sensors_temperatures():
        return temps if request.param == 0 else {}
    def mock_sensors_fans():
        return fans if request.param == 0 else {}
    def mock_sensors_battery():
        sbattery = namedtuple('sbattery', ['percent'])
        b = sbattery(percent=battery_charge)
        return b if request.param == 0 else None

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

@pytest.mark.parametrize("mock_psutil, variant", [(0, 0), (1, 1)],
                         ids=["full", "some_empty"], indirect=["mock_psutil"])
def test_get_info(mock_psutil, variant):
    hi = LinuxHardwareInfo()
    d = hi.get_info()
    
    assert d["cpu_usage"] == cpu_usage
    assert d["ram_usage"] == ram_usage
    if variant == 0:
        assert d["temps"] == sensors_dict_to_usual_dict(temps)
        assert d["fans"] == sensors_dict_to_usual_dict(fans)
        assert d["battery_charge"] == battery_charge
    else:
        assert "temps" not in d
        assert "fans" not in d
        assert "battery_charge" not in d

@pytest.mark.parametrize("mock_psutil", [0], ids=["full"], indirect=True)
def test_get_validated_info_not_critical(mock_psutil, create_not_critical_config):
    hi = LinuxHardwareInfo(create_not_critical_config)
    d = hi.get_validated_info()
    
    assert d["cpu_usage"] == cpu_usage
    assert d["ram_usage"] == ram_usage
    assert d["temps"] == sensors_dict_to_usual_dict(temps)
    assert d["fans"] == sensors_dict_to_usual_dict(fans)
    assert d["battery_charge"] == battery_charge

@pytest.mark.parametrize("mock_psutil", [0], ids=["full"], indirect=True)
def test_get_validated_info_critical(mock_psutil, create_critical_config):
    hi = LinuxHardwareInfo(create_critical_config)
    d = hi.get_validated_info()
    
    assert d["cpu_usage"] == f"{cpu_usage} (overload!)"
    assert d["ram_usage"] == f"{ram_usage} (overload!)"
    tmp_temps = sensors_dict_to_usual_dict(temps)
    names = tmp_temps.keys()
    for name in names:
        for entry in tmp_temps[name]:
                entry["current"] = f"{entry['current']} (overheat!)"
    assert d["temps"] == tmp_temps
    assert d["fans"] == sensors_dict_to_usual_dict(fans)
    assert d["battery_charge"] == f"{battery_charge} (too low!)"
