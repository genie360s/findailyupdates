"""Dashboard blueprint — all authenticated financial instrument views."""
import os
import requests
from flask import Blueprint, flash, g, redirect, render_template, url_for, request
from requests.exceptions import Timeout, RequestException
from flaskr.auth import login_required
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

BASE_API_URL = os.getenv("BASE_API_URL", "http://127.0.0.1:5000/api/v1/")

BANK_OPTIONS = [
    ("amana_bank",                  "Amana Bank"),
    ("azania_bank",                 "Azania Bank"),
    ("baroda_bank",                 "Bank of Baroda"),
    ("bank_of_india",               "Bank of India (BOI)"),
    ("bank_of_tanzania",            "Bank of Tanzania (BOT)"),
    ("dasheng_bank",                "Dasheng Bank"),
    ("tanzania_commercial_bank",    "Tanzania Commercial Bank (TCB)"),
    ("dcb_bank",                    "DCB Commercial Bank"),
    ("habib_africa_bank",           "Habib African Bank"),
    ("mkombozi_bank",               "Mkombozi Bank"),
    ("national_microfinance_bank",  "National Microfinance Bank (NMB)"),
]

FUND_OPTIONS = [
    ("uttamis_unit_prices", "UTTAMIS Fund"),
    ("faida_fund",          "Faida Fund"),
]

BOND_OPTIONS = [
    ("government_bonds", "Government Bonds"),
    ("corporate_bonds",  "Corporate Bonds"),
]

STOCK_OPTIONS = [
    ("dse", "Dar es Salaam Stock Exchange (DSE)"),
]


def fetch_api_data(url: str, timeout: int = 10):
    """Fetch JSON from a URL. Returns (data, error_message)."""
    try:
        response = requests.get(url, timeout=timeout, verify=False)
        if response.status_code == 200:
            return response.json(), None
        return None, f"API returned status {response.status_code}."
    except Timeout:
        return None, "Request timed out — please try again."
    except RequestException as exc:
        return None, f"Could not reach the API server: {exc}"


# ---------------------------------------------------------------------------
# Main overview / daily summary
# ---------------------------------------------------------------------------

@bp.route('/')
@bp.route('/overview')
@login_required
def overview():
    """Daily market summary — landing page for authenticated users."""
    best_rates, forex_error = None, None
    best_rates_url = os.getenv("BEST_BANKS_FOREX_RATES_TZ_API_URL")
    if best_rates_url:
        best_rates, forex_error = fetch_api_data(best_rates_url)

    return render_template(
        'dashboard/overview.html',
        best_rates=best_rates,
        forex_error=forex_error,
        bank_options=BANK_OPTIONS,
        fund_options=FUND_OPTIONS,
        bond_options=BOND_OPTIONS,
        stock_options=STOCK_OPTIONS,
    )


# ---------------------------------------------------------------------------
# Forex rates
# ---------------------------------------------------------------------------

@bp.route('/forex', methods=['GET', 'POST'])
@login_required
def forex():
    bank_forex_data, selected_bank, error = None, None, None

    if request.method == 'POST':
        selected_bank = request.form.get('bank_name', '').strip()
        if not selected_bank:
            error = 'Please select a bank.'
        else:
            url = f"{BASE_API_URL}{selected_bank}/latest_date"
            bank_forex_data, error = fetch_api_data(url)

    return render_template(
        'dashboard/forex.html',
        bank_forex_data=bank_forex_data,
        selected_bank=selected_bank,
        bank_options=BANK_OPTIONS,
        error=error,
    )


# ---------------------------------------------------------------------------
# Stock markets
# ---------------------------------------------------------------------------

@bp.route('/stocks', methods=['GET', 'POST'])
@login_required
def stocks():
    stock_data, error = None, None

    if request.method == 'POST':
        market = request.form.get('stock_market', '').strip()
        if not market:
            error = 'Please select a market.'
        elif market == 'dse':
            dse_url = os.getenv("DSE_STOCK_PRICES_API_URL", "")
            raw, error = fetch_api_data(dse_url)
            if raw:
                stock_data = raw.get('data', raw)

    return render_template(
        'dashboard/stocks.html',
        stock_data=stock_data,
        stock_options=STOCK_OPTIONS,
        error=error,
    )


# ---------------------------------------------------------------------------
# Bonds
# ---------------------------------------------------------------------------

@bp.route('/bonds', methods=['GET', 'POST'])
@login_required
def bonds():
    bond_data, selected_bond, error = None, None, None

    if request.method == 'POST':
        selected_bond = request.form.get('bond_type', '').strip()
        if not selected_bond:
            error = 'Please select a bond type.'
        else:
            url = f"{BASE_API_URL}{selected_bond}/latest_date"
            bond_data, error = fetch_api_data(url)

    return render_template(
        'dashboard/bonds.html',
        bond_data=bond_data,
        selected_bond=selected_bond,
        bond_options=BOND_OPTIONS,
        error=error,
    )


# ---------------------------------------------------------------------------
# Mutual funds
# ---------------------------------------------------------------------------

@bp.route('/mutual-funds', methods=['GET', 'POST'])
@login_required
def mutual_funds():
    fund_data, selected_fund, error = None, None, None

    if request.method == 'POST':
        selected_fund = request.form.get('fund_name', '').strip()
        if not selected_fund:
            error = 'Please select a fund.'
        else:
            url = f"{BASE_API_URL}{selected_fund}/latest_date"
            fund_data, error = fetch_api_data(url)

    return render_template(
        'dashboard/mutual_funds.html',
        fund_data=fund_data,
        selected_fund=selected_fund,
        fund_options=FUND_OPTIONS,
        error=error,
    )


# ---------------------------------------------------------------------------
# Best rates & summary
# ---------------------------------------------------------------------------

@bp.route('/best-rates')
@login_required
def best_rates():
    url = os.getenv("BEST_BANKS_FOREX_RATES_TZ_API_URL", "")
    data, error = fetch_api_data(url)
    return render_template('dashboard/best_rates.html', best_banks_forex_rates=data, error=error)


@bp.route('/rates-summary')
@login_required
def rates_summary():
    url = os.getenv("BEST_BANKS_FOREX_RATES_SUMMARY_TZ_API_URL", "")
    data, error = fetch_api_data(url)
    return render_template('dashboard/rates_summary.html', summary_best_rates=data, error=error)


# ---------------------------------------------------------------------------
# Backward-compatibility redirects for old URL patterns
# ---------------------------------------------------------------------------

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return redirect(url_for('dashboard.forex'))


@bp.route('/mutual_funds', methods=['GET', 'POST'])
@login_required
def mutual_funds_legacy():
    return redirect(url_for('dashboard.mutual_funds'))


@bp.route('/stock_markets', methods=['GET', 'POST'])
@login_required
def stock_markets():
    return redirect(url_for('dashboard.stocks'))


@bp.route('/best_banks_forex_rates_tz')
@login_required
def best_banks_forex_rates_tz():
    return redirect(url_for('dashboard.best_rates'))


@bp.route('/best_banks_forex_rates_summary')
@login_required
def banks_summary_forex_rates_tz():
    return redirect(url_for('dashboard.rates_summary'))
