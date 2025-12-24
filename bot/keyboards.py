from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot import messages

def create_keyboard(buttons, lang="en", back_state=None):
    keyboard = []
    
    for row in buttons:
        keyboard_row = []
        for button in row:
            if isinstance(button, dict):
                if "url" in button:
                    keyboard_row.append(InlineKeyboardButton(button["text"], url=button["url"]))
                else:
                    keyboard_row.append(InlineKeyboardButton(button["text"], callback_data=button["callback_data"]))
            else:
                keyboard_row.append(button)
        keyboard.append(keyboard_row)
    
    if back_state:
        keyboard.append([InlineKeyboardButton(messages[lang]["back"], callback_data=f"back_{back_state}")])
    
    return InlineKeyboardMarkup(keyboard)

def language_keyboard():
    buttons = [
        [
            {"text": "English 🇬🇧", "callback_data": "lang_en"},
            {"text": "العربية 🇩🇿", "callback_data": "lang_ar"}
        ]
    ]
    return create_keyboard(buttons)

def year_keyboard(lang):
    buttons = [
        [
            {"text": "First Year" if lang == "en" else "السنة الأولى", "callback_data": "year1"},
            {"text": "Second Year" if lang == "en" else "السنة الثانية", "callback_data": "year2"}
        ]
    ]
    return create_keyboard(buttons, lang, "LANGUAGE")

def semester_keyboard(year, lang):
    if year == "year1":
        semesters = ["1", "2"]
    else:
        semesters = ["3", "4"]
    
    buttons = [[
        {
            "text": f"Semester {sem}" if lang == "en" else f"السداسي {sem}",
            "callback_data": f"sem{sem}"
        } for sem in semesters
    ]]
    return create_keyboard(buttons, lang, "YEAR")

def subjects_keyboard(year, sem, lang, subjects_data):
    semester_key = f"semester{sem}"
    if year not in subjects_data or semester_key not in subjects_data[year]:
        return None
    
    subjects = subjects_data[year][semester_key]
    buttons = [[{"text": subject, "callback_data": f"sub_{subject}"}] for subject in subjects.keys()]
    return create_keyboard(buttons, lang, f"SEMESTER_{year}")

def resources_keyboard(subject_data, lang, back_data):
    if not subject_data:
        return None
    
    buttons = []
    for resource, link in subject_data.items():
        buttons.append([InlineKeyboardButton(resource, url=link)])
    
    return create_keyboard(buttons, lang, back_data)