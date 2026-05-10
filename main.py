from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from datetime import datetime, timedelta

TOKEN = "8684381963:AAGjs19VEYKU2GpjErxfodfi3wv8JNzoF3Q"
ADMIN_ID = 7714352436


# RESERVED TIMES
# FORMAT:
# "YEAR-MONTH-DAY": ["HOUR:00"]

reserved_slots = {}


# USER DATA
user_data_store = {}


# SERVICES
services = {
    "relax": {
        "name": "🌿 Relax Massage",
        "description": "Perfect for stress relief, relaxation and improving sleep quality."
    },

    "sport": {
        "name": "🏃 Sport Massage",
        "description": "Ideal for muscle recovery, body tension and active lifestyles."
    },

    "deep": {
        "name": "🔥 Deep Tissue",
        "description": "Deep pressure massage focused on muscle knots and chronic tension."
    },

    "thai": {
        "name": "🫧 Vacuum Cupping Therapy",
        "description": "Traditional cupping therapy to improve circulation and relieve muscle tension."
    }
}


# DURATIONS + PRICES
prices = {
    "30": "20€",
    "60": "30€",
    "90": "40€",
    "120": "50€"
}


# MAIN MENU
def main_menu():

    keyboard = [
        [InlineKeyboardButton("💆 Services", callback_data="services")],
        [InlineKeyboardButton("💰 Prices", callback_data="prices")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")]
    ]

    return InlineKeyboardMarkup(keyboard)


# SERVICES MENU
def services_menu():

    keyboard = [
        [InlineKeyboardButton("🌿 Relax Massage", callback_data="service_relax")],
        [InlineKeyboardButton("🏃 Sport Massage", callback_data="service_sport")],
        [InlineKeyboardButton("🔥 Deep Tissue", callback_data="service_deep")],
        [InlineKeyboardButton("🫧 Vacuum Cupping Therapy", callback_data="service_thai")],
        [InlineKeyboardButton("⬅️ Back", callback_data="main")]
    ]

    return InlineKeyboardMarkup(keyboard)


# DURATION MENU
def duration_menu():

    keyboard = [
        [InlineKeyboardButton("30 min — 20€", callback_data="duration_30")],
        [InlineKeyboardButton("60 min — 30€", callback_data="duration_60")],
        [InlineKeyboardButton("90 min — 40€", callback_data="duration_90")],
        [InlineKeyboardButton("120 min — 50€", callback_data="duration_120")],
        [InlineKeyboardButton("⬅️ Back", callback_data="services")]
    ]

    return InlineKeyboardMarkup(keyboard)


# DATE MENU
def date_menu():

    keyboard = []

    now = datetime.now()

    current_hour = now.hour

    for i in range(7):

        day = now + timedelta(days=i)

        # اگر امروز بعد از 22:00 بود، امروز نمایش داده نشود
        if i == 0 and current_hour >= 22:
            continue

        label = day.strftime("%a %d %b")
        value = day.strftime("%Y-%m-%d")

        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"date_{value}")
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="services")
    ])

    return InlineKeyboardMarkup(keyboard)


# TIME MENU
def time_menu(selected_date):

    keyboard = []

    now = datetime.now()

    today_string = now.strftime("%Y-%m-%d")

    for hour in range(14, 23):

        # اگر امروز باشد، ساعت‌های گذشته نمایش داده نشوند
        if selected_date == today_string:

            if hour <= now.hour:
                continue

        value = f"{hour}:00"

        # RESERVED TIMES
        if selected_date in reserved_slots:

            if value in reserved_slots[selected_date]:

                keyboard.append([
                    InlineKeyboardButton(
                        f"{value} ❌ Reserved",
                        callback_data="reserved"
                    )
                ])

                continue

        display_hour = hour

        suffix = "PM"

        if hour > 12:
            display_hour = hour - 12

        time_label = f"{display_hour}:00 {suffix}"

        keyboard.append([
            InlineKeyboardButton(
                time_label,
                callback_data=f"time_{value}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="services")
    ])

    return InlineKeyboardMarkup(keyboard)


# LOCATION MENU
def location_menu():

    keyboard = [
        [InlineKeyboardButton("🏠 Your Place", callback_data="location_home")],
        [InlineKeyboardButton("🪷 Private Studio", callback_data="location_studio")],
        [InlineKeyboardButton("⬅️ Back", callback_data="services")]
    ]

    return InlineKeyboardMarkup(keyboard)


# BOOKING SUMMARY
def booking_summary(user_id):

    data = user_data_store[user_id]

    return (
        f"✨ Booking Summary\n\n"
        f"💆 Service: {data['service']}\n"
        f"⏱ Duration: {data['duration']} min\n"
        f"💰 Price: {data['price']}\n"
        f"📅 Date: {data['date']}\n"
        f"⏰ Time: {data['time']}\n"
        f"📍 Location: {data['location']}"
    )


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "✨ Welcome to BCN Massage\n\nChoose an option:",
        reply_markup=main_menu()
    )


