import tkinter as tk
from tkinter import ttk

from .weather import get_weather_by_latlon
from .cities import CITY_DB, ALL_CITIES
from .city_search import CitySearchController


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NWS Weather Lookup (Preset Cities)")
        self.geometry("600x320")
        self.resizable(False, False)

        self.city_var = tk.StringVar(value=ALL_CITIES[0])
        self.status_var = tk.StringVar(value="Ready")

        frame = ttk.Frame(self, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="City:").grid(row=0, column=0, sticky="w")

        self.city_combo = ttk.Combobox(
            frame,
            textvariable=self.city_var,
            values=ALL_CITIES,
            width=45
        )
        self.city_combo.grid(row=0, column=1, sticky="we", padx=(8, 8))
        self.city_combo.focus_set()

        self.suggest_list = tk.Listbox(frame, height=0)
        self.suggest_list.grid(row=1, column=1, sticky="we", padx=(8, 8))
        self.suggest_list.grid_remove()

        self.fetch_btn = ttk.Button(frame, text="Fetch", command=self.on_fetch)
        self.fetch_btn.grid(row=0, column=2, sticky="e")

        frame.columnconfigure(1, weight=1)

        ttk.Separator(frame).grid(row=2, column=0, columnspan=3, sticky="we", pady=12)

        self.output = tk.Text(frame, height=11, wrap="word")
        self.output.grid(row=3, column=0, columnspan=3, sticky="nsew")
        self.output.configure(state="disabled")

        ttk.Label(frame, textvariable=self.status_var).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(8, 0)
        )

        # --- 打字搜索：绑定键盘事件，�?trace 更可�?---
        self.city_search = CitySearchController(
            self.city_combo,
            self.suggest_list,
            self.city_var,
            ALL_CITIES,
        )
        self.city_search.bind(status_callback=self.status_var.set)
        # Enter 触发查询
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
            info = get_weather_by_latlon(lat, lon)

            now_line = f'{info["now_label"]}: {info["now_temp"]}°{info["now_unit"]} �?{info["now_short"]}'

            if info["tomorrow_label"] is None:
                tom_line = "Tomorrow: (could not find tomorrow forecast periods)"
            else:
                low = info["tomorrow_low"]
                high = info["tomorrow_high"]
                unit = info["unit"]
                if low is None:
                    tom_line = f'{info["tomorrow_label"]}: {high}°{unit}'
                else:
                    tom_line = f'{info["tomorrow_label"]} range: Low {low}°{unit} / High {high}°{unit}'

            out = (
                f"City: {city}\n"
                f"Coords: {lat:.4f}, {lon:.4f}\n\n"
                f"{now_line}\n"
                f"{tom_line}\n"
            )
            self.set_output(out)
            self.status_var.set("Done")

        except Exception as e:
            self.status_var.set("Error")
            self.set_output(f"Error:\n{e}")


def main():
    WeatherApp().mainloop()


if __name__ == "__main__":
    main()


