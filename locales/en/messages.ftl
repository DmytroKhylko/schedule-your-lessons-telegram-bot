## Bot commands

cmd-start-description = Main menu
cmd-schedule-description = My schedule
cmd-settings-description = Settings
cmd-help-description = Help
cmd-create-description = Create schedule
cmd-requests-description = Join requests
cmd-users-description = Users list

## Help

help-message =
    ℹ️ Available commands:

    /start — Main menu
    /schedule — View your schedule
    /settings — Settings
    /help — This help message

help-message-admin =
    ℹ️ Available commands:

    /start — Main menu
    /schedule — View your schedule
    /create — Create schedule
    /requests — Join requests
    /users — Users list
    /settings — Settings
    /help — This help message

## Greeting and statuses

welcome-new =
    👋 Hello, { $full_name }!

    Your join request has been sent to the administrators.
    Please wait for confirmation.

welcome-pending =
    ⏳ Your request is still being reviewed.
    Please wait for confirmation from an administrator.

welcome-rejected =
    ❌ Unfortunately, your join request has been rejected.

welcome-admin =
    👋 Welcome, { $full_name }!

    You are logged in as an administrator.

welcome-active =
    👋 Hello, { $full_name }!

## Main menu

main-menu-admin = Choose an action:
main-menu-user = Choose an action:

btn-pending-requests = 🔔 Requests ({ $count })
btn-schedules = 📅 Schedules
btn-users = 👥 Users
btn-my-schedule = 📅 My Schedule
btn-settings = ⚙️ Settings
btn-back = ◀️ Back
btn-cancel = ❌ Cancel
btn-skip = Skip ➡️
btn-done = ✅ Done
btn-confirm = ✅ Confirm
btn-create = ➕ Create Schedule

## Join requests

admin-join-request =
    🔔 New join request

    👤 Name: { $full_name }
    🔗 Username: { $username }

    Select a role for this user:

btn-approve-user = ✅ Approve as Student
btn-approve-teacher = 🎓 Approve as Teacher
btn-reject = ❌ Reject

no-pending-requests = ✅ No pending requests.

## Approval/rejection

user-approved-as-user =
    ✅ Your request has been approved!

    You have been added as a student. You can now view your schedule.

user-approved-as-teacher =
    ✅ Your request has been approved!

    You have been added as a teacher. You will now receive lesson notifications.

user-rejected =
    ❌ Unfortunately, your join request has been rejected by an administrator.

admin-approved-user = ✅ User { $full_name } approved as student.
admin-approved-teacher = ✅ User { $full_name } approved as teacher.
admin-rejected-user = ✅ Request from { $full_name } rejected.

## User list

users-list-header = 👥 Active users:
users-list-empty = No active users.
user-list-item = { $full_name } — { $role }

role-admin = Administrator
role-teacher = Teacher
role-user = Student

## Schedule creation

schedule-ask-title = 📝 Enter the lesson title:
schedule-ask-date = 📅 Select a date:
schedule-ask-time = 🕐 Enter start time (format: HH:MM, e.g. 10:00):
schedule-ask-duration = ⏱ Select duration:
schedule-ask-subject = 📚 Enter subject (optional):
schedule-ask-location = 📍 Enter location (optional):
schedule-ask-recurrence = 🔁 Does this lesson repeat?
schedule-ask-recurrence-days = 📆 Select days of the week:
schedule-ask-participants = 👥 Select participants:
schedule-no-participants = ⚠️ Please select at least one participant.

btn-duration-30 = 30 min
btn-duration-45 = 45 min
btn-duration-60 = 1 hour
btn-duration-90 = 1.5 hours
btn-duration-120 = 2 hours

btn-recurrence-none = No recurrence
btn-recurrence-daily = Daily
btn-recurrence-weekly = Weekly
btn-recurrence-monthly = Monthly

day-mon = Mon
day-tue = Tue
day-wed = Wed
day-thu = Thu
day-fri = Fri
day-sat = Sat
day-sun = Sun

schedule-confirm-preview =
    📋 Schedule Preview:

    📝 Title: { $title }{ $subject_line }{ $location_line }
    📅 Date: { $date }
    🕐 Time: { $time }
    ⏱ Duration: { $duration } min{ $recurrence_line }
    👥 Participants: { $participant_count }

schedule-confirm-subject-line =

    📚 Subject: { $subject }
schedule-confirm-location-line =

    📍 Location: { $location }
schedule-confirm-recurrence-line =

    🔁 Recurrence: { $recurrence }

schedule-created = ✅ Schedule created! Participants have been notified.
schedule-creation-cancelled = ❌ Schedule creation cancelled.

error-invalid-time = ⚠️ Invalid time format. Enter in HH:MM format (e.g. 09:30).
error-past-date = ⚠️ The date must be in the future.
error-no-recurrence-days = ⚠️ Please select at least one day of the week.

## Schedule view

my-schedule-header = 📅 Your schedule:
my-schedule-empty = You have no upcoming lessons.

schedule-item =
    📝 { $title }
    📅 { $date } at { $time }
    ⏱ { $duration } min{ $subject_str }{ $location_str }{ $recurrence_str }

schedule-item-subject = { "  " }📚 { $subject }
schedule-item-location = { "  " }📍 { $location }
schedule-item-recurrence = { "  " }🔁 { $recurrence }

btn-view-schedule = 📋 { $title }
btn-cancel-schedule = ❌ Cancel Lesson

schedule-cancelled = ✅ Lesson cancelled.
schedule-not-found = ⚠️ Lesson not found.

recurrence-daily = Daily
recurrence-weekly-short = Weekly ({ $days })
recurrence-monthly = Monthly

## Notifications

lesson-reminder =
    🔔 Lesson Reminder

    📝 { $title }{ $subject_line }
    📅 { $date } at { $time }
    ⏱ Duration: { $duration } min{ $location_line }

    ⏰ Lesson starts in { $minutes_before } min.

new-assignment =
    📅 You have been assigned to a new lesson

    📝 { $title }{ $subject_line }
    📅 { $date } at { $time }
    ⏱ Duration: { $duration } min{ $location_line }

notification-subject-line =

    📚 { $subject }
notification-location-line =

    📍 { $location }

## Settings

settings-menu =
    ⚙️ Settings

    🌐 Language: { $language }
    🔔 Notify before: { $minutes } min
    🌍 Timezone: { $timezone }

btn-change-language = 🌐 Change Language
btn-change-notification = 🔔 Notification Time
btn-change-timezone = 🌍 Timezone

language-select = Select language:
btn-lang-uk = 🇺🇦 Ukrainian
btn-lang-en = 🇬🇧 English

settings-language-changed = ✅ Language changed to English.

notification-select = Select how many minutes before the lesson to be reminded:
btn-notify-15 = 15 min
btn-notify-30 = 30 min
btn-notify-60 = 1 hour
btn-notify-120 = 2 hours

settings-notification-changed = ✅ Notifications set: { $minutes } min before lesson.

timezone-select = Select timezone:
settings-timezone-changed = ✅ Timezone changed to { $timezone }.
