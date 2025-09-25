import boto3
import csv
import json

# List all tables first
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
tables = dynamodb.list_tables()['TableNames']
print("Available tables:", tables)

# Find skills assessment table
skills_table = None
for table_name in tables:
    if 'SkillsAssessment' in table_name:
        skills_table = table_name
        break

if not skills_table:
    print("No SkillsAssessment table found")
    exit()

print(f"Using table: {skills_table}")

# Export DynamoDB to CSV
dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb_resource.Table(skills_table)

response = table.scan()
items = response['Items']

# Create CSV file
with open('skills-data.csv', 'w', newline='') as csvfile:
    if items:
        fieldnames = items[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)

print("CSV exported: skills-data.csv")