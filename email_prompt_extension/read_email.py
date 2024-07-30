from simplegmail import Gmail
from simplegmail.query import construct_query

gmail = Gmail()


## Message that are newer than 2 day old, unread, label
query_params = {
    "newer_than": (1, "year"),
    "older_than": (0, "year")
}
print(query_params)

# Retrieve sent messages matching the query
messages = gmail.get_sent_messages(query=construct_query(query_params))
print(f"Number of messages retrieved: {len(messages)}") 
print(messages)

# Construct the query using the parameters
query = construct_query(query_params)
print("Constructed Query: ", query)  # Debugging statement


# Retrieve sent messages matching the query


for message in messages:
    print("To: " + message.recipient)
    print("From: " + message.sender)
    print("Subject: "+ message.subject)
    print("Date: " + message.date)
    print("Preview: " + message.snippet)

    with open("email_sample.txt","a") as f:
        if message.plain:
            if len(message.plain) < 1000:
                f.write(message.plain)
