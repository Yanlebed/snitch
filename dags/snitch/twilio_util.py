from twilio.rest import Client

account_sid = "AC057d64e3f33b9261e427b02e7a76a52a"
auth_token = "420394989ca22e5e6d21d28788d3fb2d"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+380939326347",
    from_="+14092047746",
    body="Hello from Python!")

call = client.calls.create(to="+380939326347", from_="+14092047746", url='http://demo.twilio.com/docs/voice.xml',)

print(message.sid)
print(call.sid)
