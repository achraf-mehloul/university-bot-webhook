from telegram import Update
from telegram.ext import ContextTypes
import logging
from bot import keyboards, messages, subjects_data
from collections import defaultdict

logger = logging.getLogger(__name__)
user_data = defaultdict(dict)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    await update.message.reply_text(
        messages["en"]["welcome"],
        reply_markup=keyboards.language_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = user_data[user_id].get("lang", "en")
    await update.message.reply_text(messages[lang]["help"])

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    logger.info(f"Callback received: {callback_data}")
    
    try:
        if callback_data.startswith("lang_"):
            await handle_language(query, callback_data)
        elif callback_data.startswith("year"):
            await handle_year(query, callback_data)
        elif callback_data.startswith("sem"):
            await handle_semester(query, callback_data)
        elif callback_data.startswith("sub_"):
            await handle_subject(query, callback_data)
        elif callback_data.startswith("back_"):
            await handle_back(query, callback_data)
    except Exception as e:
        logger.error(f"Error in callback: {e}")
        lang = user_data[query.from_user.id].get("lang", "en")
        await query.edit_message_text(messages[lang]["error"])

async def handle_language(query, callback_data):
    user_id = query.from_user.id
    lang = callback_data.replace("lang_", "")
    user_data[user_id]["lang"] = lang
    
    await query.edit_message_text(
        messages[lang]["choose_year"],
        reply_markup=keyboards.year_keyboard(lang)
    )

async def handle_year(query, callback_data):
    user_id = query.from_user.id
    year = callback_data
    lang = user_data[user_id]["lang"]
    user_data[user_id]["year"] = year
    
    await query.edit_message_text(
        messages[lang]["choose_semester"],
        reply_markup=keyboards.semester_keyboard(year, lang)
    )

async def handle_semester(query, callback_data):
    user_id = query.from_user.id
    sem = callback_data.replace("sem", "")
    lang = user_data[user_id]["lang"]
    year = user_data[user_id]["year"]
    user_data[user_id]["sem"] = sem
    
    keyboard = keyboards.subjects_keyboard(year, sem, lang, subjects_data.subjects_data)
    if not keyboard:
        await query.edit_message_text(messages[lang]["no_content"])
        return
    
    await query.edit_message_text(
        messages[lang]["choose_subject"],
        reply_markup=keyboard
    )

async def handle_subject(query, callback_data):
    user_id = query.from_user.id
    subject = callback_data.replace("sub_", "")
    lang = user_data[user_id]["lang"]
    year = user_data[user_id]["year"]
    sem = user_data[user_id]["sem"]
    user_data[user_id]["subject"] = subject
    
    semester_key = f"semester{sem}"
    subject_data = subjects_data.subjects_data[year][semester_key].get(subject, {})
    back_data = f"SUB_{year}_{sem}"
    
    keyboard = keyboards.resources_keyboard(subject_data, lang, back_data)
    if not keyboard:
        await query.edit_message_text(messages[lang]["no_content"])
        return
    
    await query.edit_message_text(
        f"📚 {subject}\n\n{messages[lang]['choose_resource']}",
        reply_markup=keyboard
    )

async def handle_back(query, callback_data):
    user_id = query.from_user.id
    parts = callback_data.split("_")
    back_type = parts[1].upper()
    lang = user_data[user_id].get("lang", "en")
    
    try:
        if back_type == "LANGUAGE":
            await query.edit_message_text(
                messages[lang]["welcome"],
                reply_markup=keyboards.language_keyboard()
            )
        elif back_type == "YEAR":
            await query.edit_message_text(
                messages[lang]["choose_year"],
                reply_markup=keyboards.year_keyboard(lang)
            )
        elif back_type == "SEMESTER":
            year = user_data[user_id]["year"]
            await query.edit_message_text(
                messages[lang]["choose_semester"],
                reply_markup=keyboards.semester_keyboard(year, lang)
            )
        elif back_type == "SUB":
            year = parts[2]
            sem = parts[3]
            keyboard = keyboards.subjects_keyboard(year, sem, lang, subjects_data.subjects_data)
            if keyboard:
                await query.edit_message_text(
                    messages[lang]["choose_subject"],
                    reply_markup=keyboard
                )
            else:
                await query.edit_message_text(messages[lang]["no_content"])
    except Exception as e:
        logger.error(f"Error in back handler: {e}")
        await query.edit_message_text(messages[lang]["error"])