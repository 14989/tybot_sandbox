from django.shortcuts import render

# Create your views here.

from .models import Change
from .tools import add_company_by_email_domain as acbed
from .tools import update_country_by_state as ucbs
from .tools import remove_unknown_characters as ruc
from .tools import make_emails_all_lowercase as meal
from .tools import identify_broken_emails as ibe

def change_table(request):
    changes = Change.objects.all()
    #return render(request, 'tybot_app/landing_page.html', {'changes': changes})
    return render(request, 'tybot_app/change_table.html', {'changes': changes})

def landing_page(request):
    changes = Change.objects.all()
    return render(request, 'tybot_app/landing_page.html', {'changes': changes})
    #return render(request, 'tybot_app/change_table.html', {'changes': changes})

def company(request):
    acbed.add_company_by_email_domain()
    changes = Change.objects.all()
    return render(request, 'tybot_app/change_table.html', {'changes': changes})

def roadmap(request):
    changes = Change.objects.all()
    return render(request, 'tybot_app/tybotroadmap.html', {'changes': changes})

def country(request):
    ucbs.update_country_by_state()
    changes = Change.objects.all()
    return render(request, 'tybot_app/change_table.html', {'changes': changes})

def unknown(request):
    ruc.remove_unknown_characters()
    changes = Change.objects.all()
    return render(request, 'tybot_app/change_table.html', {'changes': changes})

def lower(request):
    meal.make_emails_all_lowercase()
    changes = Change.objects.all()
    return render(request, 'tybot_app/change_table.html', {'changes': changes})

def broken(request):
    ibe.identify_broken_emails()
    changes = Change.objects.all()
    return render(request, 'tybot_app/change_table.html', {'changes': changes})

def all(request):
    acbed.add_company_by_email_domain(repeat=2022)
    ucbs.update_country_by_state(repeat=2022)
    ruc.remove_unknown_characters(repeat=2022)
    meal.make_emails_all_lowercase(repeat=2022)
    ibe.identify_broken_emails(repeat=2022)
    changes = Change.objects.all()
    return render(request, 'tybot_app/change_table.html', {'changes': changes})