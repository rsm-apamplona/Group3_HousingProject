from shiny import App, ui, render, reactive
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import folium
from htmltools import HTML

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Input Parameters"),
        ui.input_slider("stay_years", "Time Planning to Stay", 
            value=10, min=0.5, max=30, step=0.5,
            post=" years"),
        ui.input_slider("home_price", "Home Price", 
            value=800000, min=500000, max=2000000, step=25000,
            pre="$"),
        ui.input_checkbox("va_loan", "VA Loan", value=False),
        ui.input_slider("down_payment_pct", "Down Payment %", 
            value=20, min=0, max=50, step=1,
            post="%"),
        ui.input_slider("mortgage_rate", "Mortgage Interest Rate", 
            value=6.5, min=1, max=10, step=0.1,
            post="%"),
        ui.input_slider("mortgage_years", "Mortgage Term", 
            value=30, min=15, max=30, step=5,
            post=" years"),
        ui.input_slider("monthly_rent", "Monthly Rent", 
            value=3500, min=1500, max=8000, step=100,
            pre="$"),
        ui.input_slider("rent_increase", "Annual Rent Increase", 
            value=3, min=0, max=15, step=0.5,
            post="%"),
        ui.input_slider("property_tax_rate", "Property Tax Rate", 
            value=1.25, min=0.5, max=10, step=0.1,
            post="%"),
        ui.input_numeric("annual_maintenance", "Annual Maintenance $", 
            value=5000, min=0),
        ui.input_slider("home_appreciation", "Annual Home Appreciation", 
            value=5, min=0, max=10, step=0.5,
            post="%"),
        ui.input_slider("investment_return", "Investment Return", 
            value=7, min=2, max=15, step=0.5,
            post="%"),
        width="350px"
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Rent vs Buy Analysis"),
            ui.output_text("recommendation"),
            ui.output_text("details")
        ),
        ui.card(
            ui.card_header("San Diego Housing Map"),
            ui.output_ui("map"),
            "Interactive map showing different San Diego neighborhoods and their median home prices. Click on markers to see details."
        )
    )
)

def server(input, output, session):
    
    @reactive.effect
    def _():
        if input.va_loan():
            ui.update_slider("down_payment_pct", value=0)
    
    @output
    @render.ui
    def map():
        # Create a map centered on San Diego
        m = folium.Map(location=[32.7157, -117.1611], zoom_start=11)
        
        # Add markers for different neighborhoods with approximate median home prices
        neighborhoods = [
            {"name": "La Jolla", "loc": [32.8328, -117.2713], "price": 1750000, "rent": 4500},
            {"name": "Pacific Beach", "loc": [32.7997, -117.2304], "price": 1200000, "rent": 3200},
            {"name": "Downtown", "loc": [32.7157, -117.1611], "price": 650000, "rent": 2800},
            {"name": "North Park", "loc": [32.7418, -117.1296], "price": 850000, "rent": 2500},
            {"name": "Mission Valley", "loc": [32.7714, -117.1673], "price": 550000, "rent": 2600},
            {"name": "Hillcrest", "loc": [32.7466, -117.1631], "price": 900000, "rent": 2700},
            {"name": "Ocean Beach", "loc": [32.7492, -117.2497], "price": 1100000, "rent": 3000},
            {"name": "Mission Beach", "loc": [32.7842, -117.2527], "price": 1500000, "rent": 3500},
            {"name": "Coronado", "loc": [32.6859, -117.1831], "price": 2000000, "rent": 4800},
            {"name": "Point Loma", "loc": [32.7419, -117.2472], "price": 1300000, "rent": 3300}
        ]
        
        for hood in neighborhoods:
            folium.Marker(
                hood["loc"],
                popup=folium.Popup(
                    f"<b>{hood['name']}</b><br>"
                    f"Median Home Price: ${hood['price']:,}<br>"
                    f"Typical Rent: ${hood['rent']:,}/month",
                    max_width=200
                ),
                tooltip=hood["name"]
            ).add_to(m)
            
        return HTML(m._repr_html_())
    
    @reactive.calc
    def calculate_costs():
        # Home purchase calculations
        down_payment = input.home_price() * (input.down_payment_pct() / 100)
        loan_amount = input.home_price() - down_payment
        monthly_rate = (input.mortgage_rate() / 100) / 12
        num_payments = input.mortgage_years() * 12
        
        monthly_payment = -npf.pmt(monthly_rate, num_payments, loan_amount)
        
        va_funding_fee = 0
        if input.va_loan():
            va_funding_fee = input.home_price() * 0.023
        
        annual_property_tax = input.home_price() * (input.property_tax_rate() / 100)
        annual_maintenance = input.annual_maintenance()
        
        buy_costs = []
        rent_costs = []
        home_value = input.home_price()
        monthly_rent = input.monthly_rent()
        
        total_months = int(input.stay_years() * 12)
        
        for month in range(total_months):
            monthly_property_tax = annual_property_tax / 12
            monthly_maintenance = annual_maintenance / 12
            
            monthly_buy_cost = monthly_payment + monthly_property_tax + monthly_maintenance
            buy_costs.append(monthly_buy_cost)
            
            rent_costs.append(monthly_rent)
            
            if month % 12 == 11:
                home_value *= (1 + input.home_appreciation() / 100)
                annual_property_tax = home_value * (input.property_tax_rate() / 100)
                monthly_rent *= (1 + input.rent_increase() / 100)
        
        discount_rate = input.investment_return() / 100
        monthly_discount_rate = (1 + discount_rate) ** (1/12) - 1
        
        buy_cash_flows = [-down_payment - va_funding_fee] + [-x for x in buy_costs]
        buy_cash_flows.append(home_value * 0.94)
        
        buy_npv = npf.npv(monthly_discount_rate, buy_cash_flows)
        rent_npv = npf.npv(monthly_discount_rate, [-x for x in rent_costs])
        
        return {
            "buy_npv": buy_npv,
            "rent_npv": rent_npv,
            "final_home_value": home_value,
            "va_funding_fee": va_funding_fee
        }

    @output
    @render.text
    def recommendation():
        costs = calculate_costs()
        
        if costs["buy_npv"] < costs["rent_npv"]:
            return " Recommendation: BUYING is financially advantageous in the long term."
        else:
            return " Recommendation: RENTING is financially advantageous in the long term."

    @output
    @render.text
    def details():
        costs = calculate_costs()
        
        va_fee_text = f"\n" VA Funding Fee: ${costs['va_funding_fee']:,.0f}" if input.va_loan() else ""
        
        years = input.stay_years()
        if years >= 1:
            period_text = f"{years:g} year{'s' if years != 1 else ''}"
        else:
            months = int(years * 12)
            period_text = f"{months} month{'s' if months != 1 else ''}"
        
        return (
            f"\n\n=Ê Analysis Details ({period_text} projection):\n"
            f"" Total cost of buying (Present Value): ${-costs['buy_npv']:,.0f}\n"
            f"" Total cost of renting (Present Value): ${-costs['rent_npv']:,.0f}\n"
            f"" Projected home value after {period_text}: ${costs['final_home_value']:,.0f}"
            f"{va_fee_text}\n"
            f"\nNote: This analysis includes mortgage payments, property taxes, maintenance, "
            f"and assumes the input appreciation rates. The comparison accounts for the time "
            f"value of money using the specified investment return rate. The buying scenario "
            f"includes estimated selling costs (6%) at the end of the period."
        )

app = App(app_ui, server)
