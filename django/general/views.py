from django.views.generic import TemplateView


class WelcomeTemplateView(TemplateView):
    """
    Class-based view to show the welcome template
    """
    template_name = 'general/welcome.html'


class AboutTemplateView(TemplateView):
    """
    Class-based view to show the about template
    """
    template_name = 'general/about.html'


class TranscriptionsTemplateView(TemplateView):
    """
    Class-based view to show the transcriptions template
    """
    template_name = 'general/transcriptions.html'


class ResourcesTemplateView(TemplateView):
    """
    Class-based view to show the resources template
    """
    template_name = 'general/resources.html'


class AccessibilityTemplateView(TemplateView):
    """
    Class-based view to show the accessibility template
    """
    template_name = 'general/accessibility.html'


class CookiesTemplateView(TemplateView):
    """
    Class-based view to show the cookies template
    """
    template_name = 'general/cookies.html'
