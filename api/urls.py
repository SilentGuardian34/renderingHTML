from django.urls import include, path
from api.views import (
    ScheduleRenderView
)

urlpatterns = [
    path("render/<schedule_type>/<uuid>/", ScheduleRenderView.as_view()),
    path("render/<schedule_type>/<uuid>/<start_time>/", ScheduleRenderView.as_view()),
    path("render/<schedule_type>/<uuid>/<start_time>/<end_time>/", ScheduleRenderView.as_view()),
]