import pandas as pd
import matplotlib.pyplot as plt

# --- Weather Data Processing ---
# Load sensor data (HOBO logger export)
sensor_df = pd.read_csv("sensor_5_4.csv", encoding="latin-1", skiprows=1)
sensor_df.columns = ["idx5", "time5", "temp5", "rh5", "dew5",
                      "idx4", "time4", "temp4", "rh4"]
sensor_df["time5"] = pd.to_datetime(sensor_df["time5"])

# Load weather station data
weather_df = pd.read_excel("DX4PG3N5_1.xlsx", skiprows=12)
weather_df.columns = ["datetime", "air_temp_f", "rh_pct"]
weather_df["datetime"] = pd.to_datetime(weather_df["datetime"])

weather_df["air_temp_f"] = pd.to_numeric(weather_df["air_temp_f"], errors="coerce")
weather_df["rh_pct"] = pd.to_numeric(weather_df["rh_pct"], errors="coerce")
weather_df = weather_df.sort_values("datetime").reset_index(drop=True)

WINDOW_MINUTES = 15

def window_average(timestamp):
    """Average the 1-min weather readings covering the WINDOW_MINUTES
    leading up to and including `timestamp`."""
    start = timestamp - pd.Timedelta(minutes=WINDOW_MINUTES - 1)
    window = weather_df[(weather_df["datetime"] >= start) & (weather_df["datetime"] <= timestamp)]
    return pd.Series({
        "weather_temp_avg": window["air_temp_f"].mean(),
        "weather_rh_avg": window["rh_pct"].mean(),
        "weather_points_used": len(window),
    })

# Apply window average to sensor timestamps
averages = sensor_df["time5"].apply(window_average)
result = pd.concat([sensor_df, averages], axis=1)

result.to_csv("sensor_with_weather_averages.csv", index=False)

# --- Figure 1: Full Range Sensor Comparison ---
df = pd.read_csv("Greenhouse data(SENSOR4_5).csv", encoding="latin-1", skiprows=1)
df.columns = ["idx4", "time4", "temp4", "rh4", "dew4",
              "idx5", "time5", "temp5", "rh5", "dew5"]
df["time5"] = pd.to_datetime(df["time5"])

fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax1.plot(df["time5"], df["temp5"], label="Sensor 5 Temp (°F)")
ax1.plot(df["time5"], df["temp4"], label="Sensor 4 Temp (°F)")
ax1.set_ylabel("Temperature (°F)")
ax1.set_title("Sensor 5 vs Sensor 4 Temperature")
ax1.legend()

ax2.plot(df["time5"], df["temp5"], color="tab:red", label="Sensor 5 Temp (°F)")
ax2.set_ylabel("Temperature (°F)", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")

ax2b = ax2.twinx()
ax2b.plot(df["time4"], df["rh4"], color="tab:blue", label="Sensor 4 RH (%)")
ax2b.set_ylabel("Relative Humidity (%)", color="tab:blue")
ax2b.tick_params(axis="y", labelcolor="tab:blue")
ax2.set_title("Sensor 4 Temperature & Humidity")

plt.tight_layout()
plt.savefig("greenhouse_plot.png", dpi=150)
plt.show()

# --- Figure 2: Zoomed Day (2026-09-16) ---
df_day = df[df["time4"].dt.date == pd.to_datetime("2026-09-16").date()]

fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax1.plot(df_day["time4"], df_day["temp4"], label="Sensor 4 Temp (°F)")
ax1.plot(df_day["time4"], df_day["temp5"], label="Sensor 5 Temp (°F)")
ax1.set_ylabel("Temperature (°F)")
ax1.set_title("Sensor 4 vs Sensor 5 Temperature - 2026-09-16")
ax1.legend()

ax2.plot(df_day["time4"], df_day["temp4"], color="tab:red", label="Sensor 4 Temp (°F)")
ax2.set_ylabel("Temperature (°F)", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")

ax2b = ax2.twinx()
ax2b.plot(df_day["time4"], df_day["rh4"], color="tab:blue", label="Sensor 4 RH (%)")
ax2b.set_ylabel("Relative Humidity (%)", color="tab:blue")
ax2b.tick_params(axis="y", labelcolor="tab:blue")
ax2.set_title("Sensor 4 Temperature & Humidity - 2026-09-16")

plt.tight_layout()
plt.savefig("greenhouse_plot_2026-09-16.png", dpi=150)
plt.show()

# --- Figure 3: Sensors + Weather Station Data Comparison ---
fig3, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Top Plot: Sensor 4, Sensor 5, and Weather Temperature
ax1.plot(result["time4"], result["temp4"], label="Sensor 4 Temp (°F)")
ax1.plot(result["time4"], result["temp5"], label="Sensor 5 Temp (°F)")
ax1.plot(result["time4"], result["weather_temp_avg"], label="Weather Station Temp (°F)", linestyle="--", color="tab:green")
ax1.set_ylabel("Temperature (°F)")
ax1.set_title("Sensor 4 vs Sensor 5 vs Weather Station Temperature")
ax1.legend()

# Bottom Plot: Sensor 4 RH vs Weather Station Relative Humidity
ax2.plot(result["time4"], result["rh4"], label="Sensor 4 RH (%)", color="tab:blue")
ax2.plot(result["time4"], result["weather_rh_avg"], label="Weather Station RH (%)", linestyle="--", color="tab:cyan")
ax2.set_ylabel("Relative Humidity (%)")
ax2.set_title("Sensor 4 vs Weather Station Relative Humidity")
ax2.legend()

plt.tight_layout()
plt.savefig("greenhouse_plot_with_weather.png", dpi=150)
plt.show()
plt.show()

