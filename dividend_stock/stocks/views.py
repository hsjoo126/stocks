from django.shortcuts import render


def main(request):
    return render(request, "stocks/main.html")

def high(request):
    return render(request, "stocks/high.html")

def middle(request):
    return render(request, "stocks/middle.html")

def detail(request):
    return render(request, "stocks/detail.html")