# sm2 algorithm
from datatime import datetime, timedelta

def calculate_next_review(
		repetition: int,
		ease_factor: float,
		interval: int,
		quality: int
) -> tuple:
	"""
	calculate the next review date and updated parameters based on the SM-2 algorithm.

	Args:
		repetition (int): The number of times the item has been reviewed.
		ease_factor (float): current ease factor of the item.
		interval (int): The current interval (in days) until the next review.
		quality (int): The quality of the response (0-5) given by the user during the review.

	Returns:
		tuple: A tuple containing the updated interval, ease factor, repetition count, and the next review date.
	"""
	if quality >= 3:
		if repetition == 0:
			interval = 1
		elif repetition == 1:
			interval = 4
		else:
			interval = int(interval * ease_factor)

		repetition += 1
	else:
		repetition = 0
		interval = 1

	ease_factor += (0.1 - (5 - quality) * (0.07 + (5 - quality) * 0.03))
	ease_factor = max(ease_factor, 1.3)
	
	return (interval, ease_factor, repetition, datetime.now() + timedelta(days=interval))
		