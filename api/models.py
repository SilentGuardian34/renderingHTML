from datetime import date, time
from enum import Enum
from typing import Optional, Self, List

from pydantic import BaseModel, Field, model_validator
from rest_framework.exceptions import ValidationError


class CommonModel(BaseModel):
    idnumber: str = Field(max_length=260, title="Уникальный строковый идентификатор")

    # idnumber = models.CharField(
    #     unique=True,
    #     blank=True,
    #     null=True,
    #     max_length=260,
    #     verbose_name="Уникальный строковый идентификатор",
    # )

    # datecreated = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    # datemodified = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения записи")
    # dateaccessed = models.DateTimeField(
    #     null=True, blank=True, verbose_name="Дата доступа к записи"
    # )
    # author = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Автор записи"
    # )
    # note = models.TextField(
    #     null=True, blank=True, verbose_name="Комментарий для этой записи", max_length=1024
    # )

    # @classmethod
    # def last_modified_record(cls) -> Optional[Self]:
    #     return cls.objects.order_by("-datemodified").first()

    def __str__(self):
        return self.__repr__()


class Subject(CommonModel):
    name: str = Field(max_length=256, title="Название")

    def __repr__(self):
        return "{} [{}]".format(str(self.name), self.idnumber)


class TimeSlot(CommonModel):
    start_time: time = Field(title="Время начала")
    end_time: time = Field(title="Время окончания")

    @classmethod
    @model_validator(mode="before")
    def validate_time(cls, field_values):
        if field_values.data["end_time"] <= field_values.data["start_time"]:
            raise ValidationError("Время проведения не корректно")
        return field_values

    def __repr__(self):
        res = self.start_time.strftime("%H:%M")
        if self.end_time:
            res += "- {}".format(self.end_time.strftime("%H:%M"))
        return res


class EventPlace(CommonModel):
    building: str = Field(max_length=128, title="Корпус")
    room: str = Field(max_length=64, title="Аудитория")

    def __repr__(self):
        return str(self.room)


class EventParticipant(CommonModel):
    class Role(Enum):
        STUDENT = "student"
        TEACHER = "teacher"
        ASSISTANT = "assistant"

    name: str = Field(max_length=255, title="Имя")
    role: Role = Field(title="Роль")
    is_group: bool = Field(default=False, title="Является группой")

    def __repr__(self):
        return str(self.name) + f" ({self.role})"


class EventKind(CommonModel):
    name: str = Field(title="Название типа", max_length=64)

    def __repr__(self):
        return "{} [{}]".format(str(self.name), self.idnumber)


class Schedule(CommonModel):
    class Scope(Enum):
        BACHELOR = "bachelor"
        MASTER = "master"
        POSTGRADUATE = "postgraduate"
        CONSULTATION = "consultation"

    faculty: str = Field(max_length=32, title="Факультет")
    scope: Scope = Field(title="Обучение")
    course: int = Field(title="Курс")
    semester: int = Field(title="Семестр")
    years: str = Field(max_length=16, title="Учебный год")
    events: List[Optional["Event"]] = Field(default=[], title="События")

    # def first_event(self):
    #     events = self.events.all()
    #
    #     return events.annotate(min_date=models.Min("holdings__date")).order_by("min_date").first()
    #
    # def last_event(self):
    #     events = self.events.all()
    #
    #     return events.annotate(max_date=models.Max("holdings__date")).order_by("-max_date").first()

    def __repr__(self):
        return f"{self.faculty},{self.years},{self.scope},{self.course}к,{self.semester}сем"


class EventHolding(CommonModel):
    place: EventPlace = Field(EventPlace, title="Место")
    event_date: date = Field(title="Дата")
    time_slot: TimeSlot = Field(title="Временной интервал")

    def __repr__(self):
        date_str = self.event_date.strftime("%Y-%m-%d")
        return f"{self.place}, {date_str}, {self.time_slot}"


class Event(CommonModel):
    kind: EventKind = Field(title="Тип")
    subject: Subject = Field(title="Предмет")
    participants: List[EventParticipant] = Field(default=[], title="Участники")
    teachers: List[str] = Field(default=[], title="Преподаватели")
    groups: List[str] = Field(default=[], title="Группы")
    holdings: List[EventHolding] = Field(default=[], title="Дата, место и время")
    schedule: Schedule = Field(title="Связанное расписание")

    def __repr__(self):
        return f"Занятие по {self.subject.name} [{self.idnumber}]"
