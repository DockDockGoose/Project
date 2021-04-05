from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from transactions.models import Transaction
from accounts.models import Account
from frontEndStocks.models import FrontEndStock
from prevPrices.models import PrevPrices
import datetime


def index(request):
    return render(request, "home.html", {})

def viewStocks(request):
    stock_list = FrontEndStock.objects.all()
    myAccount = Account.objects.filter(username="daniel")
    context = {
        'stock_list': stock_list,
        'account': myAccount[0]
    }
    return render(request, 'viewAllStocks.html', context)

def viewTransactions(request):
    transaction_list = Transaction.objects.order_by('transactionNum')
    '''output = ', '.join([t.stockSymbol for t in transaction_list])
    return HttpResponse(output)'''
    #template = loader.get_template('./templates/transactions.html')
    context = {
        'transaction_list': transaction_list,
    }
    return render(request, 'transactions.html', context)

def viewMyTransactions(request):
    transaction_list = Transaction.objects.filter(username="daniel")
    myAccount = Account.objects.filter(username="daniel").first()
    
    print(myAccount.stocks)
    context = {
        'transaction_list': transaction_list,
        'account': myAccount
    }
    return render(request, 'transactions.html', context)

def viewIndividualTransaction(request, transactionNu):
    transaction_list = Transaction.objects.filter(transactionNum=transactionNu)
    print(transaction_list)
    context = {
        'transactionNum': transactionNu
    }
    return render(request, 'viewIndividualTransaction.html', context)

def purchaseStockView(request, stockId):
    stock_list = FrontEndStock.objects.filter(id=stockId)
    context = {
        "stock": stock_list[0],
    }
    return render(request, 'purchaseStock.html', context)

def past_prices_chart(request, stockId):
    stock_list = FrontEndStock.objects.filter(id=stockId)
    prevPrices = PrevPrices.objects.filter(stockSymbol=stock_list[0].stockSymbol)
    data = []
    
    labels = []
    for p in prevPrices:
        data.append(p.price)
        labels.append(p.quoteServerTime)

    time = datetime.datetime.now()
    
    data.append(stock_list[0].price)
    labels.append(time.strftime("%H:%M:%S"))

    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })

def confirmPurchaseStock(request):

    user = Account.objects.get(username=request.POST["user"])

    if(user.stocks == None):
        user.stocks = []
    stockBought = request.POST["stockSymbol"]

    s = Stock(stockSymbol=stockBought, price=500.0, quoteServerTime=0, sharesAmount=10000)
    s.save()


    context = {
        'user': request.POST["user"],
        'stockSymbol': stockBought,
        'amount': request.POST["amount"]
    }
    t = Transaction(
        type="buy",
        timestamp= 0,
        server= "localhost:8000",
        transactionNum= 5,
        command= "buy",
        username= request.POST["user"],
        stockSymbol= stockBought,
        fileName= "",
        action= "buy",
        amount= request.POST["amount"],
        price= 500,
        quoteServerTime= 0,
        cryptoKey= "",
        systemEvent= "",
        errorEvent= "",
        errorMessage= "",
        debugEvent= "",
        debugMessage= ""
    )
    #t.save()
    user.save()
    return render(request, 'confirmPurchase.html', context)

def sellStock(request, stockSymbol):

    myAccount = Account.objects.filter(username="daniel").first()
    stock = FrontEndStock.objects.filter(stockSymbol=stockSymbol).first()
    
    stockFacts = {}
    stockFacts["sym"] = stockSymbol
    stockFacts["currentPrice"] = stock.price
    stockFacts["amount"] = 0
    if not myAccount.stocks:
        print ("none")
    else:
        stockFacts["amount"] = myAccount.stocks[stockSymbol]["amount"]
        stockFacts["currValue"] = stockFacts["amount"] * stockFacts["currentPrice"]

    
    context = {
        'stock': stockFacts
    }

    return render(request, 'sellStock.html', context)

def processPurchase(request):
    return HttpResponse("Processing purchase")

