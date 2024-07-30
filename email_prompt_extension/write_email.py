import os
import openai
import json

# Uncomment this line if you want to use an environment variable for the API key
# openai.api_key = os.getenv("OPENAI_API_KEY")

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


system_prompt = """
Please Write an email in the style of the user given a prompt and the sample email
Please add the subject also 
Sign the email as an Sumay Chatterjee



Hi Mrs. Sharma,

Sorry for the late response; I Forget to send the email earlier. My Presentation is about Social Welfare where we detail to give classes
regarding the How to overcome from the Depression or What are the right path to be good person and sometime also we make the presentation 
on what we can do for the environment.

Thanks
Sumay Chaatterjee

Hi, Dr Verma,

My name is Sumay Chatterjee and i want to thanks that after I have taken your therapy I really feels very good and it was my really awseom 
experence. But I not only write the mail to thank you as I want to help you to grow your bussiness in the large scale where you will get
much more client than of now. Let me tell you I am expert in the skills of Digital Marketing where i can do a good SEO, Email-Marketing, blog
write and much more. I can help you in the do Insta and Facebook Advertising and not only this as i will it in the Youtube also.

I am waiting for your respone 

Thanks
Sumay Chatterjee
"""


def create_email():
    try:
    
        user_prompt = input("Describe the email you want: \n")
        messages = [
                {"role":"system","content":system_prompt},
                {"role": "user", "content":user_prompt}    
            ]

        def write_email(prompt):
                messages.append({"role": "user", "content":prompt})
                completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        engine="GPT35",
                        messages=messages
                )
                
                reply = completion.choices[0].message['content']
                print(reply)

                messages.append({"role": "assistant", "content":reply})
                return input("Please type quit or q and press Enter if satisfied, if not, continue prompting: \n")

        while user_prompt not in ["quit","q"]:
                user_prompt = write_email(user_prompt)
        
        final_draft = messages[-1]["content"]
        return final_draft


    except openai.error.APIError as e:
        print(f"APIError: {e}")
        print(e.http_body)
    except openai.error.InvalidRequestError as e:
        print(f"InvalidRequestError: {e}")
        print(e.http_body)
    except openai.error.AuthenticationError as e:
        print(f"AuthenticationError: {e}")
    except openai.error.OpenAIError as e:
        print(f"OpenAIError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
