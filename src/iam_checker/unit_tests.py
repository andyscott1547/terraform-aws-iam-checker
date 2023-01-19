import boto3
import os
from moto import mock_iam

os.environ['MAX_KEY_AGE'] = '90'

AWS_ACCESS_KEY_ID='testing'
AWS_SECRET_ACCESS_KEY='testing'
AWS_SECURITY_TOKEN='testing'
AWS_SESSION_TOKEN='testing'
AWS_DEFAULT_REGION='eu-west-1'

def test_generate_strong_password():
    from iam_checks import main
    response = main.generate_strong_password(14)
    assert len(response) == 14

@mock_iam()
def test_check_user_profile_false():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_login_profile(
        UserName="test@test.com", 
        Password="my-pass"
    )

    is_new_profile = main.check_user_profile("test@test.com", "new-pass")

    assert is_new_profile == False

@mock_iam()
def test_check_user_profile_true():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    is_new_profile = main.check_user_profile("test@test.com", "new-pass")

    assert is_new_profile == True

@mock_iam()
def test_reset_user_password():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    password = main.reset_user_password("test@test.com")

    assert len(password) == 14

@mock_iam()
def test_remove_from_user_group_none():
    from iam_checks import main

    user_list_without_mfa = []

    response = main.remove_from_user_group(user_list_without_mfa)

    assert response == []


@mock_iam()
def test_remove_from_user_group():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_login_profile(
        UserName="test@test.com", 
        Password="my-pass"
    )

    iam_client.create_group(
        GroupName='test-user'
    )

    iam_client.create_group(
        GroupName='new-group'
    )

    iam_client.add_user_to_group(
        GroupName='test-user',
        UserName='test@test.com'
    )
    
    iam_client.add_user_to_group(
        GroupName='new-group',
        UserName='test@test.com'
    )

    user_list_without_mfa = ["test@test.com"]

    main.remove_from_user_group(user_list_without_mfa)
    response = iam_client.list_groups_for_user(
        UserName='test@test.com'
    )

    assert len(response['Groups']) == 1
    assert response['Groups'][0]['GroupName'] == "test-user"

@mock_iam()
def test_disable_access_key():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    key = iam_client.create_access_key(
        UserName='test@test.com'
    )

    key_id = key['AccessKey']['AccessKeyId']

    response = main.disable_access_key(key_id, "test@test.com")

    assert response == f"Deleted access key {key_id} belonging to user: test@test.com"

@mock_iam()
def test_check_password_age():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_login_profile(
        UserName="test@test.com", 
        Password="my-pass"
    )

    user_list = iam_client.list_users()

    response = main.check_password_age(user_list)

    assert response == []

@mock_iam()
def test_check_mfa_enabled():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_virtual_mfa_device(
        VirtualMFADeviceName='test',
    )

    iam_client.enable_mfa_device(
        UserName='test@test.com',
        SerialNumber='arn:aws:iam::123456789012:mfa/test',
        AuthenticationCode1='123456',
        AuthenticationCode2='123456'
    )

    test = iam_client.list_mfa_devices(UserName="test@test.com")

    user_list = iam_client.list_users()

    response = main.check_mfa_enabled(user_list)

    assert response == []

@mock_iam()
def test_check_mfa_enabled_send_email():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_virtual_mfa_device(
        VirtualMFADeviceName='test',
    )

    iam_client.create_group(
        GroupName='test-user'
    )

    test = iam_client.list_mfa_devices(UserName="test@test.com")
    user_list = iam_client.list_users()

    response = main.check_mfa_enabled(user_list)

    assert response == ["test@test.com"]

@mock_iam()
def test_check_access_key_age():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_access_key(
        UserName='test@test.com'
    )

    user_list = iam_client.list_users()

    response = main.check_access_key_age(user_list)

    assert response == []

@mock_iam()
def test_check_access_key_age():
    from iam_checks import main

    iam_client = boto3.client('iam')

    iam_client.create_user(
        UserName="test@test.com"
    )

    iam_client.create_access_key(
        UserName='test@test.com'
    )

    user_list = iam_client.list_users()

    response = main.check_access_key_age(user_list)

    assert response == []

@mock_iam()
def test_send_email_invalid():
    from iam_checks import main

    ses_client = boto3.client('ses')
    response = main.send_email('test', 'message', '20')

    assert response == "test is not a valid email address"

@mock_iam()
def test_send_email_valid():
    from iam_checks import main

    ses_client = boto3.client('ses')
    response = main.send_email('test@test.com', 'message', '20')

    assert '\'HTTPStatusCode\': 200' in response

# @mock_iam()
# def test_get_key_age():
#     from iam_checks import main

#     iam_client = boto3.client('iam')
#     key = [
#         {
#             'UserName': 'string',
#             'AccessKeyId': 'string',
#             'Status': 'Active'|'Inactive',
#             'CreateDate': datetime(2015, 1, 1)
#         }
#     ]

#     # key_age = main.get_key_age(key)

#     print(key)
