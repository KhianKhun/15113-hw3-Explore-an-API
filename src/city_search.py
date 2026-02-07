import tkinter as tk


class CitySearchController:
    def __init__(self, city_combo, suggest_list, city_var, all_cities):
        self.city_combo = city_combo
        self.suggest_list = suggest_list
        self.city_var = city_var
        self.all_cities = all_cities

    def bind(self, status_callback=None):
        self.city_combo.bind("<KeyRelease>", self.on_keyrelease_filter)
        if status_callback is not None:
            self.city_combo.bind(
                "<<ComboboxSelected>>",
                lambda e: status_callback("Ready"),
            )
        self.city_combo.bind("<Down>", self.on_down)
        self.city_combo.bind("<Up>", self.on_up)
        self.city_combo.bind("<Return>", self.on_combo_return)
        self.city_combo.bind("<Escape>", self.on_escape)
        self.suggest_list.bind("<ButtonRelease-1>", self.on_list_click)

    def _hide_suggestions(self):
        self.suggest_list.grid_remove()
        self.suggest_list.selection_clear(0, tk.END)

    def _show_suggestions(self, items):
        self.suggest_list.delete(0, tk.END)
        for item in items:
            self.suggest_list.insert(tk.END, item)
        height = min(6, len(items))
        self.suggest_list.configure(height=height)
        self.suggest_list.grid()
        if items:
            self.suggest_list.selection_set(0)
            self.suggest_list.activate(0)

    def _restore_entry_focus(self):
        self.city_combo.focus_set()
        self.city_combo.selection_clear()
        self.city_combo.icursor(tk.END)

    def on_keyrelease_filter(self, event):
        typed = self.city_var.get().strip().lower()

        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Tab"):
            return

        if not typed:
            self.city_combo["values"] = self.all_cities
            self._hide_suggestions()
            return

        filtered = [c for c in self.all_cities if typed in c.lower()]

        if not filtered:
            self._hide_suggestions()
            return

        self.city_combo["values"] = filtered
        self.city_combo.after_idle(self._restore_entry_focus)
        self._show_suggestions(filtered)

    def on_down(self, event):
        if not self.suggest_list.winfo_ismapped():
            return
        cur = self.suggest_list.curselection()
        index = 0 if not cur else min(cur[0] + 1, self.suggest_list.size() - 1)
        self.suggest_list.selection_clear(0, tk.END)
        self.suggest_list.selection_set(index)
        self.suggest_list.activate(index)
        return "break"

    def on_up(self, event):
        if not self.suggest_list.winfo_ismapped():
            return
        cur = self.suggest_list.curselection()
        index = 0 if not cur else max(cur[0] - 1, 0)
        self.suggest_list.selection_clear(0, tk.END)
        self.suggest_list.selection_set(index)
        self.suggest_list.activate(index)
        return "break"

    def on_combo_return(self, event):
        if not self.suggest_list.winfo_ismapped():
            return
        cur = self.suggest_list.curselection()
        if not cur:
            return "break"
        choice = self.suggest_list.get(cur[0])
        self.city_var.set(choice)
        self._hide_suggestions()
        self._restore_entry_focus()
        return "break"

    def on_escape(self, event):
        self._hide_suggestions()
        return "break"

    def on_list_click(self, event):
        if not self.suggest_list.curselection():
            return
        choice = self.suggest_list.get(self.suggest_list.curselection()[0])
        self.city_var.set(choice)
        self._hide_suggestions()
        self._restore_entry_focus()
