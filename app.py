import json
import boto3
import logging
from datetime import datetime
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'EventMonitoringTable'

def lambda_handler(event, context):
    """
    AWS Lambda function to process CloudWatch Events for S3 and EC2 monitoring
    Stores event details in DynamoDB table
    """
    
    try:
        logger.info(f"Received event: {json.dumps(event, indent=2)}")
        
        # Extract event details
        event_time = event.get('time', datetime.utcnow().isoformat())
        event_source = event.get('source', 'unknown')
        event_name = event.get('detail-type', 'unknown')
        region = event.get('region', 'unknown')
        
        # Initialize variables
        resource_name = 'unknown'
        username = 'unknown'
        
        # Parse event details based on source
        detail = event.get('detail', {})
        
        if event_source == 'aws.s3':
            # S3 Events
            if 'requestParameters' in detail:
                bucket_name = detail.get('requestParameters', {}).get('bucketName')
                if bucket_name:
                    resource_name = bucket_name
            
            # Extract username from userIdentity
            user_identity = detail.get('userIdentity', {})
            username = extract_username(user_identity)
            
        elif event_source == 'aws.ec2':
            # EC2 Events
            if 'instance-id' in detail:
                resource_name = detail.get('instance-id', 'unknown')
            
            # For EC2 state changes, username might not be directly available
            # But we can try to extract from userIdentity if present
            user_identity = detail.get('userIdentity', {})
            username = extract_username(user_identity)
        
        # Prepare DynamoDB item
        item = {
            'EventId': f"{event_source}-{int(datetime.utcnow().timestamp())}-{hash(str(event)) % 10000}",
            'EventTime': event_time,
            'EventSource': event_source,
            'EventName': event_name,
            'ResourceName': resource_name,
            'Region': region,
            'Username': username,
            'RawEvent': json.dumps(event, default=str)  # Store full event for debugging
        }
        
        # Store in DynamoDB
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
        
        logger.info(f"Successfully stored event in DynamoDB: {item['EventId']}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Event processed successfully',
                'eventId': item['EventId']
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to process event',
                'details': str(e)
            })
        }

def extract_username(user_identity):
    """
    Extract username from userIdentity object
    """
    if not user_identity:
        return 'system'
    
    # Try different fields where username might be stored
    username = (
        user_identity.get('userName') or
        user_identity.get('arn', '').split('/')[-1] or
        user_identity.get('principalId', '').split(':')[-1] or
        user_identity.get('type', 'unknown')
    )
    
    return username if username else 'system'
