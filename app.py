import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg'
import matplotlib.pyplot as plt
import io
import base64
import requests
from flask import Flask, render_template, request
from matplotlib.figure import Figure
from datetime import datetime
import random
import locale

app = Flask(__name__)

# Set locale for number formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def format_currency(value):
    """Format number with thousand separators and 2 decimal places"""
    return locale.format_string("%.2f", value, grouping=True)

def format_percentage(value):
    """Format percentage with 2 decimal places"""
    return locale.format_string("%.2f", value, grouping=True)

# Function to fetch the current USD to COP exchange rate
def get_exchange_rate():
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()
        return data['rates']['COP']
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

# Helper function to generate the seasonal trends graph
def generate_seasonal_trends_graph():
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    occupancy_rates = [0.55, 0.50, 0.60, 0.65, 0.70, 0.75, 0.80, 0.78, 0.70, 0.65, 0.60, 0.58]
    nightly_prices = [50, 45, 55, 60, 65, 70, 80, 78, 70, 65, 60, 55]

    # Create the plot
    fig, ax1 = plt.subplots()

    # Plot occupancy rates
    color = 'tab:blue'
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Occupancy Rate', color=color)
    ax1.plot(months, occupancy_rates, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot nightly prices on a secondary y-axis
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Nightly Price (USD)', color=color)
    ax2.plot(months, nightly_prices, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    # Format y-axis with thousand separators
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_percentage(x * 100)))
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))

    # Adjust layout
    fig.tight_layout()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the image to base64
    graph_url = base64.b64encode(img.getbuffer()).decode('ascii')

    # Close the plot to free up memory
    plt.close(fig)

    return graph_url

@app.route("/", methods=["GET", "POST"])
def index():
    exchange_rate = get_exchange_rate()

    # Generate the seasonal trends graph
    seasonal_trends_graph = generate_seasonal_trends_graph()

    if request.method == "POST":
        # Get form data
        purchase_price = float(request.form["purchase_price"])
        nightly_rate = float(request.form.get("nightly_rate", 35))
        occupancy_rate = float(request.form.get("occupancy_rate", 0.47))
        monthly_expenses = float(request.form["monthly_expenses"])
        exchange_rate = float(request.form.get("exchange_rate", exchange_rate))
        
        # Calculations
        days_in_month = 30
        monthly_income = nightly_rate * days_in_month * (occupancy_rate / 100)
        monthly_profit = monthly_income - monthly_expenses
        annual_profit = monthly_profit * 12
        roi = (annual_profit / purchase_price) * 100

        # Format numbers with thousand separators
        monthly_income_formatted = format_currency(monthly_income)
        monthly_profit_formatted = format_currency(monthly_profit)
        annual_profit_formatted = format_currency(annual_profit)
        roi_formatted = format_percentage(roi)
        exchange_rate_formatted = format_currency(exchange_rate)

        # Convert USD values to COP using the exchange rate
        monthly_income_cop = monthly_income * exchange_rate
        monthly_profit_cop = monthly_profit * exchange_rate
        annual_profit_cop = annual_profit * exchange_rate

        # Format COP values with thousand separators
        monthly_income_cop_formatted = format_currency(monthly_income_cop)
        monthly_profit_cop_formatted = format_currency(monthly_profit_cop)
        annual_profit_cop_formatted = format_currency(annual_profit_cop)

        # Generate graphs
        monthly_profit_trend = generate_monthly_profit_trend(monthly_profit)
        roi_over_time = generate_roi_over_time(roi, purchase_price, annual_profit)
        break_even_analysis = generate_break_even_analysis(purchase_price, monthly_profit)
        occupancy_vs_profit = generate_occupancy_vs_profit(occupancy_rate, monthly_profit)    
        
        # Return results to the template
        return render_template("results.html", 
                            monthly_income=monthly_income_formatted,
                            monthly_income_cop=monthly_income_cop_formatted,
                            monthly_profit=monthly_profit_formatted,
                            monthly_profit_cop=monthly_profit_cop_formatted,
                            annual_profit=annual_profit_formatted,
                            annual_profit_cop=annual_profit_cop_formatted,
                            roi=roi_formatted,
                            exchange_rate=exchange_rate_formatted,
                            monthly_profit_trend=monthly_profit_trend,
                            roi_over_time=roi_over_time,
                            break_even_analysis=break_even_analysis,
                            occupancy_vs_profit=occupancy_vs_profit,
                            seasonal_trends_graph=seasonal_trends_graph)

    # Pass the seasonal trends graph to the index template
    return render_template("index.html", 
                        exchange_rate=exchange_rate,
                        seasonal_trends_graph=seasonal_trends_graph)

def generate_monthly_profit_trend(monthly_profit):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    profits = [monthly_profit * (1 + random.uniform(-0.1, 0.1)) for _ in months]

    fig = Figure()
    ax = fig.subplots()
    ax.plot(months, profits, marker='o')
    ax.set_title('Monthly Profit Trend')
    ax.set_xlabel('Month')
    ax.set_ylabel('Profit (USD)')
    
    # Format y-axis with thousand separators
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

def generate_roi_over_time(roi, purchase_price, annual_profit):
    years = [1, 2, 3, 4, 5]
    rois = [roi * (1 + random.uniform(-0.05, 0.05)) * year for year in years]

    fig = Figure()
    ax = fig.subplots()
    ax.plot(years, rois, marker='o')
    ax.set_title('ROI Over Time')
    ax.set_xlabel('Year')
    ax.set_ylabel('ROI (%)')
    
    # Format y-axis with thousand separators
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_percentage(x)))

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

def generate_break_even_analysis(purchase_price, monthly_profit):
    months_to_break_even = int(purchase_price / monthly_profit)
    months = list(range(1, months_to_break_even + 1))
    cumulative_profit = [monthly_profit * month for month in months]

    fig = Figure()
    ax = fig.subplots()
    ax.bar(months, cumulative_profit)
    ax.set_title('Break-even Analysis')
    ax.set_xlabel('Month')
    ax.set_ylabel('Cumulative Profit (USD)')
    
    # Format y-axis with thousand separators
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

def generate_occupancy_vs_profit(occupancy_rate, monthly_profit):
    occupancy_rates = [occupancy_rate * (1 + random.uniform(-0.1, 0.1)) for _ in range(12)]
    profits = [monthly_profit * (1 + random.uniform(-0.1, 0.1)) for _ in range(12)]

    fig = Figure()
    ax = fig.subplots()
    ax.scatter(occupancy_rates, profits)
    ax.set_title('Occupancy vs. Profit')
    ax.set_xlabel('Occupancy Rate')
    ax.set_ylabel('Profit (USD)')
    
    # Format axes with thousand separators
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_percentage(x * 100)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

if __name__ == "__main__":
    app.run(debug=True)