import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

Token = "6658883117:AAEvptiN_eGRdMHQZX1J0yTzBtnL3hWfUgQ"

updater = Updater(Token, use_context=True)
dispatcher = updater.dispatcher
uniq = 0

semester_mapping_2021_2025 = {
    '1': 486,
    '2': 857,
    '3': 1130,
    '4': 1735,
    '5': 2132,
    '6': 0,
    '7': 0,
    '8': 0
}

semester_mapping_2022_2026 = {
    '1': 1369,
    '2': 1831,
    '3': 2302,
    '4': 0,
    '5': 0,
    '6': 0,
    '7': 0,
    '8': 0
}

semester_mapping_2023_2027 = {
    '1': 2343,
    '2': 0,
    '3': 0,
    '4': 0,
    '5': 0,
    '6': 0,
    '7': 0,
    '8': 0
}

def start(update, context):
    update.message.reply_text("Welcome to Result Finder Bot!")
    help_after_start(update , context)

def help_after_start(update, context):
    update.message.reply_text(
        """
        /start -> Welcome to the Bot
        /purpose -> The purpose of the Bot
        /year -> Select the Year
        """
    )

def help_after_year(update, context):
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.message.reply_text(
            """
            /semester -> Define the semester
            """
        )
    elif update.message:
        update.message.reply_text(
            """
            /semester -> Define the semester
            """
        )

def help_after_semester(update, context):
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.message.reply_text(
            """
            /seat -> Please enter the seat
            """
        )
    elif update.message:
        update.message.reply_text(
            """
            /seat -> Please enter the seat
            """
        )

def purpose(update, context):
    update.message.reply_text("The purpose of the Bot is to fetch you result easily!")

def year(update , context) :
    year_keyboard = [
        [InlineKeyboardButton(f"{year} - {int(year)+4}", callback_data=f"year_{year}")] 
        for year in range(2021, 2027)
    ]
    reply_markup = InlineKeyboardMarkup(year_keyboard)
    update.message.reply_text("Please select a Year:", reply_markup=reply_markup)

def year_button_click(update, context):
    global selected_year
    query = update.callback_query
    selected_year = int(query.data.split('_')[1])
    context.user_data['selected_year'] = selected_year
    query.message.reply_text(f"Year {selected_year} - {selected_year + 4} selected.")
    help_after_year(update, context)

def semester(update, context):
    keyboard = [
        [InlineKeyboardButton(f"Semester {i}", callback_data=f"semester_{i}")] 
        for i in range(1, 9)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select a semester:", reply_markup=reply_markup)

def semester_button_click(update, context):
    global uniq
    query = update.callback_query
    selected_semester = query.data.split('_')[1]
    selected_year = context.user_data.get('selected_year')
    
    semester_mappings = {
        2021: semester_mapping_2021_2025,
        2022: semester_mapping_2022_2026,
        2023: semester_mapping_2023_2027
    }

    uniq = semester_mappings.get(selected_year, {}).get(selected_semester)
    
    if uniq is not None:
        result_link = f"https://ums.cvmu.ac.in/GenerateResultHTML/{uniq}.html"
        query.message.reply_text(f"Semester {selected_semester} selected.")
        help_after_semester(update, context)
    else:
        query.message.reply_text("Semester mapping not found for the selected year.")

def seat(update, context):
    global sgpa , cgpa , no_of_backlogs , pass_or_fail , seat_number , result_link
    if context.args is None or len(context.args) == 0:
        update.message.reply_text("Enter the seat number in this format: /seat 5204254")
    else:
        if uniq != 0:
            seat_number = context.args[0]
            result_link = f"https://ums.cvmu.ac.in/GenerateResultHTML/{uniq}/{seat_number}.html"

            r = requests.get(result_link)

            if r.status_code == 200:
                html_content = r.content
                soup = BeautifulSoup(html_content, 'html.parser')
                colum_left_elements = soup.find_all(class_="colum-left")

                sgpa = colum_left_elements[0].get_text().strip()
                cgpa = colum_left_elements[1].get_text().strip()
                no_of_backlogs = colum_left_elements[3].get_text().strip()
                pass_or_fail = colum_left_elements[2].get_text().strip()

                buttons = [
                    InlineKeyboardButton("Result Link", callback_data="result_link"),
                    InlineKeyboardButton("SGPA", callback_data="sgpa"), 
                    InlineKeyboardButton("CGPA", callback_data="cgpa"), 
                    InlineKeyboardButton("Number of Backlogs", callback_data="backlogs"),
                    InlineKeyboardButton("Pass / Fail", callback_data="pass_fail")
                ]

                keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text("Choose what you want:", reply_markup=reply_markup)

            else:
                update.message.reply_text(f"No such result found !!")
        else:
            update.message.reply_text(f"Result not published")

def button_click(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "result_link" :
        query.message.reply_text(f"Result Link for Seat Number {seat_number}: {result_link}")
    elif query.data == "sgpa":
        query.message.reply_text(sgpa)
    elif query.data == "cgpa":
        query.message.reply_text(cgpa)
    elif query.data == "backlogs":
        query.message.reply_text(no_of_backlogs)
    elif query.data == "pass_fail" :
        query.message.reply_text(pass_or_fail)
    

def unknown(update, context):
    update.message.reply_text("Sorry, I didn't understand that command.")

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('purpose', purpose))
dispatcher.add_handler(CommandHandler('year', year))
dispatcher.add_handler(CommandHandler('semester', semester))
dispatcher.add_handler(CommandHandler('seat', seat))
dispatcher.add_handler(CallbackQueryHandler(semester_button_click, pattern=r'semester_'))
dispatcher.add_handler(CallbackQueryHandler(year_button_click, pattern=r'year_'))
dispatcher.add_handler(CallbackQueryHandler(button_click))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown))

updater.start_polling()
updater.idle()