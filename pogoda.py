import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
import json
import os

# Цветовые градиенты для фона в зависимости от погоды
weather_gradients = {
    "clear": ("#FFD700", "#FFFFFF"),
    "partly-cloudy": ("#87CEEB", "#FFFFFF"),
    "cloudy": ("#B0C4DE", "#D3D3D3"),
    "rain": ("#4682B4", "#87CEFA"),
    "snow": ("#ADD8E6", "#FFFFFF")
}

# Полезные советы в зависимости от погоды
weather_tips = {
    "clear": "Ясная погода Кристина Александровна! Возьмите солнцезащитные очки.",
    "partly-cloudy": "Переменная облачность Кристина Александровна, на всякий случай захватите легкий зонт.",
    "cloudy": "Облачная погода Кристина Александровна, наденьте теплую кофту, возможен небольшой ветер.",
    "rain": "Дождь Кристина Александровна! Не забудьте зонт и водонепроницаемую обувь.",
    "snow": "Снег Кристина Александровна! Одевайтесь тепло и наденьте нескользящую обувь."
}

# Текстовые иконки для погодных условий
weather_icons = {
    "clear": "☀️",
    "partly-cloudy": "⛅",
    "cloudy": "☁️",
    "rain": "🌧️",
    "snow": "❄️"
}

# Словарь для преобразования номера месяца в название
month_names = {
    "04": "апреля",
    "05": "мая",
    "06": "июня",
    "07": "июля",
    "08": "августа",
    "09": "сентября",
    "10": "октября",
    "11": "ноября",
    "12": "декабря",
    "01": "января",
    "02": "февраля",
    "03": "марта"
}

class BaseWeatherApp(ABC):
    """Abstract base class for weather applications."""
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#1A1A1A")
        self.main_frame = tk.Frame(self.root, bg="#1A1A1A")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    @abstractmethod
    def update_weather(self):
        """Update the weather display."""
        pass

    @abstractmethod
    def set_gradient_background(self, condition):
        """Set the background gradient based on weather condition."""
        pass

