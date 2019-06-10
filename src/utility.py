from datetime import date, datetime, time, timedelta, timezone

import discord
import math
import subprocess


def shell_cmd(cmd):
    result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


def get_first_of_following_month(utcnow):
    year = utcnow.year
    month = utcnow.month + 1
    if (month == 13):
        year += 1
        month = 1
    result = datetime(year, month, 1, 0, 0, 0, 0, timezone.utc)
    return result


def get_first_of_next_month():
    utcnow = get_utcnow()
    return get_first_of_following_month(utcnow)


def get_formatted_datetime(date_time, include_tz=True, include_tz_brackets=True):
    result = date_time.strftime('%Y-%m-%d %H:%M:%S')
    if include_tz:
        tz = date_time.strftime('%Z')
        if include_tz_brackets:
            result += ' ({})'.format(tz)
        else:
            result += ' {}'.format(tz)
    return result


def get_formatted_date(date_time, include_tz=True, include_tz_brackets=True):
    result = date_time.strftime('%Y-%m-%d')
    if include_tz:
        tz = date_time.strftime('%Z')
        if include_tz_brackets:
            result += ' ({})'.format(tz)
        else:
            result += ' {}'.format(tz)
    return result


def get_formatted_timedelta(delta, include_relative_indicator=True):
    total_seconds = delta.total_seconds()
    is_past = total_seconds < 0
    if is_past:
        total_seconds = abs(total_seconds)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    seconds = round(seconds)
    minutes = math.floor(minutes)
    hours = math.floor(hours)
    days = math.floor(days)
    weeks = math.floor(weeks)
    result = ''
    if (weeks > 0):
        result += '{:d}w '.format(weeks)
    result += '{:d}d {:d}h {:d}m {:d}s'.format(days, hours, minutes, seconds)
    if include_relative_indicator:
        if is_past:
            result += ' ago'
        else:
            result = 'in {}'.format(result)
    return result


def get_utcnow(naive=False):
    if naive:
        return datetime.utcnow()
    else:
        return datetime.now(timezone.utc)


async def get_latest_message(from_channel, by_member_id=None, with_content=None, after=None, before=None):
    if from_channel is not None:
        messages = from_channel.history(limit=100, after=after, before=before, older_first=True).flatten()
        for msg in reversed(messages):
            process = not by_member_id or msg.author.id == by_member_id
            if process and msg.content == with_content:
                return msg
    return None


def create_embed(title, description=None, colour=None, field_defs=None):
    result = discord.Embed(title=title, description=description, colour=colour)
    if field_defs is not None:
        for t in field_defs:
            result.add_field(name=t[0], value=t[1], inline=t[2])
    return result


def create_embed_rich(title, description=None, colour=None,
                      field_defs=None, thumbnail_url=None,
                      image_url=None, author_def=None, footer_def=None):
    result = create_embed(title, description, colour, field_defs)
    if thumbnail_url is not None:
        result.set_thumbnail(url=thumbnail_url)
    if image_url is not None:
        result.set_image(url=image_url)
    if author_def is not None:
        result.set_author(name=author_def[0], url=author_def[1], icon_url=author_def[2])
    if footer_def is not None:
        result.set_footer(text=footer_def[0], icon_url=footer_def[1])
    return result


def get_bot_member_colour(bot, guild):
    bot_member = guild.get_member(bot.user.id)
    bot_colour = bot_member.colour
    return bot_colour


def get_embed_field_def(title=None, text=None, inline=True):
    if title and text:
        return (title, text, inline)
    return None


def get_embed_author_def(name, url=None, icon_url=None):
    if name:
        return (name, url, icon_url)
    return None


def get_embed_footer_def(text, icon_url=None):
    if text:
        return (text, icon_url)
    return None


def get_embed_timestamp(date_time):
    if date_time:
        return date_time.strf('%Y-%m-%dT%H:%M:%S.%fZ')
    return None


