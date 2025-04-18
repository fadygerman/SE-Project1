
import boto3

from AWSLambda.database.BookingsTable import Bookings

ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

BookingService = Bookings(ddb)
print(BookingService)
testTable = BookingService.create_table("testTableName")
print(testTable)
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
