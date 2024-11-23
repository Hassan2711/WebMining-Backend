# from pyairtable import Api
# import os

# AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
# AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')


# class Airtable:
#     def __init__(self):
#         self.api = Api(AIRTABLE_API_KEY)

#     def save_to_ba_trips(self, data):
#         table = self.api.table(AIRTABLE_BASE_ID, 'BA Trips')
#         for record in data:
#             new_record = table.create({
#                 'Name': record['Name'],
#                 'Notes': f'{record}',
#                 'Status': 'Done'
#             })
#             print("Record saved to BA Trips:", new_record)

#     def save_to_local_work(self, data):
#         table = self.api.table(AIRTABLE_BASE_ID, 'Local Work')
#         for record in data:
#             new_record = table.create({
#                 'Name': record.get('Name', '-'),
#                 'Notes': f'{record}',
#                 'Status': 'Done'
#             })
#             print("Record saved to Local Work:", new_record)
