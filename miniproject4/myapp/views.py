import os
import requests
import matplotlib
import matplotlib.pyplot as plt
from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings
from .forms import HoldingForm
from .models import Holding

API_KEY = settings.ALPHA_VANTAGE_API_KEY
matplotlib.use('Agg')

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def stock_view(request):
    data = None
    error = None
    plot_filename = None
    selected_date = None
    hourly_data = None
    ticker = ""
    available_dates = []

    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper().strip()
        selected_date = request.POST.get("selected_date", "").strip()

        if not ticker:
            error = "Please enter a ticker symbol."
        else:
            try:
                # DAILY DATA
                daily_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}'
                daily_response = requests.get(daily_url)
                daily_response.raise_for_status()
                daily_json = daily_response.json()
                time_series = daily_json.get("Time Series (Daily)")
                if not time_series:
                    error = daily_json.get("Note") or daily_json.get("Error Message") or "No daily data found."
                else:
                    available_dates = sorted(time_series.keys(), reverse=True)[:5]

                    if not selected_date:
                        selected_date = available_dates[0]

                    # Fetch INTRADAY DATA
                    intraday_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=60min&outputsize=full&apikey={API_KEY}'
                    intraday_response = requests.get(intraday_url)
                    intraday_response.raise_for_status()
                    intraday_json = intraday_response.json()
                    intraday_series = intraday_json.get("Time Series (60min)")

                    if not intraday_series:
                        error = intraday_json.get("Note") or intraday_json.get("Error Message") or "No intraday data found."
                    else:
                        # Filter data for the selected date
                        hourly_data = {
                            k: float(v["4. close"])
                            for k, v in intraday_series.items()
                            if k.startswith(selected_date)
                        }

                        if not hourly_data:
                            error = "No hourly data found for the selected date."
                        else:
                            # Sort by time
                            hourly_data = dict(sorted(hourly_data.items()))

                            # Plot
                            times = list(hourly_data.keys())
                            prices = list(hourly_data.values())

                            plt.figure(figsize=(10, 5))
                            plt.plot(times, prices, marker='o', linestyle='-', color='blue')
                            plt.title(f"{ticker} - Hourly Prices on {selected_date}")
                            plt.xlabel("Time")
                            plt.ylabel("Price (USD)")
                            plt.xticks(rotation=45)
                            plt.grid(True)
                            plt.tight_layout()

                            plot_id = str(uuid4())
                            plot_filename = f"{plot_id}.png"
                            plot_path = os.path.join(settings.BASE_DIR, "static", "charts", plot_filename)
                            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
                            plt.savefig(plot_path)
                            plt.close()
            except Exception as e:
                error = f"Data retrieval failed: {e}"

    return render(request, "stock.html", {
        "ticker": ticker,
        "available_dates": available_dates,
        "selected_date": selected_date,
        "plot_filename": plot_filename,
        "hourly_data": hourly_data,
        "error": error,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Holding
import requests


def portfolio_view(request):
    error = None

    if request.method == "POST":
        ticker = request.POST.get("ticker", "").upper()
        shares = request.POST.get("shares")
        purchase_price = request.POST.get("purchase_price")

        if ticker and shares and purchase_price:
            try:
                shares = float(shares)
                purchase_price = float(purchase_price)
                Holding.objects.create(
                    ticker=ticker,
                    shares=shares,
                    purchase_price=purchase_price
                )
                return redirect("portfolio")
            except ValueError:
                error = "Invalid numeric input."
        else:
            error = "All fields are required."

    holdings = Holding.objects.all()
    portfolio = []
    total_value = 0
    total_gain = 0

    for holding in holdings:
        ticker = holding.ticker.upper()

        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}"
            response = requests.get(url)
            data = response.json()
            price_str = data.get("Global Quote", {}).get("05. price")
            price = float(price_str) if price_str else 0
        except Exception as e:
            price = 0
            error = error or f"Could not fetch price for {ticker}"

        current_value = price * holding.shares
        gain = current_value - (holding.purchase_price * holding.shares)

        total_value += current_value
        total_gain += gain

        portfolio.append({
            "id": holding.id,
            "ticker": ticker,
            "shares": holding.shares,
            "purchase_price": holding.purchase_price,
            "current_price": round(price, 2),
            "current_value": round(current_value, 2),
            "gain": round(gain, 2)
        })

    return render(request, "portfolio.html", {
        "portfolio": portfolio,
        "total_value": round(total_value, 2),
        "total_gain": round(total_gain, 2),
        "error": error
    })



