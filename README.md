# Test task

## Run

```
usage: python -m hardware_monitor [-h] [T]

Log system info at specified interval

positional arguments:
  T           interval of time (default: m10)

optional arguments:
  -h, --help  show this help message and exit

Possible values of T:
  m10  - 10 minutes
  hour - one hour
  day  - one day
```
You can find written logs in `~/hardware_monitor/logs`.

## Test
`.../test_task$ pytest`
