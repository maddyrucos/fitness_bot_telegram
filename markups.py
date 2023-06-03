from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

to_menu = InlineKeyboardButton('🏠 Главное меню', callback_data='main_menu')
to_menu_only = InlineKeyboardMarkup(row_width=1).add(to_menu)

# -- Главное меню --

trainings = InlineKeyboardButton('💪 Тренировки', callback_data='trainings')
feeding = InlineKeyboardButton('🍲 Питание', callback_data='feeding')
#profile = InlineKeyboardButton('👤 Профиль', callback_data='profile')
main_menu = InlineKeyboardMarkup(row_width=1).add(trainings, feeding) #, profile)

# -- Тренировки --

continue_training = InlineKeyboardButton('➡ Продолжить', callback_data='continue_training')
new_training = InlineKeyboardButton('🆕 Новая', callback_data='new_training')
trainings_menu = InlineKeyboardMarkup(row_width=1).add(continue_training, new_training, to_menu)

not_chosen_training = InlineKeyboardMarkup(row_width=2).insert(new_training)
not_chosen_training.insert(trainings)

start_training_btn = InlineKeyboardButton('🟢 Начать', callback_data='next_exercise')
start_training_menu = InlineKeyboardMarkup(row_width=2).insert(start_training_btn)
start_training_menu.insert(to_menu)

active_training_next_btn = InlineKeyboardButton('➡ Далее', callback_data='next_iteration')
active_training_exit_btn = InlineKeyboardButton('↩ Выход', callback_data='exit_training')
active_training_menu = InlineKeyboardMarkup(row_width=2).insert(active_training_next_btn)
active_training_menu.insert(active_training_exit_btn)

training_warning_menu = InlineKeyboardMarkup(row_width=2)
training_exit_ok_btn = InlineKeyboardButton('✅ Ок', callback_data='trainings')
training_exit_abort_btn = InlineKeyboardButton('🛑 Отмена', callback_data='next_exercise')
training_warning_menu.insert(training_exit_ok_btn)
training_warning_menu.insert(training_exit_abort_btn)

# -- Питание --

new_diet = InlineKeyboardButton('✍️ Составить', callback_data='new_diet')
body_index = InlineKeyboardButton('📊 ИМТ', callback_data='body_index')
feeding_menu = InlineKeyboardMarkup(row_width=1).add(new_diet, body_index, to_menu)

# -- Профиль --

profile_menu = InlineKeyboardMarkup(row_width=1).add(to_menu)

# -- Администратор --

admin_send = InlineKeyboardButton('Отправить сообщение', callback_data='send_button')
admin_download = InlineKeyboardButton('Выгрузить базу', callback_data='download')
admin_menu = InlineKeyboardMarkup(row_width=1).add(admin_send, admin_download)