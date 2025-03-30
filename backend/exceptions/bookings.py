class NoCarFoundException(Exception):
  def __init__(self, car_id: int):
    self.car_id = car_id
    self.message = f"Car with ID {car_id} not found"
    
class CarNotAvailableException(Exception):
  def __init__(self, car_id: int):
    self.car_id = car_id
    self.message = f"Car with ID {car_id} is not available"
    
class BookingOverlapException(Exception):
  def __init__(self, car_id: int):
    self.car_id = car_id
    self.message = "The car is already booked for the selected dates"
    
class BookingTooShortException(Exception):
  def __init__(self, car_id: int):
    self.car_id = car_id
    self.message = "Booking must be for at least 1 day"
    

    
