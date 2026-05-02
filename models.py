from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional
from datetime import datetime

@dataclass(frozen=True)
class Skill:
    name: str

@dataclass(frozen=True)
class Equipment:
    name: str

from enum import Enum

class PreferenceType(Enum):
    AVOID_DAY = "avoid_day"
    AVOID_TIME_RANGE = "avoid_time_range"

@dataclass(frozen=True)
class Preference:
    type: PreferenceType
    weight: int  # Penalty for violating the preference
    day_of_week: Optional[int] = None # 0=Monday, ..., 6=Sunday
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Doctor:
    id: str
    name: str
    skills: Set[Skill]
    unavailabilities: List[Tuple[datetime, datetime]] = field(default_factory=list)
    preferences: List[Preference] = field(default_factory=list)

@dataclass
class Room:
    id: str
    name: str
    equipment: Set[Equipment]

@dataclass
class ActivityType:
    id: str
    name: str
    required_skills: Set[Skill]
    required_equipment: Set[Equipment] = field(default_factory=set)
    burden_weight: int = 1 # Weight for equity calculation

@dataclass
class ActivityInstance:
    id: str
    activity_type: ActivityType
    start_time: datetime
    end_time: datetime
    required_doctors: int = 1
    fixed_room: Optional[Room] = None
