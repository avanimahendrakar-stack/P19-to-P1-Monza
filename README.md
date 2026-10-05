# P19 to P1: Monza Race Data

FastF1 data extraction for the 2026 Italian Grand Prix, focused on Kimi Antonelli, George Russell, and Max Verstappen.

## Run

Install the dependencies and run the extractor from this directory:

```powershell
python -m pip install -r requirements.txt
python extract_data.py
```

The script downloads and caches the race session data, then writes these files to `data/`:

- `race_results.csv`: race classification and grid positions
- `laps.csv`: lap times, sectors, positions, and an `IsValidLap` flag
- `kimi_telemetry.csv`, `russell_telemetry.csv`, `verstappen_telemetry.csv`: telemetry from accurate, non-deleted laps, including speed, throttle, brake, and distance

The dashboard and presentation are not included yet; this repository currently contains the data extraction stage.