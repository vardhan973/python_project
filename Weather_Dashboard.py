import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

class WeatherDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        self.tracked_cities = []
        self.weather_data = {}
        self.session = requests.Session()

    def get_weather(self, city_name, units='metric'):
        """Fetch current weather with caching"""
        if city_name in self.weather_data:
            return self.weather_data[city_name]

        url = f"{self.base_url}weather?q={city_name}&appid={self.api_key}&units={units}"
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.weather_data[city_name] = data
                if city_name not in self.tracked_cities:
                    self.tracked_cities.append(city_name)
                return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {city_name}: {str(e)}")
        return None

    def get_forecast(self, city_name, days=5, units='metric'):
        """Fetch forecast data with caching"""
        cache_key = f"{city_name}_forecast"
        if cache_key in self.weather_data:
            return self.weather_data[cache_key]

        url = f"{self.base_url}forecast?q={city_name}&appid={self.api_key}&units={units}&cnt={days * 8}"
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.weather_data[cache_key] = data
                return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast for {city_name}: {str(e)}")
        return None

    def display_current_weather(self, city_name):
        """Prints current weather data"""
        data = self.get_weather(city_name)
        if not data:
            return

        print(f"\n🌦 Current Weather in {data['name']}:")
        print(f"🌡 Temperature: {data['main']['temp']}°C")
        print(f"💧 Humidity: {data['main']['humidity']}%")
        print(f"☁ Conditions: {data['weather'][0]['description'].capitalize()}")

    def plot_temperature_comparison(self):
        """Plots a bar chart comparing city temperatures"""
        if not self.tracked_cities:
            print("No cities to compare. Add cities first.")
            return

        cities = []
        temps = []

        for city in self.tracked_cities[:5]:
            data = self.get_weather(city)
            if data:
                cities.append(city)
                temps.append(data['main']['temp'])

        if not cities:
            return

        plt.figure(figsize=(10, 5))
        sns.barplot(x=cities, y=temps)
        plt.title('Temperature Comparison')
        plt.ylabel('Temperature (°C)')
        plt.tight_layout()
        plt.show()

    def plot_forecast_trend(self, city_name):
        """Plots a 3-day temperature trend"""
        data = self.get_forecast(city_name, days=3)
        if not data:
            return

        sampled_data = data['list'][::3]

        df = pd.DataFrame([{
            'Time': datetime.fromtimestamp(item['dt']),
            'Temperature': item['main']['temp'],
            'Humidity': item['main']['humidity'],
            'Conditions': item['weather'][0]['description']
        } for item in sampled_data])

        fig = px.line(df, x='Time', y='Temperature',
                      title=f'3-Day Forecast for {city_name}',
                      hover_data=['Conditions', 'Humidity'])
        fig.update_layout(
            xaxis_title='Date/Time',
            yaxis_title='Temperature (°C)',
            height=400
        )
        fig.show()


def main():
    API_KEY = "256e4fa4236c0b50e13043fda68d41a5"  # Replace with your real API key
    dashboard = WeatherDashboard(API_KEY)

    while True:
        print("\n" + "=" * 30)
        print("🌤 WEATHER DASHBOARD")
        print("=" * 30)
        print("1. Check current weather")
        print("2. Compare city temperatures")
        print("3. View 3-day forecast")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if c4hoice == "1":
            city = input("Enter city name: ").strip()
            if city:
                dashboard.display_current_weather(city)

        elif choice == "2":
            if len(dashboard.tracked_cities) < 2:
                print("Need at least 2 cities for comparison")
            else:
                dashboard.plot_temperature_comparison()

        elif choice == "3":
            city = input("Enter city name: ").strip()
            if city:
                dashboard.plot_forecast_trend(city)

        elif choice == "4":
            print("Goodbye! 👋")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
