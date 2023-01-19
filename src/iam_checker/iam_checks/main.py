'''Module for checking IAM users and access keys'''

import boto3
import logging
import os
import re
import random
import array
from datetime import datetime

iam_client = boto3.client('iam')
ses_client = boto3.client('ses')

log_level = os.environ.get('LOGGING_LEVEL', logging.INFO)
max_key_age = os.environ.get('MAX_KEY_AGE')

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
date_now = datetime.now()

def check_mfa_enabled(user_list):
    '''Checks if MFA is enabled for all users'''
    user_list_without_mfa = []
    for user in user_list['Users']:
        list_mfa_devices = iam_client.list_mfa_devices(UserName=user['UserName'])
        if list_mfa_devices['MFADevices'] == []:
            user_list_without_mfa.append(user['UserName'])
            logger.info(f"{user['UserName']} has no mfa devices enabled")
            send_email(user['UserName'], "MFA is not enabled on your AWS account. Please enable an MFA device as soon as possible", max_key_age)
        else:
            logger.debug(f"{user['UserName']} has mfa enabled")
            
    remove_from_user_group(user_list_without_mfa)
    return user_list_without_mfa
 
def check_access_key_age(user_list):
    '''Checks if access keys are older than 90 days'''
    expired_keys = []
    for user in user_list['Users']:
        access_keys = iam_client.list_access_keys(UserName=user['UserName'])
        if 'AccessKeyMetadata' in access_keys:
                for key in access_keys['AccessKeyMetadata']:
                    # created_date = key['CreateDate'].replace(tzinfo=None)
                    key_id = key['AccessKeyId']
                    key_age = get_key_age(key)
                    if key_age == int(max_key_age)/2:
                        logger.info(f"{user['UserName']} access key {key_id} is older than {int(max_key_age) / 2} days")
                        send_email(user['UserName'], f"Your AWS Access key: {key_id} is {int(max_key_age) / 2} days old. Access keys expire after 90 days.", max_key_age)
                    elif key_age == int(max_key_age)/1.5:
                        logger.info(f"{user['UserName']} access key {key_id} is older than {int(max_key_age) / 1.5} days")
                        send_email(user['UserName'], f"Your AWS Access key: {key_id} is {int(max_key_age) / 1.5} days old. Access keys expire after 90 days.", max_key_age)
                    elif key_age == int(max_key_age)/1.2:
                        logger.info(f"{user['UserName']} access key {key_id} is older than {int(max_key_age) / 1.2} days")
                        send_email(user['UserName'], f"Your AWS Access key: {key_id} is {int(max_key_age) / 1.2} days old. Access keys expire after 90 days. Please rotate your access key as soon as possible. It will be deleted after {max_key_age}.", max_key_age)
                    elif key_age >= int(max_key_age):
                        expired_keys.append(key_id)
                        logger.info(f"{user['UserName']} access key {key_id} is older than {int(max_key_age)} days")
                        disable_access_key(key_id, user['UserName'])
                        send_email(user['UserName'], f"Your AWS Access key: {key_id} is {int(max_key_age)} days old. Access keys expire after 90 days. Your access key has been deleted, please login to the console to create a new one.", max_key_age)
    
    return expired_keys

def get_key_age(key):
    created_date = key['CreateDate'].replace(tzinfo=None)
    difference = date_now - created_date
    return difference.days


def check_password_age(user_list):
    '''Checks if password is older than 90 days or a multiple of 90 days'''
    expired_passwords = []
    for user in user_list['Users']:
        if 'PasswordLastUsed' in user:
            last_used_date = user['PasswordLastUsed'].replace(tzinfo=None)
            difference = date_now - last_used_date
            if difference.days == 30:
                send_email(user['UserName'], "You have not logged into AWS console in more than 30 days. AWS Password expire after 90 days, please ensure you rotate your password", max_key_age)
                logger.info(f"Sent email to {user} to notify they haven't logged into console 30 days")
            if difference.days == 60:
                send_email(user['UserName'], "You have not logged into AWS console in more than 60 days. AWS Password expire after 90 days, please ensure you rotate your password", max_key_age)
                logger.info(f"Sent email to {user} to notify they haven't logged into console 60 days")
            if difference.days % 90 == 0 & difference.days != 0:
                expired_passwords.append(user)
                password = reset_user_password(user['UserName'])
                send_email(user['UserName'], f"You have not logged into AWS console in more than 90 days. Your AWS Password has expired, this is your temporary password: {password} please log in to reset", max_key_age)
                logger.info(f"Sent email to {user} to notify they haven't logged into console 90 days, there password has been reset and action is required")
    
    return expired_passwords