class WeatherDataHandler:
    """Class to handle weather data processing."""
    def __init__(self, data_file="weather_data.json"):
        self.data_file = data_file
        self.weather_data = self.load_weather_data()

    def load_weather_data(self):
        """Load weather data from JSON file."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, self.data_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showwarning("Предупреждение", f"Файл данных о погоде '{self.data_file}' не найден. Приложение запустится с пустым набором данных.")
            print(f"Warning: Weather data file '{self.data_file}' not found. Starting with empty dataset.")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", f"Неверный формат JSON в файле '{self.data_file}'. Приложение запустится с пустым набором данных.")
            print(f"Error: Invalid JSON format in '{self.data_file}'. Starting with empty dataset.")
            return {}
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка при загрузке '{self.data_file}': {str(e)}. Приложение запустится с пустым набором данных.")
            print(f"Error: Unknown error loading '{self.data_file}': {str(e)}. Starting with empty dataset.")
            return {}

    def get_current_weather(self, city):
        """Get current weather data for a city."""
        return self.weather_data.get(city, {}).get("current", {"temp": 0, "condition": "cloudy", "wind": 0, "humidity": 0})

    def get_hourly_forecast(self, city):
        """Get hourly forecast data for a city."""
        return self.weather_data.get(city, {}).get("hourly", {})

    def get_daily_forecast(self, city):
        """Get daily forecast data for a city."""
        return self.weather_data.get(city, {}).get("forecast", {})

    def format_date(self, date):
        """Format date string to a readable format."""
        try:
            day, month = date.split('-')[2], date.split('-')[1]
            return f"{int(day)} {month_names[month]}"
        except (IndexError, KeyError):
            return date

class WeatherUIComponent(ABC):
    """Abstract base class for UI components."""
    def __init__(self, parent, bg="#1A1A1A"):
        self.frame = tk.Frame(parent, bg=bg)
        self.frame.pack(fill="both", expand=True)

    def clear_frame(self, frame):
        """Clear all widgets in a given frame."""
        for widget in frame.winfo_children():
            widget.destroy()

    @abstractmethod
    def render(self):
        """Render the UI component."""
        pass

class CityListComponent(WeatherUIComponent):
    """UI component for displaying and selecting cities."""
    def __init__(self, parent, cities, on_select_callback, bg="#1A1A1A"):
        super().__init__(parent, bg)
        self.cities = sorted(cities) if cities else ["Нет данных"]
        self.on_select_callback = on_select_callback
        self.city_labels = []
        self.current_city = self.cities[0]
        self.render()

    def render(self):
        self.clear_frame(self.frame)
        city_canvas = tk.Canvas(self.frame, bg="#1A1A1A", highlightthickness=0, width=150)
        scrollable_frame = tk.Frame(city_canvas, bg="#1A1A1A")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: city_canvas.configure(scrollregion=city_canvas.bbox("all"))
        )

        city_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        city_canvas.bind_all("<MouseWheel>", lambda event: city_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        city_canvas.pack(side="left", fill="both", expand=True)

        for city in self.cities:
            label = tk.Label(
                scrollable_frame,
                text=city,
                font=("Arial", 12),
                fg="white",
                bg="#2C2C2C" if city != self.current_city else "#3B82F6",
                anchor="w",
                padx=10,
                pady=5,
                width=18,
                relief="flat",
                borderwidth=0,
                highlightthickness=0
            )
            label.pack(fill="x", pady=0)
            label.bind("<Button-1>", lambda event, c=city: self.select_city(c))
            label.bind("<Enter>", lambda event, l=label: self.on_enter(l))
            label.bind("<Leave>", lambda event, l=label: self.on_leave(l))
            self.city_labels.append(label)

    def on_enter(self, label):
        if label["bg"] != "#3B82F6":
            label.config(bg="#4A4A4A", fg="white")

    def on_leave(self, label):
        if label["bg"] != "#3B82F6":
            label.config(bg="#2C2C2C", fg="white")

    def select_city(self, city):
        self.current_city = city
        for label in self.city_labels:
            label.config(bg="#3B82F6" if label["text"] == city else "#2C2C2C", fg="white")
        self.on_select_callback(city)

class WeatherDisplayComponent(WeatherUIComponent):
    """UI component for displaying weather information."""
    def __init__(self, parent, data_handler, bg="#1A1A1A"):
        super().__init__(parent, bg)
        self.data_handler = data_handler
        self.city_label = tk.Label(
            self.frame,
            text="",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1A1A1A"
        )
        self.city_label.pack(anchor="w", padx=10, pady=(0, 10))
        self.info_frame = tk.Frame(self.frame, bg="#2C2C2C", bd=0)
        self.info_frame.pack(fill="both", expand=True, pady=10)
        self.hourly_frame = tk.Frame(self.frame, bg="#1A1A1A")
        self.hourly_frame.pack(fill="x", pady=5)
        self.forecast_frame = tk.Frame(self.frame, bg="#1A1A1A")
        self.forecast_frame.pack(fill="x", pady=5)

    def render(self, city):
        self.city_label.config(text=f"ПОГОДА В {city.upper()}")
        self.show_current(city)
        self.show_hourly_forecast(city)
        self.show_14_day_forecast(city)

    def show_current(self, city):
        self.clear_frame(self.info_frame)
        data = self.data_handler.get_current_weather(city)
        condition_icon = weather_icons.get(data['condition'], "⛅")

        main_info = tk.Frame(self.info_frame, bg="#2C2C2C")
        main_info.pack(fill="x", pady=5)

        tk.Label(main_info, text=f"+{data['temp']}° {condition_icon}", font=("Arial", 24, "bold"), fg="white", bg="#2C2C2C").pack(anchor="w", padx=10)
        tk.Label(main_info, text="Пасмурно, в ближайшие 2 часа осадков не ожидается" if city != "Нет данных" else "Данные отсутствуют", font=("Arial", 12), fg="gray", bg="#2C2C2C").pack(anchor="w", padx=10)

        details_frame = tk.Frame(self.info_frame, bg="#2C2C2C")
        details_frame.pack(fill="x", pady=5)
        tk.Label(details_frame, text=f"ОЩУЩАЕТСЯ\n+{data['temp']-1}°" if city != "Нет данных" else "ОЩУЩАЕТСЯ\nН/Д", font=("Arial", 12), fg="white", bg="#2C2C2C").pack(side="left", padx=10)
        tk.Label(details_frame, text=f"ВЕТЕР\n{data['wind']} м/с" if city != "Нет данных" else "ВЕТЕР\nН/Д", font=("Arial", 12), fg="white", bg="#2C2C2C").pack(side="left", padx=10)
        tk.Label(details_frame, text="ДАВЛЕНИЕ\n743 мм рт. ст." if city != "Нет данных" else "ДАВЛЕНИЕ\nН/Д", font=("Arial", 12), fg="white", bg="#2C2C2C").pack(side="left", padx=10)
        tk.Label(details_frame, text=f"ВЛАЖНОСТЬ\n{data['humidity']}%" if city != "Нет данных" else "ВЛАЖНОСТЬ\nН/Д", font=("Arial", 12), fg="white", bg="#2C2C2C").pack(side="left", padx=10)

        tk.Label(self.info_frame, text=weather_tips.get(data['condition'], "Нет данных о погоде"), font=("Arial", 10, "italic"), fg="gray", bg="#2C2C2C").pack(anchor="w", padx=10, pady=5)

    def show_hourly_forecast(self, city):
        self.clear_frame(self.hourly_frame)
        tk.Label(self.hourly_frame, text="Почасовой прогноз", font=("Arial", 14, "bold"), fg="white", bg="#1A1A1A").pack(anchor="w", padx=10, pady=5)
        hourly_data = self.data_handler.get_hourly_forecast(city)
        if not hourly_data:
            tk.Label(self.hourly_frame, text="Нет данных", font=("Arial", 10), fg="gray", bg="#1A1A1A").pack(anchor="w", padx=10)
            return
        scroll_frame = tk.Frame(self.hourly_frame, bg="#1A1A1A")
        scroll_frame.pack(fill="x")
        for time, data in hourly_data.items():
            frame = tk.Frame(scroll_frame, bg="#2C2C2C")
            frame.pack(side="left", padx=5, pady=5)
            tk.Label(frame, text=time, font=("Arial", 10), fg="white", bg="#2C2C2C").pack()
            tk.Label(frame, text=f"{weather_icons.get(data['condition'], '⛅')}", font=("Arial", 18), fg="white", bg="#2C2C2C").pack()
            tk.Label(frame, text=f"+{data['temp']}°", font=("Arial", 10), fg="white", bg="#2C2C2C").pack()
            tk.Label(frame, text=f"Осадки: {data['precipitation']}", font=("Arial", 8), fg="gray", bg="#2C2C2C").pack()

    def show_14_day_forecast(self, city):
        self.clear_frame(self.forecast_frame)
        tk.Label(self.forecast_frame, text="Прогноз на 14 дней", font=("Arial", 14, "bold"), fg="white", bg="#1A1A1A").pack(anchor="w", padx=10, pady=5)
        if city == "Нет данных":
            tk.Label(self.forecast_frame, text="Нет данных", font=("Arial", 10), fg="gray", bg="#1A1A1A").pack(anchor="w", padx=10)
            return
        dates = [
            "2025-04-15", "2025-04-16", "2025-04-17", "2025-04-18", "2025-04-19", 
            "2025-04-20", "2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24",
            "2025-04-25", "2025-04-26", "2025-04-27", "2025-04-28"
        ]
        temps = [16, 14, 12, 10, 13, 15, 17, 11, 13, 18, 19, 16, 14, 12]
        conditions = [
            "clear", "cloudy", "rain", "snow", "partly-cloudy", 
            "clear", "clear", "cloudy", "partly-cloudy", "clear",
            "rain", "snow", "partly-cloudy", "cloudy"
        ]
        for i, date in enumerate(dates):
            try:
                formatted_date = self.data_handler.format_date(date)
                frame = tk.Frame(self.forecast_frame, bg="#2C2C2C")
                frame.pack(fill="x", pady=2)
                tk.Label(frame, text=formatted_date, font=("Arial", 10), fg="white", bg="#2C2C2C").pack(side="left", padx=10)
                tk.Label(frame, text=weather_icons.get(conditions[i], "⛅"), font=("Arial", 16), fg="white", bg="#2C2C2C").pack(side="left", padx=10)
                tk.Label(frame, text=f"+{temps[i]}°", font=("Arial", 10), fg="white", bg="#2C2C2C").pack(side="right", padx=10)
            except Exception as e:
                print(f"Error rendering forecast for date {date}: {str(e)}")
                continue

class WeatherApp(BaseWeatherApp):
    """Main weather application class."""
    def __init__(self, root):
        super().__init__(root)
        self.root.title("Погода")
        self.root.geometry("900x600")
        try:
            self.data_handler = WeatherDataHandler()
            self.current_city = sorted(self.data_handler.weather_data.keys())[0] if self.data_handler.weather_data else "Нет данных"
            self.setup_styles()
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Не удалось инициализировать приложение: {str(e)}")
            print(f"Critical error initializing app: {str(e)}")
            self.root.destroy()

    def setup_styles(self):
        """Configure UI styles."""
        try:
            style = ttk.Style()
            style.configure("Modern.TButton", 
                            background="#2C2C2C", 
                            foreground="white", 
                            font=("Arial", 10, "bold"),
                            borderwidth=0,
                            padding=8,
                            relief="flat")
            style.map("Modern.TButton",
                      background=[("active", "#3C3C3C"), ("!active", "#2C2C2C")])
        except Exception as e:
            print(f"Error setting up styles: {str(e)}")

    def setup_ui(self):
        """Set up the main UI components."""
        try:
            self.city_frame = tk.Frame(self.main_frame, bg="#1A1A1A")
            self.city_frame.pack(side="left", fill="y", padx=(0, 10))
            self.weather_frame = tk.Frame(self.main_frame, bg="#1A1A1A")
            self.weather_frame.pack(side="left", fill="both", expand=True)

            self.city_list = CityListComponent(self.city_frame, self.data_handler.weather_data.keys(), self.select_city)
            self.weather_display = WeatherDisplayComponent(self.weather_frame, self.data_handler)

            self.update_weather()
        except Exception as e:
            messagebox.showerror("Ошибка UI", f"Ошибка настройки интерфейса: {str(e)}")
            print(f"Error setting up UI: {str(e)}")

    def select_city(self, city):
        """Handle city selection."""
        try:
            self.current_city = city
            self.update_weather()
        except Exception as e:
            print(f"Error selecting city {city}: {str(e)}")

    def set_gradient_background(self, condition):
        """Set the background gradient based on weather condition."""
        try:
            start_color, _ = weather_gradients.get(condition, ("#87CEEB", "#FFFFFF"))
            self.main_frame.config(bg=start_color)
        except Exception as e:
            print(f"Error setting gradient background: {str(e)}")
            self.main_frame.config(bg="#87CEEB")

    def update_weather(self):
        """Update the weather display for the current city."""
        try:
            self.set_gradient_background(self.data_handler.get_current_weather(self.current_city)["condition"])
            self.weather_display.render(self.current_city)
        except Exception as e:
            messagebox.showerror("Ошибка обновления", f"Ошибка обновления погоды: {str(e)}")
            print(f"Error updating weather: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WeatherApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Critical error starting application: {str(e)}")