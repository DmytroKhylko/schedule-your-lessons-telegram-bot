## Вітання та статуси

welcome-new =
    👋 Привіт, { $full_name }!

    Ваш запит на приєднання надіслано адміністраторам.
    Очікуйте підтвердження.

welcome-pending =
    ⏳ Ваш запит ще розглядається.
    Будь ласка, зачекайте підтвердження від адміністратора.

welcome-rejected =
    ❌ На жаль, ваш запит на приєднання було відхилено.

welcome-admin =
    👋 Вітаємо, { $full_name }!

    Ви увійшли як адміністратор.

welcome-active =
    👋 Привіт, { $full_name }!

## Головне меню

main-menu-admin = Оберіть дію:
main-menu-user = Оберіть дію:

btn-pending-requests = 🔔 Запити ({ $count })
btn-schedules = 📅 Розклади
btn-users = 👥 Користувачі
btn-my-schedule = 📅 Мій розклад
btn-settings = ⚙️ Налаштування
btn-back = ◀️ Назад
btn-cancel = ❌ Скасувати
btn-skip = Пропустити ➡️
btn-done = ✅ Готово
btn-confirm = ✅ Підтвердити
btn-create = ➕ Створити розклад

## Запити на приєднання

admin-join-request =
    🔔 Новий запит на приєднання

    👤 Ім'я: { $full_name }
    🔗 Username: { $username }

    Оберіть роль для користувача:

btn-approve-user = ✅ Підтвердити як учня
btn-approve-teacher = 🎓 Підтвердити як вчителя
btn-reject = ❌ Відхилити

no-pending-requests = ✅ Немає нових запитів.

## Підтвердження/відхилення

user-approved-as-user =
    ✅ Ваш запит підтверджено!

    Вас додано як учня. Тепер ви можете переглядати свій розклад.

user-approved-as-teacher =
    ✅ Ваш запит підтверджено!

    Вас додано як вчителя. Тепер ви отримуватимете сповіщення про заняття.

user-rejected =
    ❌ На жаль, ваш запит на приєднання було відхилено адміністратором.

admin-approved-user = ✅ Користувача { $full_name } підтверджено як учня.
admin-approved-teacher = ✅ Користувача { $full_name } підтверджено як вчителя.
admin-rejected-user = ✅ Запит від { $full_name } відхилено.

## Список користувачів

users-list-header = 👥 Активні користувачі:
users-list-empty = Немає активних користувачів.
user-list-item = { $full_name } — { $role }

role-admin = Адміністратор
role-teacher = Вчитель
role-user = Учень

## Створення розкладу

schedule-ask-title = 📝 Введіть назву заняття:
schedule-ask-date = 📅 Оберіть дату:
schedule-ask-time = 🕐 Введіть час початку (формат: ГГ:ХХ, наприклад 10:00):
schedule-ask-duration = ⏱ Оберіть тривалість:
schedule-ask-subject = 📚 Введіть предмет (необов'язково):
schedule-ask-location = 📍 Введіть місце проведення (необов'язково):
schedule-ask-recurrence = 🔁 Чи повторюється це заняття?
schedule-ask-recurrence-days = 📆 Оберіть дні тижня:
schedule-ask-participants = 👥 Оберіть учасників:
schedule-no-participants = ⚠️ Оберіть хоча б одного учасника.

btn-duration-30 = 30 хв
btn-duration-45 = 45 хв
btn-duration-60 = 1 год
btn-duration-90 = 1.5 год
btn-duration-120 = 2 год

btn-recurrence-none = Без повторень
btn-recurrence-daily = Щодня
btn-recurrence-weekly = Щотижня
btn-recurrence-monthly = Щомісяця

day-mon = Пн
day-tue = Вт
day-wed = Ср
day-thu = Чт
day-fri = Пт
day-sat = Сб
day-sun = Нд

schedule-confirm-preview =
    📋 Перегляд розкладу:

    📝 Назва: { $title }{ $subject_line }{ $location_line }
    📅 Дата: { $date }
    🕐 Час: { $time }
    ⏱ Тривалість: { $duration } хв{ $recurrence_line }
    👥 Учасників: { $participant_count }

schedule-confirm-subject-line =

    📚 Предмет: { $subject }
schedule-confirm-location-line =

    📍 Місце: { $location }
schedule-confirm-recurrence-line =

    🔁 Повторення: { $recurrence }

schedule-created = ✅ Розклад створено! Учасники отримали сповіщення.
schedule-creation-cancelled = ❌ Створення розкладу скасовано.

error-invalid-time = ⚠️ Невірний формат часу. Введіть у форматі ГГ:ХХ (наприклад: 09:30).
error-past-date = ⚠️ Дата повинна бути у майбутньому.
error-no-recurrence-days = ⚠️ Оберіть хоча б один день тижня.

## Перегляд розкладу

my-schedule-header = 📅 Ваш розклад:
my-schedule-empty = У вас немає майбутніх занять.

schedule-item =
    📝 { $title }
    📅 { $date } о { $time }
    ⏱ { $duration } хв{ $subject_str }{ $location_str }{ $recurrence_str }

schedule-item-subject = { "  " }📚 { $subject }
schedule-item-location = { "  " }📍 { $location }
schedule-item-recurrence = { "  " }🔁 { $recurrence }

btn-view-schedule = 📋 { $title }
btn-cancel-schedule = ❌ Скасувати заняття

schedule-cancelled = ✅ Заняття скасовано.
schedule-not-found = ⚠️ Заняття не знайдено.

recurrence-daily = Щодня
recurrence-weekly-short = Щотижня ({ $days })
recurrence-monthly = Щомісяця

## Сповіщення

lesson-reminder =
    🔔 Нагадування про заняття

    📝 { $title }{ $subject_line }
    📅 { $date } о { $time }
    ⏱ Тривалість: { $duration } хв{ $location_line }

    ⏰ Заняття починається через { $minutes_before } хв.

new-assignment =
    📅 Вас призначено на нове заняття

    📝 { $title }{ $subject_line }
    📅 { $date } о { $time }
    ⏱ Тривалість: { $duration } хв{ $location_line }

notification-subject-line =

    📚 { $subject }
notification-location-line =

    📍 { $location }

## Налаштування

settings-menu =
    ⚙️ Налаштування

    🌐 Мова: { $language }
    🕐 Нагадувати за: { $minutes } хв
    🌍 Часовий пояс: { $timezone }

btn-change-language = 🌐 Змінити мову
btn-change-notification = 🔔 Час нагадування
btn-change-timezone = 🌍 Часовий пояс

language-select = Оберіть мову:
btn-lang-uk = 🇺🇦 Українська
btn-lang-en = 🇬🇧 English

settings-language-changed = ✅ Мову змінено на Українська.

notification-select = Оберіть за скільки хвилин нагадувати про заняття:
btn-notify-15 = 15 хв
btn-notify-30 = 30 хв
btn-notify-60 = 1 год
btn-notify-120 = 2 год

settings-notification-changed = ✅ Нагадування налаштовано: за { $minutes } хв до заняття.

timezone-select = Оберіть часовий пояс:
settings-timezone-changed = ✅ Часовий пояс змінено на { $timezone }.
