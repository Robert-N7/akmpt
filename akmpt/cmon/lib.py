def top(fun, items):
    """
    Get the first item meeting condition
    :param fun: function(x): bool
    :param items: iterable
    :return: the first item found or none
    """
    for x in items:
        if fun(x):
            return x


def topi(fun, items, return_i=False):
    """
    Get the first item meeting condition
    :param fun: function(i, x): bool
    :param items: iterable
    :return: item if found
    """
    for i in range(len(items)):
        if fun(i, items[i]):
            if return_i:
                return items[i], i
            else:
                return items[i]
    return None, -1 if return_i else None


def topa(attr, value, items):
    """
    Get the first item with matching attribute
    :param attr: attribute (str)
    :param value: match value
    :param items: iterable
    :return: first item found or none
    """
    for x in items:
        if getattr(x, attr) == value:
            return x


def pile(fun, items):
    """
    Collects items returned from 'fun' if they are not falsy
    :param fun: function(x) returning items to gather
    :param items: iterable
    :return list of items gathered
    """
    ret = []
    for x in items:
        if y := fun(x):
            ret.append(y)
    return ret


def pili(fun, items, return_i=False):
    """
    Collects items returned from 'fun' if they are not falsy
    :param fun: function(i, x)
    :param items: iterable
    :param return_i: if true, the index is returned with the returned items
    :return: list of items gathered
    """
    ret = []
    for i in range(len(items)):
        if y := fun(i, items[i]):
            if return_i:
                ret.append((i, y))
            else:
                ret.append(y)
    return ret


def bid(fun, items):
    for x in items:
        fun(x)


def bidi(fun, items):
    for i in range(len(items)):
        fun(i, items[i])


def mapi(get_key, items):
    """
    Create a dictionary using items
    :param get_key: function(x): key
    :param items: iterable
    :return dict
    """
    r = {}
    for x in items:
        r[get_key(x)] = x
    return r


def mapa(attr, items):
    """
    Map attributes to items
    :param attr: attribute
    :param items: items
    :return: dict
    """
    r = {}
    for x in items:
        r[getattr(x, attr)] = x
    return r


def pmap(fun_map, args):
    """
    Parse arguments using a function map.
    Args are parsed one at a time, and the function is passed remaining args.
    :param fun_map: dict{arg: function(args)}
    :param args: keys to use,
    :return: results from calling functions
    """
    results = []
    while len(args):
        f = fun_map[args.pop(0)]
        results.append(f(args))
    return results
