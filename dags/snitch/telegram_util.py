import yaml
import telegram

message_template = "Match: {teams}\n{link}\n Expected goals: 1.1 - 2.2"


def main():
    bot_token = '5775727156:AAFji3qtTLvO4ZmFIOsLuAEsDCeM30XT7dw'
    bot_chatID = 354467348
    bot = telegram.Bot(bot_token)
    with open('/home/asus/PycharmProjects/snitch/data.yml', 'r') as file_to_read:
        matches_dict = yaml.safe_load(file_to_read)
        for match_id, match_data in matches_dict.items():
            message_to_send = message_template.format(teams=match_data.get('name'), link=match_data.get('link'))
            bot.send_message(text=message_to_send, chat_id=bot_chatID)


if __name__ == '__main__':
    main()

# import time
# # import schedule
# import requests
# import yaml
#
# message_template = """Match: {teams}\n{link}\n Expected goals: 1.1 - 2.2"""
#
#
# def telegram_bot_sendtext(bot_message):
#     bot_token = '5775727156:AAFji3qtTLvO4ZmFIOsLuAEsDCeM30XT7dw'
#     bot_chatID = '5775727156'
#     send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
#
#     response = requests.get(send_text)
#
#     return response.json()
#
#
# def report():
#     with open('/home/asus/PycharmProjects/snitch/data.yml', 'r') as file_to_read:
#         matches_dict = yaml.safe_load(file_to_read)
#         qty = 3
#         for match_id, match_data in matches_dict.items():
#             if qty != 0:
#                 qty -= 1
#                 message_to_send = message_template.format(teams=match_data.get('name'), link=match_data.get('link'))
#                 print(f'Sending.... {message_to_send}')
#                 r = telegram_bot_sendtext(message_to_send)
#                 print(r)
#             else:
#                 break
#
#
# report()

# my_balance = 10  ## Replace this number with an API call to fetch your account balance
# my_message = "Current balance is: {}".format(my_balance)  ## Customize your message
# telegram_bot_sendtext(my_message)


# schedule.every().day.at("12:00").do(report)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)
