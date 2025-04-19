
import boto3

from backend.AWSLambda.database.BookingsTable import BookingsTable

from backend.models.pydantic.booking import BookingCreate

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

BookingService = BookingsTable(ddb)
print(BookingService)
testTable = BookingService.create_table("testTableName")
print(testTable)

new_booking = BookingCreate(user_id=1,
car_id=999,  # Non-existent car ID
start_date="2025-06-01",
end_date="2025-06-05",
planned_pickup_time="09:30:00",
currency_code="USD")

print("new_booking: {}".format(new_booking))

print(BookingService.add_booking(new_booking))

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