def format_tuple_list(tuple_list, separator=':'):
    title_width = max([len(item[0]) for item in tuple_list]) + len(separator) + 1
    result = []
    for item in tuple_list:
        title_with_separator = f'{item[0]}{separator}'.ljust(title_width)
        result.append(f'{title_with_separator}{item[1]}')
    return result


# always returns the whole left column while returning a maximum of len(left_column_list) items of the right column
# returns a list
def join_table_columns(left_column_list, right_column_list, separator='   '):
    left_column_width = max([len(row) for row in left_column_list])
    len_left = len(left_column_list)
    len_right = len(right_column_list)
    result = []
    for i in range(len_left):
        row = left_column_list[i].ljust(left_column_width)
        if i < len_right:
            row += f'{separator}{right_column_list[i]}'
        result.append(row)
    return result


def join_format_tuple_list(left_tuple_list, right_tuple_list, tuple_list_separator=':', column_separator='   '):
    left_column = format_tuple_list(left_tuple_list, tuple_list_separator)
    right_column = format_tuple_list(right_tuple_list, tuple_list_separator)
    result = join_table_columns(left_column, right_column, column_separator)
    return result


def format_embed_rows(column_list, separator='  '):
    result = [f'**{row[0]}**{separator}{row[1]}' for row in column_list]
    return result


def is_older_than(timestamp, days=0, hours=0, minutes=0, seconds=0):
    utc_now = get_utcnow()
    if utc_now < timestamp:
        return False

    delta = utc_now - timestamp
    delta_seconds = delta.total_seconds()
    user_seconds = ((days * 24 + hours) * 60 + minutes) * 60 + seconds
    result = user_seconds < delta_seconds
    return result


#---------- DB utilities ----------
DB_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

def db_get_column_definition(column_name, column_type, is_primary=False, not_null=False):
    column_name_txt = column_name.upper()
    column_type_txt = column_type.upper()
    is_primary_txt = ''
    not_null_txt = ''
    if is_primary:
        is_primary_txt = ' PRIMARY KEY'
    if not_null:
        not_null_txt = ' NOT NULL'
    result = '{} {}{}{}'.format(column_name_txt, column_type_txt, is_primary_txt, not_null_txt)
    return result


def db_get_where_and_string(where_strings):
    if where_strings:
        result = ''
        for i in range(0, len(where_strings)):
            if i > 0:
                result += ' AND '
            result += where_strings[i]
        return result


def db_get_where_or_string(where_strings):
    if where_strings:
        result = ''
        for i in range(0, len(where_strings)):
            if i > 0:
                result += ' OR '
            result += where_strings[i]
        return result


def db_get_where_string(column_name, column_value, is_text_type=False):
    column_name = column_name.lower()
    if is_text_type:
        column_value = db_convert_text(column_value)
    return '{} = {}'.format(column_name, column_value)


def db_convert_boolean(value):
    if value:
        return 'TRUE'
    else:
        return 'FALSE'

def db_convert_text(value):
    if value:
        result = str(value)
        result = result.replace('\'', '\'\'')
        result = '\'{}\''.format(result)
        return result
    else:
        return ''

def db_convert_timestamp(datetime):
    if datetime:
        result = 'TIMESTAMPTZ \'{}\''.format(datetime.strftime(DB_TIMESTAMP_FORMAT))
        return result
    else:
        return None

def db_convert_to_boolean(db_boolean):
    if db_boolean is None:
        return None
    db_upper = db_boolean.upper()
    if db_upper == 'TRUE' or db_upper == '1' or db_upper == 'T' or db_upper == 'Y' or db_upper == 'YES':
        return True
    else:
        return False

def db_convert_to_datetime(db_timestamp):
    if db_timestamp is None:
        return None
    result = db_timestamp.strptime(DB_TIMESTAMP_FORMAT)
    return result

def db_convert_to_int(db_int):
    if db_int is None:
        return None
    result = int(db_int)
    return result

def db_convert_to_float(db_float):
    if db_float is None:
        return None
    result = float(db_float)
    return result
