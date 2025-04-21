
import boto3

from backend.AWSLambda.database.BookingsTable import BookingsTable

from backend.models.pydantic.booking import BookingCreate

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

BookingService = BookingsTable(ddb)
print(BookingService)
testTable = BookingService.create_table("testTableName")
print(testTable)

booking1 = BookingCreate(user_id=1,
car_id=999,
start_date="2025-06-01",
end_date="2025-06-05",
planned_pickup_time="09:30:00",
currency_code="USD")

# new booking fails due to overlapping dates
booking2 = BookingCreate(user_id=2,
car_id=999,
start_date="2025-06-02",
end_date="2025-06-06",
planned_pickup_time="09:30:00",
currency_code="USD")

# new booking succeeds due to distinct dates
booking3 = BookingCreate(user_id=3,
car_id=999,
start_date="2025-06-07",
end_date="2025-06-08",
planned_pickup_time="09:30:00",
currency_code="USD")

#new booking succeeds due to distinct car_id
booking4 = BookingCreate(user_id=4,
car_id=1,
start_date="2025-06-01",
end_date="2025-06-05",
planned_pickup_time="09:30:00",
currency_code="USD")

try:
    print(BookingService.add_booking(booking1))
except:
    print("next")

try:
    print(BookingService.add_booking(booking2))
except:
    print("next")
try:
    print(BookingService.add_booking(booking3))
except:
    print("next")

try:
    print(BookingService.add_booking(booking4))
except:
    print("next")


print("all bookings:")
print(BookingService.get_bookings())

BookingService.delete_table(ddb)
'''
table = testTable.create_table("testTableName")
print(table)
testTable.delete_table()

testTable.delete_table(ddb)

BookingsTable = Bookings(dynamodb)

table = BookingsTable.create_table(table_name='testBookingsTable')

table.put_item(
    Item={
        'pk': 'id#1',
        'sk': 'cart#123',
        'name': 'SomeName',
        'inventory': 500,
        # ... more attributes ...
    }
)


'''
