import calendar

from datetime import timedelta
from quads.config import Config


def param_check(data, params, defaults=None):
    if not defaults:
        defaults = {}
    result = []
    # set defaults
    for k, v in defaults.items():
        data.setdefault(k, v)

    if data:
        # check for missing params
        for param in params:
            if param not in data:
                result.append("Missing required parameter: %s" % param)
            elif not data[param]:
                result.append("Could not parse %s parameter" % param)
            elif data[param] == "None":
                data[param] = None

    return result, data


def is_supported(_host_name):
    for host_type in Config.SUPPORTED:
        if host_type in _host_name:
            return True
    return False


def get_vlan(cloud_obj, index, last_nic=False):
    if cloud_obj.vlan and last_nic:
        return int(cloud_obj.vlan.vlan_id)
    else:
        vlan_first = int(Config.sw_vlan_first) - 10
        cloud_offset = int(cloud_obj.name[5:]) * 10
        base_vlan = vlan_first + cloud_offset
        if cloud_obj.qinq == 1:
            index = 0
        vlan = base_vlan + list(Config.OFFSETS.values())[index]
        return vlan


def date_span(start, end, delta=timedelta(days=1)):
    current = start
    while current < end:
        yield current
        current += delta


def month_delta_past(date, months):
    years = months // 12
    year = date.year - years
    month_delta = months % 12
    if not month_delta:
        return date.replace(year=year)
    if month_delta > date.month:
        year -= 1
        month = 12 - month_delta
        day = min(date.day, calendar.monthrange(year, month)[1])
        return date.replace(year=year, month=month, day=day)
    else:
        month = date.month - month_delta
        if month:
            day = min(date.day, calendar.monthrange(year, month)[1])
            return date.replace(year=year, month=month, day=day)
        return date.replace(year=year)


def last_day_month(date):
    next_month = date.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def first_day_month(date):
    return date - timedelta(days=date.day - 1)

