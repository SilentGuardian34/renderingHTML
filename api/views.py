import httplib2
import urllib

from django.views.generic.base import TemplateView

from schedule_html_renderer.settings import CORE_PATH
from api.filters import FilterType


class ScheduleRenderView(TemplateView):

    def get(self, request, *args, **kwargs):
        self.schedule_type = self.kwargs['schedule_type']
        self.uuid = self.kwargs['uuid']
        self.start_time = self.kwargs.get('start_time')
        self.end_time = self.kwargs.get('end_time')

        # Get and parse schedule from the core


        # Get
        if self.schedule_type == FilterType.GROUP.value:
            return ["group.html"]
        elif self.schedule_type == FilterType.TEACHER.value:
            return ["teacher.html"]
        elif self.schedule_type == FilterType.PLACE.value:
            return ["place.html"]

        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=self.get_context_data())

    def get_schedule_from_core(self):
        h = httplib2.Http()
        resp, content = h.request(CORE_PATH)
        if (resp)

    def get_template_names(self, isError = False):
        if isError:
            return ["error.html"]

        if self.schedule_type == FilterType.GROUP.value:
            return ["group.html"]
        elif self.schedule_type == FilterType.TEACHER.value:
            return ["teacher.html"]
        elif self.schedule_type == FilterType.PLACE.value:
            return ["place.html"]
        else:
            return ["error.html"]

    def get_context_data(self, **kwargs):
        context = super(ScheduleRenderView, self).get_context_data(**kwargs)
        context['title'] = "ttt"
        return context

    def get_view_name(self):
        return "Рендеринг Расписания"
