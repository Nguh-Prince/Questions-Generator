import os
import re
import pickle

questions_directory = os.path.join(
    os.path.dirname(__file__), "questions"
)

text_file_regex = re.compile("(\.txt)$")
file_topics_regex = re.compile("((\w+\s?)+)(– (\d+)){0,1}")
question_number_and_topic_regex = re.compile("^((\(\w+\s?\) )?(\w+\.)) ")
answer_explanation_regex = re.compile("Answer: (\w+)\nExplanation: (.*)")
answer_regex = re.compile('(\w)\) (.*)')

topics_and_questions_dictionary = {}

for root, dirs, files in os.walk(questions_directory):
    text_files = [ f for f in files if text_file_regex.search(f) ]

    for file in text_files:
        file_path = os.path.join(root, file)

        topic, _, __, number = file_topics_regex.search(file).groups()
        list_of_questions = topics_and_questions_dictionary.setdefault(topic, [])

        with open(file_path, encoding="utf-8") as _:
            content = _.read()
            questions = content.split("\n"*4)

            for index, question in enumerate(questions):
                question = re.sub("\t", '', question)

                print(f"Curating data for question {index+1} out of {len(questions)}")
                # getting sections
                sections = question.split('\n\n')

                if len(sections) < 3:
                    try:
                        _sections = sections
                        regex = re.compile("((.*)\d+\.)(.*)")
                        result = regex.search(_sections[0]).group()

                        choices = _sections[0].split(result)[1]

                        sections.append(_sections[1]) 
                        sections[0], sections[1] = result, choices
                    except Exception as e:
                        continue

                sections_dictionary = {
                    "question": sections[0],
                    "code_snippet": None,
                    "answers": sections[-2].strip("\n"),
                    "correct_answer_and_explanation": sections[-1],
                    "options_exist": False,
                    "correct_answer_exists": False,
                    "correct_answer_in_options": False 
                }

                sections_dictionary["code_snippet"] = (
                    sections[1] if len(sections) > 3 else None
                )

                # Formatting the different sections
                sections_dictionary["question"] = sections_dictionary["question"].strip("\n")
                sections_dictionary["question"] = question_number_and_topic_regex.sub('', sections_dictionary["question"])

                try:
                    # Formatting correct_answer_and_explanation
                    correct_answer_and_explanation = answer_explanation_regex.search(sections_dictionary["correct_answer_and_explanation"]).groups()
                    sections_dictionary["correct_answer_and_explanation"] = {
                    "answer": correct_answer_and_explanation[0],
                    "explanation": correct_answer_and_explanation[1]
                }
                except AttributeError as e:
                    continue
                
                answers = sections_dictionary["answers"].split("\n")
                sections_dictionary["answers"] = []
                
                for answer in answers:
                    try:
                        option_and_answer = answer_regex.search(answer).groups()
                        is_correct_answer = option_and_answer[0] == sections_dictionary["correct_answer_and_explanation"]["answer"]

                        answer_dictionary = {
                            "answer": option_and_answer[1],
                            "is_correct_answer": 1 if is_correct_answer else 0,
                            "explanation": sections_dictionary["correct_answer_and_explanation"]["explanation"] if is_correct_answer else None
                        }

                        sections_dictionary["answers"].append(answer_dictionary)

                        if is_correct_answer:
                            sections_dictionary["correct_answer_in_options"] = True
                    except AttributeError as e:
                        print(f"AttributeError on line 95, answers:")
                        print(answers)
                        continue
                    
                sections_dictionary["options_exist"] = len(answers) >= 2
                sections_dictionary["correct_answer_exists"] = True
                
                if (
                    sections_dictionary["options_exist"] and 
                    sections_dictionary["correct_answer_exists"] and 
                    sections_dictionary["correct_answer_in_options"]
                ):
                    list_of_questions.append(sections_dictionary)
                else:
                    print(f"The question was not appended to the list of questions. The question is:")
                    print(question)
                    print(f"The sections are:")
                    print(sections_dictionary)

with open ('topics_and_questions.pkl', 'wb') as file:
    pickle.dump(topics_and_questions_dictionary, file)