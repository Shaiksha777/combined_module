import csv
import json
import os
import random
from test_cases import generate_response


def assign_randomly():
        # Collect questions and their texts from uploaded questions CSV
        question_ids = []
        qid_to_text = {}
        with open('uploads/temp.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            for row in reader:
                qid = row.get('Question_ID')
                if not qid:
                    continue
                question_ids.append(qid)
                if 'Question' in row and row['Question']:
                    qid_to_text[qid] = row['Question']

        # Read emails list
        emails = {}
        with open('uploads/emails.csv', 'r', newline='', encoding='utf-8') as f:
            mails = csv.DictReader(f, skipinitialspace=True)
            for mail in mails:
                if mail.get('Email'):
                    emails[mail['Email']] = None

        # Ensure enough questions by cycling if fewer questions than emails
        if len(emails) > len(question_ids) and question_ids:
            extra = len(emails) - len(question_ids)
            question_ids.extend(question_ids[:extra])

        # Assign questions randomly
        remaining = list(question_ids)
        for mail in emails:
            try:
                question = random.choice(remaining)
                emails[mail] = question
                remaining.remove(question)
            except Exception as e:
                print('something went wrong, Trying to fix it :)', e)
                with open('error_logs.txt', 'a', encoding='utf-8') as file:
                    file.write(f'error was {e} occured during assignment\n')

        # Fetch boilerplate and test cases per unique question id using Gemini
        boiler_by_qid = {}
        tests_by_qid = {}
        unique_qids = {qid for qid in emails.values() if qid}
        for qid in unique_qids:
            q_text = qid_to_text.get(qid, f"Solve the problem for question id {qid}.")
            try:
                resp = generate_response([q_text])  # returns dict
                boiler_by_qid[qid] = resp.get('boiler_code', '')
                tests_by_qid[qid] = resp.get('test_cases', [])
            except Exception as e:
                boiler_by_qid[qid] = f"# Failed to get boilerplate: {e}"
                tests_by_qid[qid] = []
                with open('error_logs.txt', 'a', encoding='utf-8') as file:
                    file.write(f'Gemini generation failed for {qid}: {e}\n')

        return emails, boiler_by_qid, tests_by_qid
