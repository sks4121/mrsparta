from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription, Payment

def plans_pricing(request):
    plans = Plan.objects.filter(is_active=True)
    context = {'plans': plans}
    return render(request, 'billing/plans_pricing.html', context)

@login_required
def checkout(request):
    plan_id = request.GET.get('plan')
    plan = get_object_or_404(Plan, pk=plan_id)
    context = {'plan': plan}
    return render(request, 'billing/checkout.html', context)

@login_required
def payment_process(request):
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        plan = get_object_or_404(Plan, pk=plan_id)
        return redirect('billing:payment-success')
    return render(request, 'billing/payment_processing.html')

@login_required
def payment_success(request):
    context = {'transaction_id': '123456', 'amount': '49.99'}
    return render(request, 'billing/payment_success.html', context)

@login_required
def payment_error(request):
    context = {'error_message': 'Tu pago no fue procesado. Intenta de nuevo.'}
    return render(request, 'billing/payment_error.html', context)

@login_required
def subscription_manage(request):
    subscription = get_object_or_404(Subscription, coach=request.user)
    context = {'subscription': subscription}
    return render(request, 'billing/subscription_manage.html', context)

@login_required
def invoice_list(request):
    payments = Payment.objects.filter(subscription__coach=request.user).order_by('-created_at')
    context = {'payments': payments}
    return render(request, 'billing/invoice_list.html', context)

@login_required
def invoice_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk, subscription__coach=request.user)
    context = {'payment': payment}
    return render(request, 'billing/invoice_detail.html', context)
from django.shortcuts import render

# Create your views here.
