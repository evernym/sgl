class PreconditionViolation(BaseException):
    def __init__(self, msg):
        BaseException.__init__(self, msg)


def precondition(expr, msg):
    if not bool(expr):
        raise PreconditionViolation(msg)


def precondition_is_str(value, name):
    if not isinstance(value, str):
        raise PreconditionViolation(f'"{name}" must be a str, not {value.__class__.__name__}.')


def precondition_nonempty_sequence_of_str(value, name):
    if isinstance(value, str):
        raise PreconditionViolation(f"'{name}' must be a non-empty Sequence[str], not str.")
    precondition_nonempty_sequence_of_x(value, name, str)


def precondition_nonempty_sequence_of_x(value, name, typ):
    if value is None:
        bad_type = 'None'
    else:
        try:
            empty = True
            for item in value:
                empty = False
                if isinstance(item, typ):
                    return
                bad_type = f"{value.__class__.__name__} of {item.__class__.__name__}"
                break
            if empty:
                bad_type = f"empty {value.__class__.__name__}"
        except:
            bad_type = f"{value.__class__.__name__}"
    raise PreconditionViolation(f"'{name}' must be a non-empty sequence of {typ.__name__}, not {bad_type}.")
