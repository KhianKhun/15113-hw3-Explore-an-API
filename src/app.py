import tkinter as tk
from tkinter import ttk

from .weather import fetch_forecast_periods, fetch_latest_relative_humidity
from .cities import CITY_DB, ALL_CITIES
from .city_search import CitySearchController
from .forecast_summary import build_day_summaries, format_days, format_now


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NWS Weather Lookup (Preset Cities)")
        self.geometry("700x520")
        self.resizable(False, False)

        self.city_var = tk.StringVar(value=ALL_CITIES[0])
        self.status_var = tk.StringVar(value="Ready")

        self.time_range_var = tk.StringVar(value="")
        self.show_temp_range = tk.BooleanVar(value=False)
        self.show_weather = tk.BooleanVar(value=False)
        self.show_wind = tk.BooleanVar(value=False)
        self.temp_unit_var = tk.StringVar(value="F")

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="City:").grid(row=0, column=0, sticky="w")

        self.city_combo = ttk.Combobox(
            frame,
            textvariable=self.city_var,
            values=ALL_CITIES,
            width=45,
        )
        self.city_combo.grid(row=0, column=1, sticky="we", padx=(8, 8))
        self.city_combo.focus_set()

        self.suggest_list = tk.Listbox(frame, height=0)
        self.suggest_list.grid(row=1, column=1, sticky="we", padx=(8, 8))
        self.suggest_list.grid_remove()

        self.fetch_btn = ttk.Button(frame, text="Fetch", command=self.on_fetch)
        self.fetch_btn.grid(row=0, column=2, sticky="e")

        frame.columnconfigure(1, weight=1)

        self.city_search = CitySearchController(
            self.city_combo,
            self.suggest_list,
            self.city_var,
            ALL_CITIES,
        )
        self.city_search.bind(status_callback=self.status_var.set)

        options_frame = ttk.Frame(frame)
        options_frame.grid(row=2, column=0, columnspan=3, sticky="we", pady=(10, 0))

        time_frame = ttk.LabelFrame(options_frame, text="Time Range")
        time_frame.grid(row=0, column=0, sticky="w", padx=(0, 12))

        ttk.Radiobutton(time_frame, text="Show Today", value="1", variable=self.time_range_var).grid(
            row=0, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Radiobutton(time_frame, text="Show Next 3 Days", value="3", variable=self.time_range_var).grid(
            row=1, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Radiobutton(time_frame, text="Show Next 7 Days", value="7", variable=self.time_range_var).grid(
            row=2, column=0, sticky="w", padx=8, pady=2
        )

        info_frame = ttk.LabelFrame(options_frame, text="Extra Info")
        info_frame.grid(row=0, column=1, sticky="w", padx=(0, 12))

        ttk.Checkbutton(info_frame, text="Temp range (high/low)", variable=self.show_temp_range).grid(
            row=0, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Checkbutton(info_frame, text="Conditions", variable=self.show_weather).grid(
            row=1, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Checkbutton(info_frame, text="Wind dir + speed", variable=self.show_wind).grid(
            row=2, column=0, sticky="w", padx=8, pady=2
        )

        unit_frame = ttk.LabelFrame(options_frame, text="Temperature Unit")
        unit_frame.grid(row=0, column=2, sticky="w")

        ttk.Radiobutton(unit_frame, text="Fahrenheit (F)", value="F", variable=self.temp_unit_var).grid(
            row=0, column=0, sticky="w", padx=8, pady=2
        )
        ttk.Radiobutton(unit_frame, text="Celsius (C)", value="C", variable=self.temp_unit_var).grid(
            row=1, column=0, sticky="w", padx=8, pady=2
        )

        ttk.Separator(frame).grid(row=3, column=0, columnspan=3, sticky="we", pady=12)

        self.output = tk.Text(frame, height=14, wrap="word")
        self.output.grid(row=4, column=0, columnspan=3, sticky="nsew")
        self.output.configure(state="disabled")

        ttk.Label(frame, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        self.bind("<Return>", lambda event: self.on_fetch())

    def set_output(self, text: str):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def on_fetch(self):
        city = self.city_var.get().strip()

        if city not in CITY_DB:
            self.status_var.set("Pick a city from the list (or type to filter).")
            self.set_output(
                "City not found in preset list.\n\n"
                "Tip: Type to filter, then choose one from the dropdown."
            )
            return

        lat, lon = CITY_DB[city]

        self.status_var.set("Fetching forecast from NWS...")
        self.set_output("Fetching...\n")
        self.update_idletasks()

        try:
            periods = fetch_forecast_periods(lat, lon)
            humidity = fetch_latest_relative_humidity(lat, lon)

            if not periods:
                raise ValueError("No forecast periods returned.")

            target_unit = self.temp_unit_var.get()

            lines = []
            lines.append(f"City: {city}")
            lines.append(f"Coords: {lat:.4f}, {lon:.4f}")
            lines.append("")
            lines.append(format_now(periods[0], humidity, target_unit))

            time_range = self.time_range_var.get().strip()
            if time_range in ("1", "3", "7"):
                days = int(time_range)
                summaries = build_day_summaries(periods)
                lines.append("")
                lines.append(f"Forecast (next {days} day{'s' if days > 1 else ''}):")
                lines.extend(
                    format_days(
                        summaries,
                        days,
                        show_temp_range=self.show_temp_range.get(),
                        show_weather=self.show_weather.get(),
                        show_wind=self.show_wind.get(),
                        target_unit=target_unit,
                    )
                )

            self.set_output("\n".join(lines))
            self.status_var.set("Done")

        except Exception as e:
            self.status_var.set("Error")
            self.set_output(f"Error:\n{e}")


def main():
    WeatherApp().mainloop()


if __name__ == "__main__":
    main()
