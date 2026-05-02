from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import CoachProfile, Organization

def coaches_directory(request):
    coaches = CoachProfile.objects.filter(is_available=True)
    specialties = CoachProfile.Specialty.choices
    context = {'coaches': coaches, 'specialties': specialties}
    return render(request, 'coaching/coaches_directory.html', context)

def coach_detail(request, pk):
    coach = get_object_or_404(CoachProfile, pk=pk)
    context = {'coach': coach}
    return render(request, 'coaching/coach_detail.html', context)

@login_required
def coach_profile_edit(request):
    try:
        coach = CoachProfile.objects.get(user=request.user)
    except CoachProfile.DoesNotExist:
        return redirect('coaches:coaches-directory')
    
    if request.method == 'POST':
        for key, value in request.POST.items():
            if hasattr(coach, key):
                setattr(coach, key, value)
        coach.save()
        return redirect('coaches:coach-detail', pk=coach.pk)
    context = {'coach': coach}
    return render(request, 'coaching/coach_detail.html', context)

def organization_detail(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    context = {'organization': org}
    return render(request, 'coaching/coach_detail.html', context)
