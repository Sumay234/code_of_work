import pandas as pd
import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import boto3
from botocore.exceptions import ClientError


# Set up Azure OpenAI API configuration
openai.api_type = "azure"
openai.api_base = "https://openai231123.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = "24e4ce2aabc34ed9a63812fabe60a79e"


engine = "GPT35"
temperature = 0.7
max_tokens = 500
top_p = 0.95
frequency_penalty = 0
presence_penalty = 0
stop = None


def read_excel(file_path):
    """
    Reads data from an Excel file and returns it as a DataFrame.
    
    Args:
        file_path (str): The path to the Excel file.
    
    Returns:
        pd.DataFrame: DataFrame containing the data from the Excel file.
    """
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Strip any leading/trailing spaces from column names
    return df


def generate_personalized_email(name, email,company,industry,sector ):
    """
    Generates personalized email content using OpenAI's API based on provided information.
    
    Args:
        name (str): The recipient's name.
        email (str): The recipient's email address.
        other_info (dict): Dictionary containing other relevant information for personalization.
         (str): Personal message to include at the beginning of the email.
    
    Returns:
        str: The generated personalized email content.
    """
    prompt = (
        f"Write a Short email to {name}"
        f"First highlight the key challenges faced by companies in this sector and explain how Ai Talker can address these challenges.on how Ai Talker is effective, cost-efficient, and how it can improve operational efficiency. \n"
        f"First highlight the key challenges faced by companies in this sector"
        f"Include details on how AI Talker is effective"
        f"company: {company}\n" 
        f"Industry: {industry} \n"
        f"Sector: {sector}\n"
        f"Name: Ai Talker, which is a voice-based interaction tool for businesses to handle conversations\n"
        f"Ai Talker Details:\n"
        f"Use Cases: presales, sales, customer onboarding, customer support, survey\n"
        f"Features: 24/7 responses, multi-linguaal, personalized, efficient, insightful, easy integration, always available, future-proof\n" 
        f"Benefits: Personalize instant customer support, available on demand, scalable to meet growth, increase efficiency and productivity\n"
        f"Start the email with a greeting and end with the signature of CEO Shasharik Singh of Aiverbalyze Technologies Pvt. Ltd."
    ) or (
        f"Write a concise email to {name} highlighting the primary obstacles companies face in customer interaction within the  sector.\n"
        f"Explain how AI Talker can effectively overcome these obstacles, improving customer satisfaction and operational efficiency.\n"
        f"Emphasize AI Talker's cost-effectiveness and key features such as 24/7 availability and multilingual support.\n"
        f"Include the company name: {company}, industry: {industry}, and sector: {sector}.\n"
        f"Conclude with a signature from CEO Shasharik Singh of Aiverbalyze Technologies Pvt. Ltd."
    ) or (
        f"Create a short email to {name}, discussing the prevalent challenges in the sector regarding customer interactions.\n"
        f"Detail how AI Talker can address these challenges by providing scalable, efficient, and personalized solutions.\n"
        f"Highlight its use cases like presales, customer onboarding, and support.\n"
        f"Include the company name: {company}, industry: {industry}, and sector: {sector}.\n"
        f"Sign off with the signature of CEO Shasharik Singh of Aiverbalyze Technologies Pvt. Ltd."
    ) or (
        f"Draft an email to {name}, focusing on the critical issues companies face in the sector related to customer interactions.\n"
        f"Explain how AI Talker's features, such as 24/7 responses and easy integration, can resolve these issues cost-effectively.\n"
        f"Include its benefits in enhancing customer support and operational productivity.\n"
        f"Include the company name: {company}, industry: {industry}, and sector: {sector}.\n"
        f"End with a signature from CEO Shasharik Singh of Aiverbalyze Technologies Pvt. Ltd."
    ) or (
        f"Compose a brief email to {name}, outlining the significant challenges companies encounter in managing customer interactions within the  sector.\n"
        f"Describe how AI Talker can effectively mitigate these challenges, offering insights and personalized support.\n"
        f"Highlight its ability to provide seamless integration and future-proof solutions.\n"
        f"Include the company name: {company}, industry: {industry}, and sector: {sector}.\n"
        f"Close with the signature of CEO Shasharik Singh of Aiverbalyze Technologies Pvt. Ltd."
    ) or (
        f"Create a brief email to {name}, discussing the major hurdles companies face in the  sector when it comes to customer interactions.\n"
        f"Describe how AI Talker can effectively tackle these issues, highlighting its features like 24/7 availability, multilingual support, and scalability.\n"
        f"Focus on the cost-efficiency and productivity improvements it offers.\n"
        f"Include the company name: {company}, industry: {industry}, and sector: {sector}.\n"
        f"Conclude with a signature from CEO Shasharik Singh of Aiverbalyze Technologies Pvt. Ltd."

    )



    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop
    )
 

# --> Note 1/2-A: If we use this than we will get the autogenerate msg from gpt-ai along with our personal message
    generated_content = response.choices[0].text.strip()
    full_email_content = f"{generated_content}"

    return full_email_content

# ---> Note 2/2-A : Now i am using this and we will get only the Personal Message which i added it.
    #full_email_content = f"{}"

#    return full_email_content


def send_email(to_email, subject, body, SENDERNAME):
    """
    Sends an email using SMTP.
    
    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
       
    
    """
    from_email = "shashank@verbalyze.in"  # Replace with your email address
  # from_password = "sumay@1999"  

    SMTP_USERNAME = 'AKIAXBTTUTZSUHU767GL'  # Replace with your SMTP username.
    SMTP_PASSWORD = 'BKC3p7WGIQ6ud2kVucwrrODJZubVYB28BbZ7cy7vjBCM'  # Replace with your SMTP password.
    HOST = "email-smtp.ap-south-1.amazonaws.com"  # The Amazon SES SMTP endpoint.
    PORT = 587

    # The subject line of the email.
    party_ = SENDERNAME

    subject = f"{party_}'s integration with conversational AI using Verbalyze."
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(HOST, PORT)  # Corrected SMTP server and port
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


def main():
    """
    Main function to read data from Excel, generate personalized emails, and send them.
    """
    # Path to the Excel file
    file_path = r"C:\Users\sumay\Downloads\ver\amazon_ses\seperated_files\sumay.xlsx"
    
    # Read data from Excel
    data = read_excel(file_path)
    
    # Print the columns of the DataFrame
    print("Columns in the DataFrame:", data.columns)


    
    # Loop through each row in the DataFrame
    for index, row in data.iterrows():
        try:
            name = row['name']
            email = row['email']
            company = row["company"]
            industry = row["industry"]
            sector = row["sector"]
        except KeyError as e:
            print(f"KeyError: {e}")
            continue
        other_info = row.drop(['name', 'email', 'company','industry','sector']).to_dict()


 
        # Generate personalized email
        email_content = generate_personalized_email(name, email,company,industry,sector )
        #email_content = generate_personalized_email(other_info,)
        
        # Send email
        #send_email(email, "Personalized Email", email_content, "Your SENDERNAME")
        send_email(email, "Personalized Email", email_content, "Your SENDERNAME")


if __name__ == "__main__":
    main()
