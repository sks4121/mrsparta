from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ProgressPhoto

@login_required
def photo_list(request):
    photos = ProgressPhoto.objects.filter(client=request.user).order_by('-created_at')
    context = {'photos': photos}
    return render(request, 'fitness/photo_list.html', context)

@login_required
def photo_detail(request, pk):
    photo = get_object_or_404(ProgressPhoto, pk=pk, client=request.user)
    context = {'photo': photo}
    return render(request, 'fitness/photo_detail.html', context)

@login_required
def photo_upload(request):
    if request.method == 'POST':
        ProgressPhoto.objects.create(
            client=request.user,
            image=request.FILES.get('image'),
            angle=request.POST.get('angle'),
            week=request.POST.get('week')
        )
        return redirect('photos:photo-list')
    return render(request, 'fitness/photo_upload.html')

@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(ProgressPhoto, pk=pk, client=request.user)
    photo.delete()
    return redirect('photos:photo-list')
