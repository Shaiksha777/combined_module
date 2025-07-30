import csv
import random

Question_ID = []
with open('temp.csv','r',newline='') as f:
    reader = csv.DictReader(f,skipinitialspace=True)
    for row in reader:
        Question_ID.append(row['Question_ID'])

emails = {}
with open('email.csv','r',newline='') as f:
    mails = csv.DictReader(f,skipinitialspace=True)
    for mail in mails:
        emails[mail['Email']] = 0
    
if len(emails) > len(Question_ID):
    for i in range(len(emails) - len(Question_ID)):
        Question_ID.append(Question_ID[i])
for mail in emails:
    try:
        question = random.choice(Question_ID)
        emails[mail] = question
        Question_ID.remove(question)

    except Exception as e:
        
        print('something went wrong, Trying to fix it :)')
        with open('error_logs.txt','a') as file:
            file.write(f'error was {e} occured at the time - \n')
        

print(emails)

