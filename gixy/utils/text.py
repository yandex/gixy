from six import PY3, binary_type, text_type


def to_bytes(obj, encoding="latin1", errors="strict", nonstring="replace"):
    if isinstance(obj, bytes):
        return obj

    if isinstance(obj, str):
        try:
            # Try this first as it's the fastest
            return obj.encode(encoding, errors)
        except UnicodeEncodeError:
            return b"failed_to_encode"

    if nonstring == "simplerepr":
        try:

            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Giving up
                return b"failed_to_encode"
    elif nonstring == "passthru":
        return obj
    elif nonstring == "replace":
        return b"failed_to_encode"
    elif nonstring == "strict":
        raise TypeError("obj must be a string type")
    else:
        raise TypeError(
            "Invalid value %s for to_bytes' nonstring parameter" % nonstring
        )

    return to_bytes(value, encoding, errors)


def to_text(obj, encoding="latin1", errors="strict", nonstring="replace"):
    if isinstance(obj, str):
        return obj

    if isinstance(obj, bytes):
        try:
            return obj.decode(encoding, errors)
        except UnicodeEncodeError:
            return "failed_to_encode"

    if nonstring == "simplerepr":
        try:
            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Giving up
                return "failed_to_encode"
    elif nonstring == "passthru":
        return obj
    elif nonstring == "replace":
        return "failed_to_encode"
    elif nonstring == "strict":
        raise TypeError("obj must be a string type")
    else:
        raise TypeError(
            "Invalid value %s for to_text's nonstring parameter" % nonstring
        )

    return to_text(value, encoding, errors)


to_native = to_text
