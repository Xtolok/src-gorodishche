from .models import ContactInfo, SiteSettings


def site_context(request):
    return {
        'site': SiteSettings.get(),
        'contact': ContactInfo.get(),
    }
