from hardware_monitor.hardware_logger import HardwareLogger
from hardware_monitor.repeated_timer import RepeatedTimer
from hardware_monitor.main import Interval

from freezegun import freeze_time

import os

import pytest

@pytest.fixture
def mock_repeated_timer(monkeypatch):
    def mock_start(self):
        self.function(*self.args, **self.kwargs)
    def mock_stop(self):
        pass

    monkeypatch.setattr(RepeatedTimer, "start", mock_start)
    monkeypatch.setattr(RepeatedTimer, "stop", mock_stop)

def part_test_logger(interval, tmpdir, psutil_variant, config_variant):
    if interval == Interval.M10:
        file_name = "2021-01-20.txt"
        time = "2021-01-20 00:10:00"
    elif interval == Interval.HOUR:
        file_name = "2021-01-20.txt"
        time = "2021-01-20 01:00:00"
    elif interval == Interval.DAY:
        file_name = "2021-01-21.txt"
        time = "2021-01-21 00:00:00"

    file = tmpdir / file_name
    with file.open() as f:
        lines_count = sum(1 for line in f)
    assert lines_count == 2

    with file.open() as f:
        header = f.readline()
        line = f.readline()

    grad = "[\u00B0C]"

    if psutil_variant == 0:
        assert header == (f"{'Time':<20}|{'CPU usage [%]':<18}|{'RAM usage [%]':<18}|"
                          f"{f'acpitz temp {grad}':<25}|"
                          f"{f'asus temp {grad}':<25}|"
                          f"{f'coretemp Core 0 temp {grad}':<25}|"
                          f"{f'coretemp Core 1 temp {grad}':<25}|"
                          f"{'asus cpu_fan fan speed [RPM]':<30}|"
                          f"{'corefan Core 0 fan speed [RPM]':<30}|"
                          f"{'corefan Core 1 fan speed [RPM]':<30}|"
                          f"{'Battery charge [%]':<19}|"
                          f"{os.linesep}")

        if config_variant == 0:
            assert line == (f"{time:<20}|{pytest.cpu_usage:<18}|{pytest.ram_usage:<18}|"
                            f"{'47.0':<25}|"
                            f"{'47.0':<25}|"
                            f"{'45.0':<25}|"
                            f"{'52.0':<25}|"
                            f"{'3200':<30}|"
                            f"{'1600':<30}|"
                            f"{'800':<30}|"
                            f"{pytest.battery_charge:<19}|"
                            f"{os.linesep}")
        else:
            assert line == (f"{time:<20}|"
                            f"{f'{pytest.cpu_usage} (overload!)':<18}|"
                            f"{f'{pytest.ram_usage} (overload!)':<18}|"
                            f"{'47.0 (overheat!)':<25}|"
                            f"{'47.0 (overheat!)':<25}|"
                            f"{'45.0 (overheat!)':<25}|"
                            f"{'52.0 (overheat!)':<25}|"
                            f"{'3200':<30}|"
                            f"{'1600':<30}|"
                            f"{'800':<30}|"
                            f"{f'{pytest.battery_charge} (too low!)':<19}|"
                            f"{os.linesep}")
    else:
        assert header == f"{'Time':<20}|{'CPU usage [%]':<18}|{'RAM usage [%]':<18}|{os.linesep}"
        if config_variant == 0:
            assert line == (f"{time:<20}|"
                            f"{pytest.cpu_usage:<18}|"
                            f"{pytest.ram_usage:<18}|"
                            f"{os.linesep}")
        else:
            assert line == (f"{time:<20}|"
                            f"{f'{pytest.cpu_usage} (overload!)':<18}|"
                            f"{f'{pytest.ram_usage} (overload!)':<18}|"
                            f"{os.linesep}")

@pytest.mark.parametrize("create_config, config_variant", [(0, 0), (1, 1)],
                         ids=["not_critical", "critical"], indirect=["create_config"])
@pytest.mark.parametrize("mock_psutil, psutil_variant", [(0, 0), (1, 1)],
                         ids=["full", "some_empty"], indirect=["mock_psutil"])
@freeze_time("2021-01-20 00:00:00", auto_tick_seconds=Interval.M10)
def test_hardware_logger_m10(mock_repeated_timer, mock_psutil, create_config,
                             tmpdir, psutil_variant, config_variant):
    l = HardwareLogger(Interval.M10, create_config, tmpdir)
    l.start()
    l.stop()

    part_test_logger(Interval.M10, tmpdir, psutil_variant, config_variant)

@pytest.mark.parametrize("create_config, config_variant", [(0, 0), (1, 1)],
                         ids=["critical", "not_critical"], indirect=["create_config"])
@pytest.mark.parametrize("mock_psutil, psutil_variant", [(0, 0), (1, 1)],
                         ids=["full", "some_empty"], indirect=["mock_psutil"])
@freeze_time("2021-01-20 00:00:00", auto_tick_seconds=Interval.HOUR)
def test_hardware_logger_hour(mock_repeated_timer, mock_psutil, create_config,
                             tmpdir, psutil_variant, config_variant):
    l = HardwareLogger(Interval.HOUR, create_config, tmpdir)
    l.start()
    l.stop()

    part_test_logger(Interval.HOUR, tmpdir, psutil_variant, config_variant)

@pytest.mark.parametrize("create_config, config_variant", [(0, 0), (1, 1)],
                         ids=["critical", "not_critical"], indirect=["create_config"])
@pytest.mark.parametrize("mock_psutil, psutil_variant", [(0, 0), (1, 1)],
                         ids=["full", "some_empty"], indirect=["mock_psutil"])
def test_hardware_logger_day(mock_repeated_timer, mock_psutil, create_config,
                             tmpdir, psutil_variant, config_variant):
    l = HardwareLogger(Interval.DAY, create_config, tmpdir)
    with freeze_time("2021-01-20 00:00:00"):
        l.start()
        l.stop()

    with freeze_time("2021-01-21 00:00:00"):
        l.start()
        l.stop()

    part_test_logger(Interval.DAY, tmpdir, psutil_variant, config_variant)
