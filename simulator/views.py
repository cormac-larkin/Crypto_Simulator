from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse

from simulator.models import ExtendUser

from .forms import SignUpForm
from .utils import get_coin_info, price_chart_data

# Create your views here.

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "simulator/register.html", {
                "message": "Passwords must match.", 
                "form": SignUpForm
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "simulator/register.html", {
                "message": "Username already taken.",
                "form": SignUpForm
            })
        login(request, user)

        # After new user is created and logged in, create an instance of 'ExtendUser' linked to the new User. This will give automatically them 10k cash.
        add_cash = ExtendUser(link = User.objects.get(username=request.user))
        add_cash.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "simulator/register.html", {
            "form": SignUpForm
        })


def login_view(request):    
    if request.method == "POST":
         # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "simulator/login.html", {
                "message": "Invalid username and/or password.", 
                "form": SignUpForm
            })
    else:
        return render(request, "simulator/login.html", {
            "form": SignUpForm
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def landing(request):
    return render(request, "simulator/landing.html")


@login_required(login_url= "/landing")
def index(request):
    return render(request, "simulator/index.html")


@login_required(login_url= "/landing")
def browse(request):

    if request.method == "GET":
        return render(request, "simulator/browse.html")


@login_required(login_url= "/landing")
def coin_info(request, coin_id):
    """This view takes a coin_id from the URL and passes it to the 'get_coin_info' function which gets a JSON response from the IEX API.
        The JSON information is passed to the template where specific values such as the current price can be accessed."""

    if request.method == "GET":

        # Retrieving live price data from IEX API for the selected currency
        coin_info = get_coin_info(coin_id)

        # Retrieving historic price data from Nomics API (used for rendering charts with chart.js)
        historic_price_data = price_chart_data(coin_id)

        # The API doesn't provide the full coin name in its response, so I created a dictionary where the full names can be accessed and passed to template.
        coin_name_dict = {
            "BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple", "ADA": "Cardano", 
            "LTC": "Litecoin", "BCH": "Bitcoin Cash", "DOGE": "Dogecoin", "XLM": "Stellar",
            "BNB": "Binance Coin", "SXP": "Swipe", "LINK": "Chainlink", "DOT": "Polkadot",
            "YFI": "Yearn.finance", "GRT": "The Graph", "EOS": "Eos", "EGLD": "Elrond",
            "AVAX": "Avalanche", "UNI": "Uniswap", "CHZ": "Chiliz", "ENJ": "Enjin Coin",
            "MATIC": "Polygon", "LUNA": "Terra", "THETA": "Theta", "BTT": "BitTorrent",
            "WIN": "WinKlink", "VET": "VeChain", "WRX": "WazirX", "TRX": "TRON", "SHIB": "Shiba Inu",
            "ETC": "Ethereum Classic", "SOL": "Solana", "ICP": "Internet Computer", "RUNE": "THORChain",
            "LAZIO": "Lazio Fan Token"
            }
        
        # If the coin name is not in the dictionary, use placeholder string instead, to avoid KeyError
        try:
            coin_full_name = coin_name_dict[coin_id.upper()]
        except KeyError:
            coin_full_name = "the selected cryptocurrency"

        data = request.user

        return render(request, "simulator/coin_info.html", {
            "coin_id": coin_id.upper(), 
            "coin_info": coin_info, 
            "coin_full_name": coin_full_name,
            "historic_price_data": historic_price_data[0], 
            "historic_price_timestamps": historic_price_data[1],
            "data": data
        })