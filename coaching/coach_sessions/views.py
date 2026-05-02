from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import CoachSession
from coaching.coaches.models import CoachProfile



@login_required
def session_list(request):
    if hasattr(request.user, 'coach_profile'):
        sessions = CoachSession.objects.filter(coach=request.user)
    else:
        sessions = CoachSession.objects.filter(client=request.user)
    context = {'sessions': sessions}
    return render(request, 'coaching/session_list.html', context)

@login_required
def session_booking(request, coach_id):
    coach = get_object_or_404(CoachProfile, pk=coach_id)
    if request.method == 'POST':
        session = CoachSession.objects.create(
            coach=coach.user,
            client=request.user,
            session_type=request.POST.get('session_type'),
            scheduled_at=request.POST.get('scheduled_at'),
            duration_min=coach.session_duration,
            price=coach.session_price,
        )
        return redirect('coach_sessions:session-detail', pk=session.pk)
    context = {'coach': coach}
    return render(request, 'coaching/session_booking.html', context)

@login_required
def session_detail(request, pk):
    session = get_object_or_404(CoachSession, pk=pk)
    if session.client != request.user and session.coach != request.user:
        return redirect('home')
    context = {'session': session}
    return render(request, 'coaching/session_detail.html', context)

@login_required
def session_video(request, pk):
    session = get_object_or_404(CoachSession, pk=pk)
    if session.client != request.user and session.coach != request.user:
        return redirect('home')
    context = {'session': session}
    return render(request, 'coaching/session_video.html', context)

@login_required
def session_complete(request, pk):
    session = get_object_or_404(CoachSession, pk=pk, coach=request.user)
    session.status = 'completed'
    session.completed_at = timezone.now()
    session.save()
    return redirect('coach_sessions:session-list')

@login_required
def session_cancel(request, pk):
    session = get_object_or_404(CoachSession, pk=pk)
    if session.client == request.user or session.coach == request.user:
        session.status = 'cancelled'
        session.save()
    return redirect('coach_sessions:session-list')