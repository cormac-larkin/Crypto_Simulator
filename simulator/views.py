from os import link
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from requests.api import get
import time, random

from simulator.models import ExtendUser, Holdings, Transactions

from .forms import SignUpForm
from .utils import coin_name_dict, get_coin_info, portfolio_coin_prices, price_chart_data

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
    # Determine who the current User is
    user = request.user

    if request.method == "GET":
        # Retrieve the current User's holdings (if any)
        portfolio = Holdings.objects.filter(user = user)

        # If the user has made investments, retrieve them from the database and do the following steps
        if portfolio:
            owned_coins_list = [entry.cryptocurrency for entry in portfolio]
            units_owned = [float(entry.units) for entry in portfolio]

            # Convert the list of owned coins into a comma-separated string, so we can pass it to our "portfolio_coin_prices" function
            coin_ids = ",".join(owned_coins_list)
            coin_info_list = portfolio_coin_prices(coin_ids)

            # The API does not return the information for each coin in the same order as we provided.
            # So we must create a price list which is in the same order as our owned_coins_list
            price_list = []
            for coin_id in owned_coins_list:
                for item in coin_info_list:
                    if item['id'] == coin_id:
                        price_list.append(float(item['price']))


            # Multiply the current market price for each asset owned, by the number of units owned - this gives us the current value of each holding
            holding_values_list = [a*b for a,b in zip(units_owned, price_list)]

            # Next, find the TOTAL profit/loss on the Users account ( Sum of all holdings - (All Buys - All Sells) )
            sum_of_all_buys = Transactions.objects.filter(user = user, transaction_type = 'BUY').aggregate(Sum('value'))
            sum_of_all_sells = Transactions.objects.filter(user = user, transaction_type = 'SELL').aggregate(Sum('value'))

            # This block of code prevents an error when sum_of_all_sells = None. (i.e when the user has not made any sell transactions yet)
            if not sum_of_all_sells["value__sum"]:
                total_spent = sum_of_all_buys["value__sum"]
            else:
                total_spent = (sum_of_all_buys["value__sum"] - sum_of_all_sells["value__sum"])

            combined_holdings_value = sum(holding_values_list)

            # Finally we can calculate the total profit/loss (in Euros and as a percentage)
            total_profit_or_loss = (combined_holdings_value - float(total_spent))
            total_profit_or_loss_percentage = (total_profit_or_loss / float(total_spent)) * 100


            # Next, find the profit/loss made on EACH crypto owned by the User (Sum of each holding - (Individual Buys - Individual Sells))
            sum_of_individual_buys = []
            sum_of_individual_sells = []
            for coin in owned_coins_list:

                # Find value of all buys for each owned coin, and add to 'sum_of_individual_buys 
                x = Transactions.objects.filter(transaction_type = 'BUY', cryptocurrency = coin, user = user).aggregate(Sum('value'))
                sum_of_individual_buys.append(float(x['value__sum']))

                # Find value of all sells for each owned coin, and add to 'sum_of_individual_sells
                y = Transactions.objects.filter(transaction_type = 'SELL', cryptocurrency = coin, user = user).aggregate(Sum('value'))
                # If they have no sells for a coin, set the value to 0 (to avoid errors)
                if not y['value__sum']:
                    y = 0
                    sum_of_individual_sells.append(y)
                else:
                    sum_of_individual_sells.append(float(y['value__sum']))
            
            individual_amounts_spent = [a-b for a,b in zip(sum_of_individual_buys, sum_of_individual_sells)]
            individual_profits_or_losses = [a-b for a,b in zip(holding_values_list, individual_amounts_spent)]
            individual_profit_or_loss_percentages = [(a/b)*100 for a,b in zip(individual_profits_or_losses, individual_amounts_spent)]

            # Finally, combine all this information into a list which we can iterate over in our template
            zipper = zip(owned_coins_list, holding_values_list, individual_profits_or_losses, individual_profit_or_loss_percentages, individual_amounts_spent)
            holdings_info_list = list(zipper)


        # If the user has not made any investments, we must initialise these variables anyway to avoid errors when passing them to template
        elif not portfolio:
            holdings_info_list = ""
            owned_coins_list = ""
            holding_values_list =""
            combined_holdings_value = ""
            total_profit_or_loss_percentage = ""
            total_profit_or_loss = ""
            total_spent = ""

        # Generate random number to populate our portfolio graphs (until better solution found)
        random_number_list = []
        for i in range(100):
            n = random.randint(1,99)
            random_number_list.append(n)

        label_list = []
        for i in range(50):
            label_list.append(i)

    return render(request, "simulator/index.html", {
        "user": user,
        "portfolio": portfolio,
        "owned_coins_list": owned_coins_list,
        "pie_chart_values_list": [int(value) for value in holding_values_list],
        "combined_holdings_value": combined_holdings_value,
        "holdings_info_list": holdings_info_list,
        "total_profit_or_loss": total_profit_or_loss,
        "total_profit_or_loss_percentage": total_profit_or_loss_percentage,
        "total_amount_invested": total_spent,
        "random_number_list": random_number_list,
        "label_list": label_list
    })


