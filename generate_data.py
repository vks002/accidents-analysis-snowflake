import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)

NUM_RECORDS = 12000

REGIONS = {
    "Delhi": (28.6139, 77.2090, 0.14),
    "Mumbai": (19.0760, 72.8777, 0.12),
    "Bangalore": (12.9716, 77.5946, 0.09),
    "Chennai": (13.0827, 80.2707, 0.08),
    "Kolkata": (22.5726, 88.3639, 0.07),
    "Hyderabad": (17.3850, 78.4867, 0.07),
    "Pune": (18.5204, 73.8567, 0.06),
    "Ahmedabad": (23.0225, 72.5714, 0.06),
    "Jaipur": (26.9124, 75.7873, 0.06),
    "Lucknow": (26.8467, 80.9462, 0.05),
    "Chandigarh": (30.7333, 76.7794, 0.04),
    "Bhopal": (23.2599, 77.4126, 0.04),
    "Patna": (25.6093, 85.1376, 0.04),
    "Thiruvananthapuram": (8.5241, 76.9366, 0.04),
    "Guwahati": (26.1445, 91.7362, 0.04),
}

SEVERITY_WEIGHTS = {"Slight": 0.60, "Serious": 0.30, "Fatal": 0.10}
WEATHER = {"Clear": 0.50, "Rain": 0.20, "Fog": 0.15, "Cloudy": 0.10, "Hail/Storm": 0.05}
LIGHT_CONDITIONS = {"Daylight": 0.55, "Dark - Lit": 0.25, "Dark - Unlit": 0.15, "Dawn/Dusk": 0.05}
ROAD_TYPES = {"Single Carriageway": 0.40, "Dual Carriageway": 0.25, "Highway/Expressway": 0.15, "Roundabout": 0.08, "One Way": 0.07, "Slip Road": 0.05}
ROAD_SURFACE = {"Dry": 0.55, "Wet": 0.30, "Snow/Ice": 0.05, "Muddy": 0.05, "Flooded": 0.05}
VEHICLE_TYPES = {"Car": 0.35, "Two Wheeler": 0.25, "Truck/Lorry": 0.12, "Bus": 0.08, "Auto Rickshaw": 0.08, "Bicycle": 0.05, "Pedestrian": 0.04, "Other": 0.03}
SPEED_LIMITS = {30: 0.25, 40: 0.15, 50: 0.20, 60: 0.15, 80: 0.15, 100: 0.10}


def weighted_choice(options):
    items = list(options.keys())
    weights = list(options.values())
    return random.choices(items, weights=weights, k=1)[0]


def generate_record(acc_id, start_date, end_date):
    days_range = (end_date - start_date).days
    acc_date = start_date + timedelta(days=random.randint(0, days_range))
    hour = random.choices(range(24), weights=[
        2, 1, 1, 1, 2, 3, 5, 8, 9, 7, 6, 5,
        6, 5, 5, 6, 7, 9, 10, 8, 6, 5, 4, 3
    ], k=1)[0]
    minute = random.randint(0, 59)
    acc_time = f"{hour:02d}:{minute:02d}"

    region_names = list(REGIONS.keys())
    region_weights = [v[2] for v in REGIONS.values()]
    region = random.choices(region_names, weights=region_weights, k=1)[0]
    base_lat, base_lon, _ = REGIONS[region]
    lat = round(base_lat + random.uniform(-0.15, 0.15), 6)
    lon = round(base_lon + random.uniform(-0.15, 0.15), 6)

    severity = weighted_choice(SEVERITY_WEIGHTS)
    speed_limit = weighted_choice(SPEED_LIMITS)
    weather = weighted_choice(WEATHER)
    light = weighted_choice(LIGHT_CONDITIONS)
    road_type = weighted_choice(ROAD_TYPES)
    road_surface = weighted_choice(ROAD_SURFACE)
    vehicle_type = weighted_choice(VEHICLE_TYPES)

    num_vehicles = random.choices([1, 2, 3, 4, 5], weights=[20, 45, 20, 10, 5], k=1)[0]

    if severity == "Fatal":
        num_fatalities = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5], k=1)[0]
        num_injuries = random.randint(0, num_vehicles * 2)
    elif severity == "Serious":
        num_fatalities = 0
        num_injuries = random.randint(1, num_vehicles * 2 + 1)
    else:
        num_fatalities = 0
        num_injuries = random.choices([0, 1, 2], weights=[30, 50, 20], k=1)[0]

    num_casualties = num_fatalities + num_injuries
    day_of_week = acc_date.strftime("%A")

    return {
        "accident_id": f"ACC-{acc_id:06d}",
        "date": acc_date.strftime("%Y-%m-%d"),
        "time": acc_time,
        "day_of_week": day_of_week,
        "region": region,
        "latitude": lat,
        "longitude": lon,
        "severity": severity,
        "num_vehicles": num_vehicles,
        "num_casualties": num_casualties,
        "num_fatalities": num_fatalities,
        "num_injuries": num_injuries,
        "road_type": road_type,
        "speed_limit": speed_limit,
        "weather": weather,
        "light_conditions": light,
        "road_surface": road_surface,
        "vehicle_type": vehicle_type,
    }


def main():
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, "data", "road_accidents.csv")

    fields = [
        "accident_id", "date", "time", "day_of_week", "region",
        "latitude", "longitude", "severity", "num_vehicles",
        "num_casualties", "num_fatalities", "num_injuries",
        "road_type", "speed_limit", "weather", "light_conditions",
        "road_surface", "vehicle_type",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i in range(1, NUM_RECORDS + 1):
            writer.writerow(generate_record(i, start_date, end_date))

    print(f"Generated {NUM_RECORDS} records -> {out_path}")


if __name__ == "__main__":
    main()
