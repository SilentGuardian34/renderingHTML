import json
from datetime import datetime
from itertools import groupby
from operator import itemgetter

import httplib2
import urllib

from django.views.generic.base import TemplateView

from api.importers import JSONImporter
from api.models import EventParticipant
from schedule_html_renderer.settings import CORE_PATH
from api.filters import FilterType, Filter


class ScheduleRenderView(TemplateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.schedule = None
        self.error_str = None

    def get(self, request, *args, **kwargs):
        self.schedule_type = request.GET.get('schedule_type', None)
        self.uuid = request.GET.get('uuid', None)
        self.start_time = request.GET.get('start_time', None)
        self.end_time = request.GET.get('end_time', None)
        self.hide_columns = request.GET.get('hide_columns', None)

        # Get and parse schedule from the core
        self.data = self.get_schedule_from_core()
        # Create data for UI
        for event_day in self.data:
            event_day.append(event_day[0][0].strftime('%A')) # Day of week
            event_day.append(', '.join([str(x) for x in event_day[0]]))  # Date
            for event in event_day[1]:
                event.teachers = [x.name for x in event.participants if x.role == EventParticipant.Role.TEACHER]
                event.groups = [x.name for x in event.participants if x.role == EventParticipant.Role.STUDENT and x.is_group]

        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=self.get_context_data())

    def get_schedule_from_core(self):
        h = httplib2.Http()
        resp, content = h.request(CORE_PATH)
        if int(resp['status']) != 200:
            self.error_str = f"Core returned: {resp['status']}"
            return

        # Parse
        data = json.loads(content.decode())
        json_importer = JSONImporter(data)
        json_importer.import_data()
        
        # Apply filters
        schedule_filtered = Filter.from_daterange(datetime.fromtimestamp(int(self.start_time)).date() if self.start_time else None,
                                                  datetime.fromtimestamp(int(self.end_time)).date() if self.end_time else None
                                                  ).apply_to(json_importer.schedules[0])
        schedule_filtered = Filter.from_filter_type(FilterType(self.schedule_type), self.uuid).apply_to(schedule_filtered)
        
        # Split holdings
        for event in schedule_filtered.events[:]:
            schedule_filtered.events.remove(event)
            for holding_info in event.holdings:
                schedule_filtered.events.append(event.model_copy(deep=False, update={'holdings' : [holding_info]}))

        # Sort
        schedule_filtered.events.sort(key = lambda x: datetime.combine(x.holdings[0].event_date, x.holdings[0].time_slot.start_time))

        # Group by date
        events_grouped = groupby(schedule_filtered.events,
                                            lambda x: x.holdings[0].event_date)
        events_grouped = [[[key], [item for item in data]] for (key, data) in events_grouped]

        # Group similar days
        for idx_curr, event_day in enumerate(events_grouped):
            if not event_day[0]:
                continue
            for idx_next in range(idx_curr+1, len(events_grouped)):
                if not events_grouped[idx_next][0]:
                    continue
                if set([x.idnumber for x in events_grouped[idx_next][1]]) == set([x.idnumber for x in event_day[1]]) and events_grouped[idx_next][0][0].weekday() == event_day[0][0].weekday():
                    event_day[0].extend(events_grouped[idx_next][0])
                    events_grouped[idx_next][0].clear()

        events_grouped = [x for x in events_grouped if x[0]]


        return events_grouped
            

    def get_template_names(self):
        if self.error_str:
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
        if self.error_str is not None:
            context['error_str'] = self.error_str

        if self.hide_columns is not None:
            context['hide_columns'] = [x for x in self.hide_columns.split(',')]

        if self.schedule_type == FilterType.GROUP.value:
            context['data'] = self.data
        elif self.schedule_type == FilterType.TEACHER.value:
            context['data'] = self.data
        elif self.schedule_type == FilterType.PLACE.value:
            context['data'] = self.data
        else:
            context['error_str'] = self.error_str

        return context

    def get_view_name(self):
        return "Рендеринг Расписания"
