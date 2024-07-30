"""
Data pipeline: Create Lambda to support Transfer Family for Fetch & Dispatch

Description:-
This Lambda should implement the compare fetch, files and get, remote files status functions as defined in 
Specs for Fetch & Dispatch lambda.docx,This will allow us to implement STEP functions to perform the Fetch 
and Dispatch functionality leveraging the AWS Transfer Family connectors
"""

import json
import os
import sys 
from pip._internal import main

main(['install', '-I', '-q', 'boto3', '--target', '/tmp/', '--no-cache-dir', '--disable-pip-version-check'])
sys.path.insert(0, '/tmp/')

import boto3
from botocore.exceptions import NoCredentialsError
import time
from datetime import datetime

# Initialize the clients
s3_client = boto3.client('s3')
transfer_client = boto3.client('transfer', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        input_data = event
    except (KeyError, TypeError, json.JSONDecodeError):
        return {
            "statusCode": 404,
            "body": json.dumps({"status": "FAILURE", "message": "Bad request: Invalid JSON"})
        }

    request_type = input_data.get("request_type")
    if request_type == "compare_fetch_files":
        return compare_fetch_files(input_data)
    elif request_type == "get_remote_file_status":
        return get_remote_file_status(input_data)
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"status": "FAILURE", "message": "Invalid request type"})
        }

def compare_fetch_files(input_data):
    required_keys = ["connector_id", "sftp_directory", "dest_bucket"]
    for required_key in required_keys:
        if required_key not in input_data:
            return {
                "statusCode": 404,
                "body": json.dumps({"status": "FAILURE", "message": f"Key '{required_key}' not found in request body", "files": []})
            }

    connector_id = input_data['connector_id']
    sftp_directory = input_data['sftp_directory']
    file_filter = input_data.get('file_filter', "")
    dest_bucket = input_data['dest_bucket']
    s3_key_prefix = input_data.get('dest_key', "")

    sftp_entries = list_files_and_directories_in_sftp(connector_id, sftp_directory, dest_bucket)
    s3_files = list_files_in_s3(dest_bucket, s3_key_prefix)
    processed_files = [file for file in s3_files if file.startswith('processed/')]

    t1 = datetime.now()
    files_list = []
    if s3_key_prefix:
        for entry in sftp_entries:
            if entry['type'] == 'FILE' and (f"{s3_key_prefix}/{entry['name']}" not in s3_files) and (f"{s3_key_prefix}/processed/{entry['name']}" not in processed_files):
                if match_file_filter(entry['name'], file_filter):
                    files_list.append(entry['name'])
                    # copy_file_to_s3(connector_id, entry['path'], dest_bucket, f"{s3_key_prefix}/{entry['name']}")
    else:
        for entry in sftp_entries:
            if entry['type'] == 'FILE' and (entry['name'] not in s3_files) and (f"processed/{entry['name']}" not in processed_files):
                if match_file_filter(entry['name'], file_filter):
                    files_list.append(entry['name'])
                # copy_file_to_s3(connector_id, entry['path'], dest_bucket, f"{s3_key_prefix}/{entry['name']}")
            elif entry['type'] == 'DIRECTORY':
                pass

    print("Time taken")
    print(datetime.now() - t1)

    return {
        'statusCode': 200,
        "body": json.dumps({"status": "SUCCESS", "message": "", "files": files_list})
    }

