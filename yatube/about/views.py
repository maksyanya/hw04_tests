# Импортируем TemplateView
from django.views.generic.base import TemplateView


# Описываем класс AboutAuthorView для страницы about/author
class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


# Описываем класс AboutTechView для страницы about/tech
class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
