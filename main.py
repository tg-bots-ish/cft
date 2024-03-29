import time
import requests
import json
import telebot

TOKEN = "824568611:AAGfJgHsjmiS8bA352MYGGGi6c-S6YRDwmk"
bot = telebot.TeleBot(TOKEN)
CHAT_ID = 377412691


def to_normal_time(t):
    return time.ctime(t + time.time())


def send_msg(msg):
    bot.send_message(CHAT_ID, msg, parse_mode='Markdown')


def fail(msg):
    bot.send_message(CHAT_ID, '*Error:* _' + str(msg) + '_', parse_mode='Markdown')


def get_round_statistics(x):
    print(x['oldRating'])
    send_msg("*{name}*\nThe Round is Over\nYour place: *{place}*\nRating change: `{oldRating} -> {new}`".format(
        name=x['contestName'], place=x['rank'], oldRating=x['oldRating'], new=x['newRating']))


def get_round_notification(x):
    time_before = abs(int(x['relativeTimeSeconds']))
    send_msg("*{name}*\nThe Round begin at ```" + '{time}'.format(name=x['name'],
                                                                  time=to_normal_time(
                                                                      time_before)) + "```\n_Don't forget_")


def monitoring():
    while True:
        contests = contests_list(False)
        contests_before = list(filter(lambda x: x['phase'] == 'BEFORE', contests))
        contest_is_running = any(map(lambda x: x['phase'] == 'CODING' and x['type'] == 'CF', contests))
        for i in contests_before:
            time_before = i['relativeTimeSeconds']
            if not contest_is_running and need_post(time_before):
                get_round_notification(i)
        rating = user_rating('CodeWeakness')
        get_round_statistics(rating.last())
        time.sleep(0.1)


def contests_list(gym):
    c = requests.get('http://codeforces.com/api/contest.list?gym=' + str(gym).lower())
    contests_data = json.loads(c.text)
    if contests_data['status'] == 'FAILED':
        fail("Too many requests")
    return contests_data['result']


def user_rating(handle):
    r = requests.get('http://codeforces.com/api/user.rating?handle=' + handle)
    rating_data = json.loads(r.text)
    if rating_data['status'] == 'FAILED':
        fail("Too many requests")
    return rating_data['result']


def time_before_round(t):
    t = min(0, t)
    t = abs(t)
    days = t // (60 * 60 * 24)
    t %= 60 * 60 * 24
    hours = t // (60 * 60)
    t %= 60 * 60
    minutes = t // 60
    t %= 60
    seconds = t
    return days, hours, minutes, seconds


def need_post(t):
    now = time_before_round(t)
    if now[0] > 0:
        return (now[0], 0, 0, 0) == now
    times_need = [(1, 0, 0, 0), (0, 8, 0, 0), (0, 6, 0, 0), (0, 3, 0, 0), (0, 2, 0, 0), (0, 1, 0, 0), (0, 0, 30, 0),
                  (0, 0, 20, 0), (0, 0, 10, 0), (0, 0, 5, 0), (0, 0, 2, 0), (0, 0, 1, 0), (0, 0, 0, 30),
                  (0, 0, 0, 10)]
    return t in times_need


monitoring()

