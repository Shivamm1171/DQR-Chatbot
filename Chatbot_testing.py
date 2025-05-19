import pandas as pd
import os, shutil as sh
from chatbot import run
from send_email import send_email
import time
from chatbot import MODEL

start_time = time.time()

questions_df = pd.read_excel('DQR_Chatbot_test_questions.xlsx')
questions_df = questions_df.head(5)

if os.path.exists(fr'Automated Testing Results ({MODEL})/Markdown Files'):
    sh.rmtree(fr'Automated Testing Results ({MODEL})/Markdown Files')
os.makedirs(fr'Automated Testing Results ({MODEL})/Markdown Files', exist_ok=True)

for index, row in questions_df.iterrows():
    try:
        chat_history = run(name_input= 'Automated Testing', user_input= row['Test Question'])

        if chat_history and len(chat_history) > 0:  # Check if chat_history exists and has elements
            questions_df.loc[index, 'Test Answer'] = chat_history[-1]['content']
        else:
            questions_df.loc[index, 'Test Answer'] = "No response generated"
            
        filename = os.path.join(f"Automated Testing Results ({MODEL})", "Markdown Files", f"Question_{index+1}_{row['Difficulty Level']}.md")

        with open(filename, 'w') as f:
            for message in chat_history:
                if message["role"] == "user":
                    f.write(f"**You:** {message['content']}\n\n")
                elif message["role"] == "function":
                    f.write(f"**Function** {message['content']}\n\n")
                elif message["role"] == "assistant":
                    f.write(f"**DQR Bot:** {message['content']}\n\n")
    except Exception as e:
        questions_df.loc[index, 'Test Answer'] = f"Error: {e}"
        filename = os.path.join(f"Automated Testing Results ({MODEL})", "Markdown Files", f"Question_{index+1}_{row['Difficulty Level']}_error.md")
        with open(filename, 'w') as f:
            f.write(f"**Error:** {e}")

questions_df.to_excel(f'Automated Testing Results ({MODEL})/DQR_Chatbot_test_questions_with_answers.xlsx', index=False)

end_time = time.time()
time_taken = round(end_time - start_time, 2)

sh.make_archive(f'Automated Testing Results ({MODEL})', 'zip', f'Automated Testing Results ({MODEL})')

attachment_path = f"Automated Testing Results ({MODEL}).zip"

mail_subject = f"DQR Chatbot Automated Testing Results - Model ({MODEL})"
mail_body = f"Please find the results of the automated testing in the attached file. Time taken: {time_taken} seconds"

send_email(mail_subject, mail_body, attachment_path)   

os.remove(attachment_path)


 