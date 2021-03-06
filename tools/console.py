DEFAULT_PROMPT = "> "
DEFAULT_NEXT_PROMPT = "V"


def _put_select(elements, message="Select"):
    print("{0[message]}:".format(locals()), *("{} - {}".format(i, e) for i, e in enumerate(elements, 1)), sep='\n')


def put_message(message=None):
    if message is not None:
        print(message)
    try:
        input(DEFAULT_NEXT_PROMPT)
    except EOFError:
        pass


def select_one(elements, message="Select one", empty=False):
    ol = list(elements)
    if not ol:
        if not empty:
            raise IndexError("List of selection is empty")
        return None
    _put_select(elements, message=message)
    while True:
        try:
            i = input(DEFAULT_PROMPT)
            if not i:
                if not empty:
                    continue
                return None
        except EOFError:
            if not empty:
                continue
            return None
        else:
            try:
                return ol[int(i) - 1]
            except (IndexError, ValueError):
                pass


def select(elements, message="Select one or more", empty=True):
    ol = list(elements)
    if not ol:
        if not empty:
            raise IndexError("List of selection is empty")
        return []
    _put_select(ol, message=message)
    nl = []
    while True:
        try:
            i = input(DEFAULT_PROMPT)
            if not i:
                if not nl and not empty:
                    continue
                break
        except EOFError:
            if not nl and not empty:
                continue
            break
        else:
            try:
                nl.append(ol.pop(int(i) - 1))
            except (IndexError, ValueError):
                pass
            else:
                if not ol:
                    break
                _put_select(ol, message=message)
    return nl


def validate(message="Confirm?", default=False):
    print(message)
    try:
        response = input(DEFAULT_PROMPT).lower()
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
    except EOFError:
        pass
    return default
