from django.urls import include, path
from api.views import (
    ScheduleRenderView
)

urlpatterns = [
    path("render/", ScheduleRenderView.as_view())
]