@login_required(login_url= "/landing")
def browse(request):

    if request.method == "GET":
        # Get the coin ID for every available coin and pass them into our portfolio_coin_prices function
        all_coins_list = [key for key in coin_name_dict]
        all_coins_string = ",".join(all_coins_list)
        full_coin_info_list = portfolio_coin_prices(all_coins_string)

        return render(request, "simulator/browse.html", {
            "full_coin_info_list": full_coin_info_list
        })


@login_required(login_url= "/landing")
def coin_info(request, coin_id):
    """This view takes a coin_id from the URL and passes it to the 'get_coin_info' function which gets a JSON response from the IEX API.
        The JSON information is passed to the template where specific values such as the current price/volume etc, can be accessed."""

    if request.method == "GET":
        # Retrieving live data from IEX API for the selected currency
        coin_info = get_coin_info(coin_id)

        # Retrieving historic price data from Nomics API (used for rendering charts with chart.js)
        historic_price_data = price_chart_data(coin_id)
        
        # If the coin name is not in the coin name dictionary, use placeholder string instead, to avoid KeyError
        try:
            coin_full_name = coin_name_dict[coin_id.upper()]
        except KeyError:
            coin_full_name = "the selected cryptocurrency"

        # Pass current user's data to template so we can display their account balance
        data = request.user

        return render(request, "simulator/coin_info.html", {
            "coin_id": coin_id.upper(), 
            "coin_info": coin_info, 
            "coin_full_name": coin_full_name,
            "historic_price_data": historic_price_data[0], 
            "historic_price_timestamps": historic_price_data[1],
            "data": data
        })

    elif request.method == "POST":
        # Collect submitted form data
        currency_id = request.POST["currency-id"]
        trade_type = request.POST["trade-type"]
        trade_value = float(request.POST["trade-value"])
        user = request.user

        # Find user's available funds
        user_info = ExtendUser.objects.get(link = user)
        available_funds = float(user_info.cash)

        # Translate the € value of the trade into units of the selected cryptocurrency
        data = portfolio_coin_prices(currency_id)
        live_price = float(data[0]['price'])
        units = (trade_value/live_price)

        if trade_type == "BUY":
            # If user does not have enough funds, raise an error
            if trade_value > available_funds:
                return HttpResponseForbidden("You have insufficient funds to complete this transaction")
            
            # If user has enough funds, deduct the value of the purchase from their funds
            else:
                f = ExtendUser.objects.get(link = user)
                f.cash = (available_funds - trade_value)
                f.save()

            # Next, create a new record in the Transactions model for this purchase

                t = Transactions.objects.create(
                    cryptocurrency = currency_id,
                    transaction_type = trade_type,
                    units = units,
                    value = trade_value,
                    user = user
                )

            # Finally, update the Holdings model. First check if user already holds any of this currency (in order to avoid making duplicate records)
                existing_record = Holdings.objects.filter(
                    cryptocurrency = currency_id,
                    user = user
                ).first()
                
                # If user does not already own this currency, create a new record for this holding
                if not existing_record:
                    new_holding = Holdings.objects.create(
                        cryptocurrency = currency_id,
                        units = units,
                        user = user
                    )
                # If user already owns this currency, simply update the existing record of the holding
                else:
                    existing_record.units = (float(existing_record.units) + units)
                    existing_record.save()

                # Add 1 second delay before redirecting to index page (to avoid hitting Nomics API limit of 1 request per second)
                time.sleep(1)

                return HttpResponseRedirect(reverse("index"))

        elif trade_type == "SELL":
            # First, determine if User owns any of this currency to sell
            already_owned = Holdings.objects.filter(
                cryptocurrency = currency_id,
                user = user
            ).first()

            # If user does not own this currency, raise an error
            if not already_owned:
                return HttpResponseForbidden(f"You cannot sell {currency_id} because you do not own any!")

            # If they do own it, ensure they own at least enough to cover the value of the sale, if not, raise an error
            elif already_owned: 
                if already_owned.units < units:
                    return HttpResponseForbidden(f"You do not own enough {currency_id} to complete this sale")
                
                # If user does own enough of the currency, allow this sale and update their funds balance to reflect it
                else:
                    f = ExtendUser.objects.get(link = user)
                    f.cash = (available_funds + trade_value)
                    f.save()

                    # Next, create a new transactions record for this sale
                    t = Transactions.objects.create(
                        cryptocurrency = currency_id,
                        transaction_type = trade_type,
                        units = units,
                        value = trade_value,
                        user = user
                    )

                    # Finally, update the Holding model to reflect the sale
                    already_owned.units = (float(already_owned.units) - units)
                    already_owned.save()

                    # Add 1 second delay before redirecting to index page (to avoid hitting Nomics API limit of 1 request per second)
                    time.sleep(1)

                    return HttpResponseRedirect(reverse("index"))
        
        else:
            return HttpResponseForbidden("You did not select a valid trade type ('Buy' or 'Sell')")
                







