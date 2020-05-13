import asyncio
import functools
from collections import namedtuple

from .cards import RENTS, action_card

payment_tuple = namedtuple('payment', ['paid', 'owed', 'overpaid', 'remaining'])


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res


def force_sync(fn):
    '''
    turn an async function to sync function
    '''
    import asyncio

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            return asyncio.get_event_loop().run_until_complete(res)
        return res

    return wrapper


def pay_from_bank(amount_owed,
                  available_money,
                  used_money=None,
                  unused_money=None):
    """
    make a payment from bank account
    monopdeal doesnt make change
    so if you get charged $1M and all you have is a $10M bill
    welp, that sucks

    Arguments:
        amount_owed {int} -- amount to pay
        available_money {list} -- list of money_card tuples

    Keyword Arguments:
        used_money {list} -- money used in payment (used in recursion) (default: {None})
        unused_money {list} -- money not used in payment (used in recursion) (default: {None})

    Returns:
        payment_tuple -- payment(paid=[money_card], owed=0, overpaid=0, remaining=[money_card])
    """
    used_money = used_money or []
    unused_money = unused_money or []

    if amount_owed <= 0:
        return payment_tuple(used_money, 0, amount_owed, available_money + unused_money)

    total_money_amount = sum(money.value for money in available_money)
    if amount_owed >= total_money_amount:
        paid_off = amount_owed - total_money_amount
        return payment_tuple(used_money + available_money, max(paid_off, 0), 0 - paid_off, unused_money)

    use_first_money = pay_from_bank(amount_owed - available_money[0].value,
                                    available_money[1:],
                                    used_money + [available_money[0]],
                                    unused_money)
    dont_use_first_money = pay_from_bank(amount_owed,
                                         available_money[1:],
                                         used_money + [],
                                         unused_money + [available_money[0]])

    # try and hit exact payment, without overpaying, using the fewest amount of bills
    return min(use_first_money, dont_use_first_money,
               key=lambda x: (x.owed, -x.overpaid, len(x.paid)))


def pay_from_properties(amount_owed,
                        available_properties):
    """
    make a payment from properties

    Arguments:
        amount_owed {int} -- amount to pay
        available_properties {list} -- list of property_card tuples

    Returns:
        payment_tuple -- payment(paid=[property_card], owed=0, overpaid=0, remaining=[property_card])
    """
    if amount_owed <= 0:
        return payment_tuple([], 0, amount_owed, available_properties)

    properties = [prop for prop_set in available_properties.values() for prop in prop_set]
    total_property_value = sum([prop.value for prop in properties])
    if amount_owed >= total_property_value:
        paid_off = amount_owed - total_property_value
        return payment_tuple(properties, max(paid_off, 0), 0 - paid_off, [])

    # seperate out properties into singles, and sets (which are more valuable)
    singles, nonsingles, partial_sets, full_sets = [], [], [], []
    for prop_set, properties in available_properties.items():
        if check_full_set(prop_set, properties):
            nonsingles.extend(properties)
            full_sets.append((properties, get_rent(prop_set, properties)))
        elif len(properties) > 1:
            nonsingles.extend(properties)
            partial_sets.append((properties, get_rent(prop_set, properties)))
        else:
            singles.extend(properties)
    property_sets = sorted(partial_sets, key=lambda x: -x[1]) + sorted(full_sets, key=lambda x: -x[1])

    # try to pay off using just single properties
    payment = pay_from_bank(amount_owed, singles)
    if not payment.owed:
        return payment_tuple(payment.paid, payment.owed, payment.overpaid, payment.remaining + nonsingles)

    # start breaking into partial and full property sets
    while payment.owed and property_sets:
        smallest_set, property_sets = property_sets[0], property_sets[1:]
        payment = pay_from_bank(payment.owed, smallest_set[0] + payment.remaining, payment.paid)

    unused_properties = [prop for properties, _ in property_sets for prop in properties]
    return payment_tuple(payment.paid, payment.owed, payment.overpaid, payment.remaining + unused_properties)


def check_full_set(property_set,
                   properties):
    """
    check if its a full set of properties

    Arguments:
        property_set {string} -- name of property set
        properties {list} -- list of properties

    Returns:
        bool
    """
    return len(properties) >= len(RENTS[property_set])


def get_rent(property_set,
             properties):
    """
    get rent amount for property set

    Arguments:
        property_set {string} -- name of property set
        properties {list} -- list of properties

    Returns:
        int -- rent amount
    """
    if not properties:
        return 0
    try:
        return RENTS[property_set][len(properties) - 1]
    except IndexError:
        # handle houses, hotels
        rent = RENTS[property_set][-1]
        rent_bonuses = sum(x.value for x in properties if type(x) == action_card)
        return rent + rent_bonuses
