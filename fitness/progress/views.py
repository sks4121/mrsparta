from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ProgressLog, WorkoutSession

@login_required
def progress_tracker(request):
    logs = ProgressLog.objects.filter(client=request.user).order_by('-date')
    latest_log = logs.first()
    context = {'logs': logs, 'latest_log': latest_log}
    return render(request, 'fitness/progress_tracker.html', context)

@login_required
def progress_log_create(request):
    if request.method == 'POST':
        ProgressLog.objects.create(client=request.user, **request.POST.dict())
        return redirect('progress:progress-tracker')
    return render(request, 'fitness/progress_tracker.html')

@login_required
def progress_log_detail(request, pk):
    log = get_object_or_404(ProgressLog, pk=pk, client=request.user)
    context = {'log': log}
    return render(request, 'fitness/progress_tracker.html', context)

@login_required
def workout_session_list(request):
    sessions = WorkoutSession.objects.filter(client=request.user).order_by('-date')
    context = {'sessions': sessions}
    return render(request, 'fitness/progress_tracker.html', context)

@login_required
def workout_session_detail(request, pk):
    session = get_object_or_404(WorkoutSession, pk=pk, client=request.user)
    context = {'session': session}
    return render(request, 'fitness/progress_tracker.html', context)
