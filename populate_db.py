import pickle
import sqlite3

from pprint import pprint # for debugging purposes only

topics_and_questions_dictionary = {}

with open("topics_and_questions.pkl", "rb") as _:
    topics_and_questions_dictionary = pickle.load(_)

def get_latest_instance_from_table(table_name: str, cursor: sqlite3.Cursor, id_column='id'):
    query = f"SELECT * FROM {table_name} ORDER BY {id_column} DESC LIMIT 1"
    return cursor.execute(query).fetchone()

def execute_insert_query(cursor, query, params=None):
    try:
        cursor.execute(query, params)
    except sqlite3.Error as e:
        print(e)
        raise e
    
print("Populating DB now.")

with sqlite3.connect("questions-db.sqlite3") as connection:
    cursor = connection.cursor()

    subject = cursor.execute("SELECT * FROM Subjects WHERE name=?", ("PYTHON", )).fetchone()

    for items in topics_and_questions_dictionary.items():
        try:
            topic, questions = items[0], items[1]
            print(f"Inserting questions for topic: {topic}")

            insert_topic_query = """
                INSERT INTO Topics (name, subject) VALUES (?,?)
            """
            execute_insert_query(cursor, insert_topic_query, (topic, subject[0]))

            latest_topic = get_latest_instance_from_table("Topics", cursor)
            
            for question in questions:
                insert_question_query = """
                    INSERT INTO Questions (question, topic) VALUES (?, ?)
                """
                execute_insert_query(
                    cursor=cursor, 
                    query=insert_question_query, 
                    params=(question["question"], latest_topic[0])
                )

                latest_question = get_latest_instance_from_table("Questions", cursor)

                for answer in question["answers"]:
                    insert_answer_query = """
                        INSERT INTO Choices (question, choice, is_correct_answer, explanation)
                        VALUES (?,?,?,?)
                    """
                    execute_insert_query(
                        cursor=cursor,
                        query=insert_answer_query,
                        params=(
                            latest_question[0], 
                            answer["answer"],
                            answer["is_correct_answer"],
                            answer["explanation"]
                        )
                    )
                
                if question["code_snippet"]:
                    insert_code_snippet_query = """
                        INSERT INTO code (question, code) VALUES(?,?)
                    """
                    execute_insert_query(
                        cursor=cursor,
                        query=insert_code_snippet_query,
                        params=(latest_question[0], question["code_snippet"])
                    )
        
        except sqlite3.IntegrityError:
            continue