from datetime import datetime


def create_iso_timestamp():
    """
    Create a  string with the current UTC timestamp.
    :returns: (str) string with timestamp in ISO 8601 format
    """
    timestamp = datetime.utcnow().isoformat() + "Z"  # Append 'Z' for UTC
    timestamp = str(timestamp)
    return timestamp
