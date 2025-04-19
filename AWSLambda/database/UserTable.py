class Users:
    def __init__(self, dyn_resource):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.dyn_resource = dyn_resource
        # The table variable is set during the scenario in the call to
        # 'exists' if the table exists. Otherwise, it is set by 'create_table'.
        self.table = None


    def create_table(self, table_name):
        """
        Creates an Amazon DynamoDB table that can be used to store movie data.
        The table uses the release year of the movie as the partition key and the
        title as the sort key.

        :param table_name: The name of the table to create.
        :return: The newly created table.
        """
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "first_name", "KeyType": "RANGE"},  # Sort key
                    {"AttributeName": "last_name", "KeyType": "RANGE"},  # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "N"},
                    {"AttributeName": "first_name", "AttributeType": "S"},
                    {"AttributeName": "last_name", "AttributeType": "S"},
                    {"AttributeName": "email", "AttributeType": "S"},
                    {"AttributeName": "phone_number", "AttributeType": "S"},
                    {"AttributeName": "password_hash", "AttributeType": "S"}
                ],
                BillingMode='PAY_PER_REQUEST',
            )
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s",
                table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return self.table

