from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.debug import sensitive_variables
from .forms import BusinessIntakeForm


def home(request):
    return render(request, "home.html")

@sensitive_variables()  # Hides all local variables in this view from error logs
def business_view(request):
    if request.method == 'POST':
        form = BusinessIntakeForm(request.POST)
        if form.is_valid():
            # TODO: Save this data to the database or send email
            return HttpResponse("Thank you! We have received your information.")
    else:
        form = BusinessIntakeForm()

    return render(request, 'business_intake.html', {'form': form})