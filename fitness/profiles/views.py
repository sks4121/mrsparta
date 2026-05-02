from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ClientProfile

@login_required
def client_profile(request):
    profile = get_object_or_404(ClientProfile, user=request.user)
    context = {'profile': profile}
    return render(request, 'profiles/athlete_profile.html', context)

@login_required
def client_profile_edit(request):
    profile = get_object_or_404(ClientProfile, user=request.user)
    if request.method == 'POST':
        profile.weight_kg = request.POST.get('weight_kg', profile.weight_kg)
        profile.height_cm = request.POST.get('height_cm', profile.height_cm)
        profile.body_fat_pct = request.POST.get('body_fat_pct', profile.body_fat_pct)
        profile.goal = request.POST.get('goal', profile.goal)
        profile.save()
        return redirect('profiles:client-profile')
    context = {'profile': profile}
    return render(request, 'profiles/profile_edit.html', context)