def disable_access_key(key_id, user):
    '''Disables and deletes access keys older than 90 days'''
    iam_client.update_access_key(
        UserName=user,
        AccessKeyId=key_id,
        Status='Inactive'
    )
    iam_client.delete_access_key(
        UserName=user,
        AccessKeyId=key_id
    )
    logger.info(f"Deleting access key {key_id} belonging to user: {user}")
    return f"Deleted access key {key_id} belonging to user: {user}"

def send_email(name, credential_alert, max_key_age):
    '''Sends email to user'''
    email_regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(email_regex, name):
        response = ses_client.send_templated_email(
            Source='automation@example.uk',
            Destination={'ToAddresses': [
                name
            ]},
            Template='iam-checker-credential-alert',
            TemplateData='{"credential_alert":"'+credential_alert+'", "name":"'+name+'", "max_key_age":"'+max_key_age+'"}'
        )
        logger.info(f"Sending email to {name}:{response}")
    else:
        response = f"{name} is not a valid email address"
        logger.info(f"{response}")
    return f"{response}"

def remove_from_user_group(user_list_without_mfa):
    '''Removes user from all groups except basic-user'''
    user_group_list = []
    for user in user_list_without_mfa:
        user_groups = iam_client.list_groups_for_user(
            UserName=user
        )
            
        for group in user_groups['Groups']:
            group_name = group['GroupName']
            user_group_list.append(group_name)
            if group_name != 'basic-user':
                logger.info(f"Removing {user} from {group_name} because MFA is not enabled on {user}")
                iam_client.remove_user_from_group(
                    GroupName = group_name,
                    UserName = user
                )
            else:
                logger.info(f"{user} has no other groups to remove")
        
        if 'basic-user' not in user_group_list:
            logger.info(f"Adding {user} to 'basic-user' so {user} can manage their password/MFA setup")
            iam_client.add_user_to_group(
                GroupName = 'basic-user',
                UserName = user
            )
        else:
            logger.info(f"{user} is already in 'basic-user' group")
    return user_group_list

def generate_strong_password(password_length):
    DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] 
    LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                        'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                        'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                        'z']
    
    UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                        'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                        'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                        'Z']
    
    SYMBOLS = ['@', '#', '$', '%', '?', '!', '*', '^', ]

    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS

    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)

    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

    for x in range(password_length - 4):
        temp_pass = temp_pass + random.choice(COMBINED_LIST)
 
        temp_pass_list = array.array('u', temp_pass)
        random.shuffle(temp_pass_list)

        password = ""
        for x in temp_pass_list:
                password = password + x
    return password

def check_user_profile(user, password):
    '''Check if the user has a login profile, create one for them if it doesn't exist'''
    new_profile = False
    try:
        login_profile = iam_client.get_login_profile(
            UserName=user
        )
    except iam_client.exceptions.NoSuchEntityException:
        logger.info(f'Creating a login profile for {user}')
        login_profile = iam_client.create_login_profile(
            UserName=user,
            Password=password,
            PasswordResetRequired=False
        )
        new_profile = True
    except Exception as e:
        logger.info(f'{e}')
        raise e
    return new_profile

def reset_user_password(user):
    '''Resets user password'''
    password = generate_strong_password(14)
    print(f"Generating password {password}")
    
    new_profile = check_user_profile(user, password)
    if new_profile == False:
        response = iam_client.update_login_profile(
            UserName=user,
            Password=password,
            PasswordResetRequired=True
        )
        logger.info(f"Resetting password for {user}:{response}")

    return password

def log_format():
    print("-------------------------")
