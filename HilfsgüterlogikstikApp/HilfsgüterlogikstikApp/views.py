from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Automatically grant staff status
            user.is_active = True  # Account is immediately active
            user.save()
            messages.success(
                request,
                'Account created successfully. You can now log in.',
            )
            return redirect('admin:login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
