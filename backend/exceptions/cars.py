class CarNotFoundException(Exception):
    def __init__(self, car_id: int):
        self.car_id = car_id
        self.message = f"Car with ID {car_id} not found"
        super().__init__(self.message) 