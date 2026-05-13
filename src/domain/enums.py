import enum


class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"


class RoleType(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    USER = "user"


class EventType(str, enum.Enum):
    LESSON_REMINDER = "lesson_reminder"
    NEW_ASSIGNMENT = "new_assignment"


class EventStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
