import google.generativeai as genai
import os
import json

genai.configure(api_key='AIzaSyBLzbNnvqR-9RvMPNZnHLTIMz9PHjauyUI')
model = genai.GenerativeModel('gemini-1.5-flash')


import json

def generate_questions(data, num_questions, question_level=None ,previous_question=None):
    grade = data['grade']
    subject1 = data['first_subject']
    subject2 = data['second_subject']
    rating = data['rating']

    questions = []

    for _ in range(num_questions):
        if previous_question:
            prompt = (
                f"Generate a more {question_level} question with 4 possible answers in mathematics about {subject1} or {subject2} "
                f"that is suitable for {rating} {grade} grade student, compared to the previous question:\n"
                f"{previous_question}\n"
                f"Return the answer in the following JSON format:\n"
                f"{{\n"
                f"  \"question\": \"{{the question}}\",\n"
                f"  \"possible_answers\": [\"{{answer1}}\", \"{{answer2}}\", \"{{answer3}}\", \"{{answer4}}\"],\n"
                f"  \"correct_answer\": \"{{the correct answer}}\",\n"
                f"  \"explanation\": \"{{explanation about the answer}}\"\n"
                f"}}"
            )
        else:
            prompt = (
                f"Generate a question with 4 possible answers in mathematics about {subject1} or {subject2} that is suitable for"
                f" {rating} {grade} grade student.\n"
                f"Return the answer in the following JSON format:\n"
                f"{{\n"
                f"  \"question\": \"{{the question}}\",\n"
                f"  \"possible_answers\": [\"{{answer1}}\", \"{{answer2}}\", \"{{answer3}}\", \"{{answer4}}\"],\n"
                f"  \"correct_answer\": \"{{the correct answer}}\",\n"
                f"  \"explanation\": \"{{explanation about the answer}}\"\n"
                f"}}"
            )

        # Generate the content using the model
        response = model.generate_content(prompt)
        response_data = response.text.strip()        
        # Remove markdown code block markers if present
        response_data = response_data.replace('```json', '').replace('```', '').strip()

        try:
            response_dict = json.loads(response_data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Failed to parse: {response_data}")
            return []  # Return an empty list instead of None values
        
        questions.append(response_dict)
        # Update the previous_question for the next iteration
        previous_question = response_dict['question']

    return questions
