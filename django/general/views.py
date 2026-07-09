from django.views.generic import TemplateView


class WelcomeTemplateView(TemplateView):
    """
    Class-based view to show the welcome template
    """
    template_name = 'general/welcome.html'


class TeamTemplateView(TemplateView):
    """
    Class-based view to show the team template
    """
    template_name = 'general/team.html'


class IntroductionTemplateView(TemplateView):
    """
    Class-based view to show the introduction template
    """
    template_name = 'general/introduction.html'


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
