def is_time(time):
    if time.count(':') > 1 or time.count(':') == 0:
        return False
    else:
        split_time = time.split(':')
        hours = parse_int(split_time[0])
        minutes = parse_int(split_time[1])
        if hours is None or minutes is None:
            return False
        if hours > 23 or hours < 0 or minutes > 59 or minutes < 0:
            return False
        return True


def parse_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


# TODO: Переписать эту функцию
def to_timezone_for_bot(message_time, bot_time_zone, user_time_zone):
    user_time_zone = int(user_time_zone)//3600

    definitions_timezones = user_time_zone - bot_time_zone

    hour = message_time.split(':')[0]

    message_time = f'{int(hour) - definitions_timezones}' + ':' + message_time.split(':')[1]

    bot_hour = int(message_time.split(':')[0])

    if bot_hour < 0:
        bot_hour = 24 - abs(bot_hour)
        message_time = message_time.replace(message_time.split(':')[0], f'{bot_hour}')
    elif bot_hour > 23:
        bot_hour = bot_hour - 24
        message_time = message_time.replace(message_time.split(':')[0], f'{bot_hour}')

    if int(message_time.split(':')[0]) < 10:
        return '0' + message_time
    else:
        return message_time
