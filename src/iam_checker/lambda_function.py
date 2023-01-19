#!/usr/bin/env python3
'''IAM Checker Lambda Function'''

import boto3
import logging
import os
from aws_xray_sdk.core import patch_all, xray_recorder
from iam_checks import check_mfa_enabled, check_access_key_age, check_password_age, log_format

iam_client = boto3.client('iam')

log_level = os.environ.get('LOGGING_LEVEL', logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
patch_all()

@xray_recorder.capture('iam-checker')
def lambda_handler(event, context):
    '''Main function'''
    try:
        user_list = iam_client.list_users()

        logger.info(event)
        logger.info(context)
        log_format()

        logger.info("Running check_mfa_enabled")
        check_mfa_enabled(user_list)
        log_format()

        logger.info("Running check_access_key_age")
        check_access_key_age(user_list)
        log_format()

        logger.info("Running check_password_age")
        check_password_age(user_list)
        log_format()

        return "Completed IAM Checker"

    except Exception as e:
        logger.error(e)
        raise e
