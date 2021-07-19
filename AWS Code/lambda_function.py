import json
import boto3
import email
import os
from io import StringIO
from sms_spam_classifier_utilities import * 

def lambda_handler(event, context):
    
    key = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    
    #ENDPOINT_NAME = "sms-spam-classifier-mxnet-2021-04-02-22-42-46-718"
    ENDPOINT_NAME = os.environ['SAGEENDPOINT']
    print("ENDPOINT_NAME",str(ENDPOINT_NAME))
    s3 = boto3.client('s3')
    runtime = boto3.client('runtime.sagemaker')
    ses_client = boto3.client('ses')
    
    
    original = s3.get_object(
        Bucket = bucket_name,
        Key = key
        )

    msg = email.message_from_bytes(original['Body'].read())
    
    from_name, from_address = email.utils.parseaddr(msg["from"])
    
    EMAIL_FROM = ""
    EMAIL_SUBJECT = msg['Subject']
    EMAIL_RECEIVE_DATE = str(msg['Date'])
    email_content_for_replying = ""
    email_body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            try:
                body = part.get_payload(decode=True).decode()
            except:
                pass
            if content_type == "text/plain" and "attachment" not in content_disposition:

                email_content_for_replying = body
                email_body = body.replace("\n","")
    else:
        # extract content type of email
        content_type = msg.get_content_type()
        # get the email body
        body = msg.get_payload(decode=True).decode()
        if content_type == "text/plain":
            email_content_for_replying = body
            email_body = body.replace("\n","")
            print("Content(Type 2): ")
        
    
    test_messages = [email_body]
    vocabulary_length = 9013
    one_hot_test_messages = one_hot_encode(test_messages,vocabulary_length)
    encoded_test_messages = vectorize_sequences(one_hot_test_messages,vocabulary_length)
    io = StringIO()
    json.dump(encoded_test_messages.tolist(),io)
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                       #ContentType='application/python-pickle',
                                       Body=bytes(io.getvalue(),'utf-8'))

    content = json.loads(response['Body'].read().decode())
    
    predicted_label = content['predicted_label'][0][0]
    predicted_probability = content['predicted_probability'][0][0]

    CLASSIFICATION = ""
    CLASSIFICATION_CONFIDENCE_SCORE = str(predicted_probability * 100) + "%"
    if predicted_label == 1.0 :
        CLASSIFICATION = "spam"
    if predicted_label != 1.0 :
        CLASSIFICATION = "ham"
        

    date_str = "We received your email sent at " + EMAIL_RECEIVE_DATE + " with the subject " + EMAIL_SUBJECT + ".\n\n"
    
    content_str = "Here is a 240 character sample of the email body:\n" + email_content_for_replying + "\n"

    classification_str = "The email was categorized as " + CLASSIFICATION + " with a " + CLASSIFICATION_CONFIDENCE_SCORE + " confidence.\n"

    final_str = date_str + content_str + classification_str

    
    ses_reponse = ses_client.send_email(
        Source = "spam_email_checker@columbiacoolkids.com",
        Destination = {
            'ToAddresses':[
                from_address,
            ],
        },
        Message = {
            'Subject':{
                'Data':"Result for spam email checking is here!"
            },
            'Body':{
                'Text':{
                    'Data':final_str
                },
            },
            
        },
        
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
