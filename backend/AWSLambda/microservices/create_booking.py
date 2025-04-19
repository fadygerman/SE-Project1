# /api/v1/bookings POST

import boto3
import json

def handler(event, context):
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))

        if not all(k in body for k in ['car_id', 'start_date', 'end_date']):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'car_id and start_date are required fields'})
            }
    except Exception as e:
        print(f"Error creating car: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Could not create car'})
        }

