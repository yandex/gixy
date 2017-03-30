UNSPECIFIED = 'UNSPECIFIED'
LOW = 'LOW'
MEDIUM = 'MEDIUM'
HIGH = 'HIGH'
ALL = [UNSPECIFIED, LOW, MEDIUM, HIGH]


def is_acceptable(current_severity, min_severity):
    return ALL.index(current_severity) >= ALL.index(min_severity)
