from hardware_monitor.hardware_info import LinuxHardwareInfo
from hardware_monitor.utils import sensors_dict_to_usual_dict

import pytest

@pytest.mark.parametrize("mock_psutil, variant", [(0, 0), (1, 1)],
                         ids=["full", "some_empty"], indirect=["mock_psutil"])
def test_get_info(mock_psutil, variant):
    hi = LinuxHardwareInfo()
    d = hi.get_info()
    
    assert d["cpu_usage"] == pytest.cpu_usage
    assert d["ram_usage"] == pytest.ram_usage
    if variant == 0:
        assert d["temps"] == sensors_dict_to_usual_dict(pytest.temps)
        assert d["fans"] == sensors_dict_to_usual_dict(pytest.fans)
        assert d["battery_charge"] == pytest.battery_charge
    else:
        assert "temps" not in d
        assert "fans" not in d
        assert "battery_charge" not in d

@pytest.mark.parametrize("mock_psutil", [0], ids=["full"], indirect=True)
def test_get_validated_info_not_critical(mock_psutil, create_not_critical_config):
    hi = LinuxHardwareInfo(create_not_critical_config)
    d = hi.get_validated_info()
    
    assert d["cpu_usage"] == pytest.cpu_usage
    assert d["ram_usage"] == pytest.ram_usage
    assert d["temps"] == sensors_dict_to_usual_dict(pytest.temps)
    assert d["fans"] == sensors_dict_to_usual_dict(pytest.fans)
    assert d["battery_charge"] == pytest.battery_charge

@pytest.mark.parametrize("mock_psutil", [0], ids=["full"], indirect=True)
def test_get_validated_info_critical(mock_psutil, create_critical_config):
    hi = LinuxHardwareInfo(create_critical_config)
    d = hi.get_validated_info()
    
    assert d["cpu_usage"] == f"{pytest.cpu_usage} (overload!)"
    assert d["ram_usage"] == f"{pytest.ram_usage} (overload!)"
    tmp_temps = sensors_dict_to_usual_dict(pytest.temps)
    names = tmp_temps.keys()
    for name in names:
        for entry in tmp_temps[name]:
                entry["current"] = f"{entry['current']} (overheat!)"
    assert d["temps"] == tmp_temps
    assert d["fans"] == sensors_dict_to_usual_dict(pytest.fans)
    assert d["battery_charge"] == f"{pytest.battery_charge} (too low!)"
