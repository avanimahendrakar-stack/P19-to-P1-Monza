from pathlib import Path
from typing import Any, cast

import fastf1  # pyright: ignore[reportMissingTypeStubs]
import pandas as pd


YEAR = 2026
EVENT = "Italy"
SESSION_TYPE = "R"
OUTPUT_DIR = Path(__file__).parent / "data"
DRIVERS = {
    "ANT": "kimi_telemetry.csv",
    "RUS": "russell_telemetry.csv",
    "VER": "verstappen_telemetry.csv",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir = Path.home() / ".cache" / "fastf1"
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))

    session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
    session.load(laps=True, telemetry=True, weather=False, messages=False)

    results = pd.DataFrame(session.results).reset_index(drop=True)
    results.to_csv(OUTPUT_DIR / "race_results.csv", index=False)

    laps = pd.DataFrame(session.laps).reset_index(drop=True)
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    laps["IsValidLap"] = (
        laps["LapTime"].notna()
        & laps["IsAccurate"].fillna(False)
        & ~laps["Deleted"].astype("boolean").fillna(False)
    )
    laps.to_csv(OUTPUT_DIR / "laps.csv", index=False)

    available_drivers = set(results["Abbreviation"].dropna())
    missing_drivers = set(DRIVERS) - available_drivers
    if missing_drivers:
        raise ValueError(f"Expected drivers not found in race results: {sorted(missing_drivers)}")

    for abbreviation, filename in DRIVERS.items():
        driver_laps = cast(Any, session.laps).pick_drivers(abbreviation)
        telemetry_laps: list[pd.DataFrame] = []

        for _, lap in driver_laps.iterlaps():
            lap_time = lap["LapTime"]
            is_accurate = lap["IsAccurate"]
            is_deleted = lap["Deleted"]
            if (
                pd.isna(lap_time)
                or not is_accurate
                or (pd.notna(is_deleted) and bool(is_deleted))
            ):
                continue

            telemetry = lap.get_telemetry()
            telemetry["Driver"] = abbreviation
            telemetry["LapNumber"] = lap["LapNumber"]
            telemetry["LapPosition"] = lap["Position"]
            telemetry["LapTimeSeconds"] = lap_time.total_seconds()
            telemetry_laps.append(telemetry)

        if not telemetry_laps:
            raise ValueError(f"No valid telemetry laps found for {abbreviation}")

        driver_telemetry = pd.concat(telemetry_laps, ignore_index=True)
        driver_telemetry.to_csv(OUTPUT_DIR / filename, index=False)
        print(f"Wrote {filename}: {len(driver_telemetry):,} samples")

    print(f"Wrote race_results.csv: {len(results)} drivers")
    print(f"Wrote laps.csv: {len(laps)} laps ({laps['IsValidLap'].sum()} valid)")
    print(f"Data directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()