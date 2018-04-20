from twilio.rest import Client


# Find these values at https://twilio.com/user/account
account_sid = "AC9258a6c8079e2fcf7377efea116a21d2"
auth_token = "870c744647b8e3659acb12dc48ddb146"

client = Client(account_sid, auth_token)

client.api.account.messages.create(
    to="+15104184140",
    from_="+14153608388",
    body="Hello there!")
