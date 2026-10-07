def conflicts(bookings, start, end):
    return [identifier for identifier, begin, stop in bookings
            if begin <= end and start <= stop]
