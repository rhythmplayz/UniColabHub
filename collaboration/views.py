from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect

from collaboration.models import Resource, Collaborator, JoinRequest, Notification

@login_required
def join_request(request, pk):
    organizer = get_object_or_404(Collaborator, pk=pk)
    user = request.user
    if request.method == 'POST':
        notification = Notification(user=organizer.user, message=user.username+" has requested to join.")
        notification.save()
        JoinRequest.objects.create(organizer=organizer, recipient=user, notification=notification)
        return redirect('home')
    return render(request, 'collaboration/join_request.html', {'organizer': organizer})

@login_required
def review_request(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if notification:
        join_request = get_object_or_404(JoinRequest, notification=notification)
        if request.method == 'POST':
            approval_status = request.POST.get('status')
            if approval_status == "approved":
                join_request.approve_status = "approved"
                join_request.save()
                Collaborator.objects.create(user=join_request.recipient, post=join_request.organizer.post, role='collaborator')
            return redirect('home')
        return render(request, 'collaboration/approve_request.html', {'notification': notification, 'join_request': join_request})
