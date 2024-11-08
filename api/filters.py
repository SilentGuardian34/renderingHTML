from datetime import date
from enum import Enum

from api.models import Schedule


class FilterType(Enum):
    GROUP = "group"
    TEACHER = "teacher"
    PLACE = "place"


class _InnerFilterType(Enum):
    GROUP = "group"
    TEACHER = "teacher"
    PLACE = "place"
    DATERANGE = "daterange"


class Filter:
    def __init__(self, is_from_daterange: bool, start_time: date = date(1970, 1, 1), end_time: date = date(1970, 1, 1),
                 filter_type: FilterType = FilterType.TEACHER, idnumber: str = ""):
        if is_from_daterange:
            if start_time > end_time:
                raise ValueError("Начальная дата больше конечной")

            self.filter_type = _InnerFilterType.DATERANGE
            self.end_time = end_time
            self.start_time = start_time
        else:
            self.filter_type = _InnerFilterType(filter_type.value)
            self.idnumber = idnumber

    @classmethod
    def from_daterange(cls, start_time: date, end_time: date):
        return cls(is_from_daterange=True, start_time=start_time, end_time=end_time)

    @classmethod
    def from_filter_type(cls, filter_type: FilterType, idnumber: str):
        return cls(is_from_daterange=False, filter_type=filter_type, idnumber=idnumber)

    def apply_to(self, schedule: Schedule) -> Schedule:
        schedule_copy = schedule.model_copy(deep=True)
        if self.filter_type == _InnerFilterType.DATERANGE:
            # Filter holdings of each event
            for event in schedule_copy.events:
                event.holdings = [holding for holding in event.holdings if
                                  self.start_time <= holding.event_date <= self.end_time]
            # Remove events that doesn't have any holdings
            schedule_copy.events = [event for event in schedule_copy.events if event.holdings]
        elif self.filter_type == _InnerFilterType.GROUP:
            # Save only events that has current group
            schedule_copy.events = [event for event in schedule_copy.events if
                                    any(participant for participant in event.participants
                                        if participant.is_group == True and participant.idnumber == self.idnumber)]
        elif self.filter_type == _InnerFilterType.TEACHER:
            # Save only events that has current teacher
            schedule_copy.events = [event for event in schedule_copy.events if
                                    any(participant for participant in event.participants
                                        if participant.is_group == False and participant.idnumber == self.idnumber and participant.role == participant.Role.TEACHER)]
        elif self.filter_type == _InnerFilterType.PLACE:
            # Save only holdings that has current place
            for event in schedule_copy.events:
                event.holdings = [holding for holding in event.holdings if holding.place.idnumber == self.idnumber]
            # Remove events that doesn't have any holdings
            schedule_copy.events = [event for event in schedule_copy.events if event.holdings]
        return schedule_copy
