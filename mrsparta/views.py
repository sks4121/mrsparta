from django.shortcuts import render

def index(request):
    return render(request, "index.html")


def schema(request):
    return render(request, "coaching/coach_detail.html")

# Marketing Pages
def about(request):
    return render(request, "marketing/about.html")

def contact(request):
    return render(request, "marketing/contact.html")

def faq(request):
    return render(request, "marketing/faq.html")

def privacy_policy(request):
    return render(request, "marketing/privacy_policy.html")

def terms_conditions(request):
    return render(request, "marketing/terms_conditions.html")

def notifications(request):
    return render(request, "notifications/notification_list.html")
