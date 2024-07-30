from simplegmail import Gmail

gmail = Gmail()

# sample_email = """
# Hi, Dr Verma,

# My name is Sumay Chatterjee and i want to thanks that after I have taken your therapy I really feels very good and it was my really awseom 
# experence. But I not only write the mail to thank you as I want to help you to grow your bussiness in the large scale where you will get
# much more client than of now. Let me tell you I am expert in the skills of Digital Marketing where i can do a good SEO, Email-Marketing, blog
# write and much more. I can help you in the do Insta and Facebook Advertising and not only this as i will it in the Youtube also.

# I am waiting for your respone 

# Thanks
# Sumay Chatterjee

# """

sender_email=""
def send_email(recipient,subject,message):
    message = message.replace("\n","<br>")
    params = {
        "to":recipient,
        "sender":sender_email,
        #"subject":subject,
        "msg_html":message,
        #"msg_plain":"Hi",
        #"signature":True
    }


    message = gmail.send_message(**params)
    print("Message Sent")