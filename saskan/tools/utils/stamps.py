from datetime import UTC, datetime


def create_iso_timestamp():
    """
    Create a  string with the current UTC timestamp.
    :returns: (str) string with timestamp in ISO 8601 format
    """
    timestamp = datetime.now(UTC).isoformat(timespec="milliseconds")
    timestamp = str(timestamp)
    return timestamp
