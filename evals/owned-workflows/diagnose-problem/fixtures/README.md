# Booking contract

conflicts(bookings, start, end) returns IDs in input order. Inputs are integer intervals [start, end). Empty intervals never conflict; touching endpoints are not overlap. Booking tuples are (ID, start, end). ID 0 is valid.
