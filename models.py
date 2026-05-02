from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional
from datetime import datetime

@dataclass(frozen=True)
class Skill:
    name: str

@dataclass(frozen=True)
class Equipment:
    name: str

@dataclass
class Doctor:
    id: str
    name: str
    skills: Set[Skill]
    unavailabilities: List[Tuple[datetime, datetime]] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list) # e.g., ["no_friday"]

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
