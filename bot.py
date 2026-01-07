from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8527407637:AAEXEHfaEaXLtPs6Safs8tcdYepHTrLjJys"  # Bot tokeningiz
PRIVATE_GROUP_ID = -1003267783623  # Shaxsiy admin guruhingiz ID
OWNER_ID = 7740552653  # Asosiy admin (sizning Telegram ID)

KEYWORDS = []          # Kalit so'zlar ro'yxati
ADMINS = [OWNER_ID]    # Adminlar ro'yxati

# --- Start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    greeting = f"Assalomu alaykum, {update.effective_user.full_name}! ✅"
    await update.message.reply_text(
        greeting,
        reply_markup=get_main_menu(user_id)
    )

# --- Menyu tugmalari ---
def get_main_menu(user_id):
    buttons = [
        [InlineKeyboardButton("➕ Kalit so‘z qo‘shish", callback_data="add_keyword")],
        [InlineKeyboardButton("📝 Kalit so‘zlarni ko‘rish", callback_data="view_keywords")],
        [InlineKeyboardButton("❌ Kalit so‘z o‘chirish", callback_data="delete_keyword")]
    ]

    # Faqat asosiy admin uchun admin menyu
    if user_id == OWNER_ID:
        buttons += [
            [InlineKeyboardButton("➕ Admin qo‘shish", callback_data="add_admin")],
            [InlineKeyboardButton("📝 Adminlarni ko‘rish", callback_data="view_admins")],
            [InlineKeyboardButton("❌ Admin o‘chirish", callback_data="delete_admin")]
        ]

    return InlineKeyboardMarkup(buttons)

# --- CallbackQuery handler ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "add_keyword":
        await query.message.reply_text("Kalit so‘zni yozing:")
        context.user_data["adding_keyword"] = True

    elif query.data == "view_keywords":
        if KEYWORDS:
            await query.message.reply_text("Kalit so‘zlar:\n" + "\n".join(KEYWORDS))
        else:
            await query.message.reply_text("Hozircha hech qanday kalit so‘z yo‘q.")

    elif query.data == "delete_keyword":
        if KEYWORDS:
            await query.message.reply_text(
                "O‘chirmoqchi bo‘lgan kalit so‘zni yozing:"
            )
            context.user_data["deleting_keyword"] = True
        else:
            await query.message.reply_text("Hozircha hech qanday kalit so‘z yo‘q.")

    elif user_id == OWNER_ID:
        # Admin menyusi faqat asosiy admin uchun
        if query.data == "add_admin":
            await query.message.reply_text("Yangi admin Telegram ID sini yuboring:")
            context.user_data["adding_admin"] = True
        elif query.data == "view_admins":
            await query.message.reply_text("Adminlar:\n" + "\n".join([str(a) for a in ADMINS]))
        elif query.data == "delete_admin":
            await query.message.reply_text("O‘chirmoqchi bo‘lgan admin ID sini yuboring:")
            context.user_data["deleting_admin"] = True

# --- Xabarlar handleri ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Kalit so'z qo'shish
    if context.user_data.get("adding_keyword"):
        KEYWORDS.append(text.lower())
        context.user_data["adding_keyword"] = False
        await update.message.reply_text("✅ Kalit so‘z saqlandi.", reply_markup=get_main_menu(user_id))
        return

    # Kalit so'z o'chirish
    if context.user_data.get("deleting_keyword"):
        if text.lower() in KEYWORDS:
            KEYWORDS.remove(text.lower())
            await update.message.reply_text("✅ Kalit so‘z o‘chirildi.", reply_markup=get_main_menu(user_id))
        else:
            await update.message.reply_text("Kalit so‘z topilmadi.", reply_markup=get_main_menu(user_id))
        context.user_data["deleting_keyword"] = False
        return

    # Admin qo'shish (faqat asosiy admin)
    if context.user_data.get("adding_admin") and user_id == OWNER_ID:
        try:
            new_admin_id = int(text)
            if new_admin_id not in ADMINS:
                ADMINS.append(new_admin_id)
                await update.message.reply_text(f"✅ Yangi admin qo‘shildi: {new_admin_id}", reply_markup=get_main_menu(user_id))
            else:
                await update.message.reply_text("Admin allaqachon mavjud.", reply_markup=get_main_menu(user_id))
        except:
            await update.message.reply_text("❌ Noto‘g‘ri ID.", reply_markup=get_main_menu(user_id))
        context.user_data["adding_admin"] = False
        return

    # Admin o'chirish (faqat asosiy admin)
    if context.user_data.get("deleting_admin") and user_id == OWNER_ID:
        try:
            del_admin_id = int(text)
            if del_admin_id in ADMINS and del_admin_id != OWNER_ID:
                ADMINS.remove(del_admin_id)
                await update.message.reply_text(f"✅ Admin o‘chirildi: {del_admin_id}", reply_markup=get_main_menu(user_id))
            else:
                await update.message.reply_text("❌ Bu adminni o‘chirish mumkin emas.", reply_markup=get_main_menu(user_id))
        except:
            await update.message.reply_text("❌ Noto‘g‘ri ID.", reply_markup=get_main_menu(user_id))
        context.user_data["deleting_admin"] = False
        return

# --- Guruhdagi xabarlarni kuzatish ---
async def group_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    for word in KEYWORDS:
        if word in text:
            user = update.effective_user
            username = user.username
            profile_button = []

            # Username mavjud bo'lsa tugma yaratish
            if username:
                profile_url = f"https://t.me/{username}"
                profile_button = [[InlineKeyboardButton("👤 Yuboruvchi profili", url=profile_url)]]

            report = (
                f"🚨 Kalit so‘z topildi!\n\n"
                f"👥 Guruh: {update.effective_chat.title}\n"
                f"👤 Yozgan: {user.full_name}\n"
                f"💬 Xabar: {update.message.text}"
            )

            await context.bot.send_message(
                chat_id=PRIVATE_GROUP_ID,
                text=report,
                reply_markup=InlineKeyboardMarkup(profile_button) if profile_button else None
            )
            break

# --- Asosiy funksiya ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, message_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, group_watcher))

    print("Bot ishga tushdi ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