def get_remote_file_status(input_data):
    required_keys = ["connector", "src_folder", "file_name","dest_bucket"]
    for required_key in required_keys:
        if required_key not in input_data:
            return {
                "statusCode": 404,
                "body": json.dumps({"status": "FAILURE", "message": f"Key '{required_key}' not found in request body"})
            }

    connector_id = input_data['connector']
    src_folder = input_data['src_folder']
    file_name = input_data['file_name']
    dest_bucket = input_data['dest_bucket']

    try:
        response = transfer_client.start_directory_listing(
            ConnectorId=connector_id,
            RemoteDirectoryPath=src_folder,
            OutputDirectoryPath=f'/{dest_bucket}/output'
        )
    
        output_file_name = response['OutputFileName']
        json_file_key = f"output/{output_file_name}"
        json_file_found = False
        print("Waiting for the JSON file to be available in S3...")
    
        while not json_file_found:
            response = s3_client.list_objects_v2(Bucket=dest_bucket, Prefix='output')
            json_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'] == json_file_key]
            if json_files:
                json_file_found = True
            else:
                print("JSON file not found, waiting for 10 seconds...")
                time.sleep(3)
    
        response = s3_client.get_object(Bucket=dest_bucket, Key=json_file_key)
        json_content = response['Body'].read().decode('utf-8')
        directory_listing = json.loads(json_content)
    
        for path in directory_listing.get('files', []):
            if os.path.basename(path['filePath']) == file_name:
                file_size = path['size']
                
                # Delete the JSON file after processing
                s3_client.delete_object(Bucket=dest_bucket, Key=json_file_key)
                print(f"Deleted JSON file: {json_file_key}")
                return {
                    "statusCode": 200,
                    "body": json.dumps({"status": "SUCCESS", "file_name": file_name, "file_size": file_size})
                }
                
        # Delete the JSON file if the file name is not found
        s3_client.delete_object(Bucket=dest_bucket, Key=json_file_key)
        print(f"Deleted JSON file: {json_file_key}")
    
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "FAILURE", "file_name": "", "file_size": 0})
        }

    except Exception as e:
        print(f"Failed to get file status from SFTP: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "FAILURE", "message": str(e)})
        }

def match_file_filter(filename, file_filter):
    if file_filter.startswith('*') and file_filter.endswith('*'):
        return file_filter[1:-1] in filename
    elif file_filter.startswith('*'):
        return filename.endswith(file_filter[1:])
    elif file_filter.endswith('*'):
        return filename.startswith(file_filter[:-1])
    else:
        return file_filter in filename

def list_files_and_directories_in_sftp(connector_id, directory, output_bucket):
    try:
        response = transfer_client.start_directory_listing(
            ConnectorId=connector_id,
            RemoteDirectoryPath=directory,
            OutputDirectoryPath=f'/{output_bucket}/output'
        )
        print(response)

        output_file_name = response['OutputFileName']
        json_file_key = f"output/{output_file_name}"
        json_file_found = False
        print("Waiting for the JSON file to be available in S3...")

        while not json_file_found:
            response = s3_client.list_objects_v2(Bucket=output_bucket, Prefix='output')
            json_files = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'] == json_file_key]
            if json_files:
                json_file_found = True
            else:
                print("JSON file not found, waiting for 10 seconds...")
                time.sleep(3)

        print(f"JSON file found: {json_file_key}")

        response = s3_client.get_object(Bucket=output_bucket, Key=json_file_key)
        json_content = response['Body'].read().decode('utf-8')
        directory_listing = json.loads(json_content)

        entries = []
        for path in directory_listing.get('files', []):
            entry_type = 'FILE'
            entry_path = path['filePath']
            entry_name = os.path.basename(entry_path)
            entries.append({'name': entry_name, 'type': entry_type, 'path': entry_path})
                
        # Delete the JSON file after processing
        s3_client.delete_object(Bucket=output_bucket, Key=json_file_key)
        print(f"Deleted JSON file: {json_file_key}")
        return entries
    except Exception as e:
        print(f"Failed to list files in SFTP: {str(e)}")
        return []




def list_files_in_s3(bucket_name, s3_key_prefix):
    try:
        files = []
        paginator = s3_client.get_paginator('list_objects_v2')
        operation_parameters = {
            'Bucket': bucket_name,
            'Prefix': s3_key_prefix
        }
        for page in paginator.paginate(**operation_parameters):
            if 'Contents' in page:
                files.extend([item['Key'] for item in page['Contents']])
        print(files)
        return files
    except NoCredentialsError:
        print("Credentials not available")
    except Exception as e:
        print(f"Some error occurred. Details: {str(e)}")
        return []



def copy_file_to_s3(connector_id, remote_path, bucket_name, s3_key):
    try:
        print("------Processing file -----")
        print(s3_key)
        if s3_key == "":
            path = f"/{bucket_name}/{s3_key}"
        else:
            path = f"/{bucket_name}"
        print(remote_path)

        response = transfer_client.start_file_transfer(
            ConnectorId=connector_id,
            RetrieveFilePaths=[remote_path],
            LocalDirectoryPath=path
        )
        print(f"Started file transfer: {response}")
    except Exception as e:
        print(f"Failed to copy file to S3: {str(e)}")