# BUTTON HANDLER
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    user_id = query.from_user.id

    if user_id not in user_data_store:
        user_data_store[user_id] = {}

    # SERVICES
    if data == "services":

        await query.edit_message_text(
            text="💆 Choose Your Service",
            reply_markup=services_menu()
        )

        # SERVICE SELECTED
    elif data.startswith("service_"):

        service_key = data.replace("service_", "")

        user_data_store[user_id]["service"] = services[service_key]["name"]

        service_name = services[service_key]["name"]
        service_description = services[service_key]["description"]

        await query.edit_message_text(
            text=(
                f"{service_name}\n\n"
                f"{service_description}\n\n"
                "⏱ Choose Duration"
            ),
            reply_markup=duration_menu()
        )
    # DURATION
    elif data.startswith("duration_"):

        duration = data.replace("duration_", "")

        user_data_store[user_id]["duration"] = duration
        user_data_store[user_id]["price"] = prices[duration]

        await query.edit_message_text(
            text="📅 Choose Date",
            reply_markup=date_menu()
        )

    # DATE
    elif data.startswith("date_"):

        selected_date = data.replace("date_", "")

        user_data_store[user_id]["date"] = selected_date

        await query.edit_message_text(
            text="⏰ Choose Start Time",
            reply_markup=time_menu(selected_date)
        )

    # RESERVED CLICK
    elif data == "reserved":

        await query.answer(
            "This time is already reserved.",
            show_alert=True
        )

    # TIME
    elif data.startswith("time_"):

        selected_time = data.replace("time_", "")

        user_data_store[user_id]["time"] = selected_time

        await query.edit_message_text(
            text="📍 Choose Location",
            reply_markup=location_menu()
        )

    # YOUR PLACE
    elif data == "location_home":

        user_data_store[user_id]["location"] = "Your Place"

        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
            [InlineKeyboardButton("⬅️ Back", callback_data="services")]
        ]

        await query.edit_message_text(
            text=booking_summary(user_id),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # PRIVATE STUDIO
    elif data == "location_studio":

        user_data_store[user_id]["location"] = "Private Studio"

        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
            [InlineKeyboardButton("⬅️ Back", callback_data="services")]
        ]

        await query.edit_message_text(
            text=(
                "🪷 Private Studio\n\n"
                "📍 Plaça Universitat, Barcelona\n\n"
                + booking_summary(user_id)
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # CONFIRM
    elif data == "confirm":

        booking_text = booking_summary(user_id)

        customer_message = (
            "✅ Your booking has been confirmed!\n\n"
            + booking_text
            + "\n\nWe will contact you shortly."
        )

        await query.edit_message_text(
            text=customer_message
        )

        username = query.from_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "No username"

        admin_message = (
            "📥 NEW BOOKING\n\n"
            + booking_text
            + f"\n\n👤 Username: {username_text}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message
        )

    # PRICES
    elif data == "prices":

        await query.edit_message_text(
            text=(
                "💰 Price List\n\n"
                "30 min — 20€\n"
                "60 min — 30€\n"
                "90 min — 40€\n"
                "120 min — 50€"
            ),
            reply_markup=main_menu()
        )

    # CONTACT
    elif data == "contact":

        await query.edit_message_text(

        text=(

            "📞 Contact Admin\n\n"

            "Telegram: @MassageAdmin_BCN"

        ),

        reply_markup=main_menu()
        )

    # BACK MAIN
    elif data == "main":

        await query.edit_message_text(
            text="✨ Welcome to BCN Massage\n\nChoose an option:",
            reply_markup=main_menu()
        )


# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("BCNMassageBot Running...")
app.run_polling()
