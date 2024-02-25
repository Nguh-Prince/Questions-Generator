import sqlite3

create_subjects_table = """
CREATE TABLE subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)
"""

create_topics_table = """
CREATE TABLE topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        subject INTEGER NOT NULL,
        deleted INTEGER DEFAULT 0,
        FOREIGN KEY(subject) REFERENCES Subjects(id) ON DELETE CASCADE ON UPDATE CASCADE,
        UNIQUE(subject, name)
    )
"""

create_difficulties_table = """
CREATE TABLE difficulties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    deleted INTEGER DEFAULT 0,
    min_difficulty_level REAL,
    max_difficulty_level REAL
)
"""

create_questions_table = """
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    difficulty REAL,
    topic INTEGER NOT NULL,
    deleted INTEGER DEFAULT 0,
    FOREIGN KEY(topic) REFERENCES Topics(id) ON UPDATE CASCADE
)
"""

create_choices_tables = """
CREATE TABLE Choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question INTEGER,
    choice TEXT,
    is_correct_answer INTEGER DEFAULT 0,
    explanation TEXT,
    deleted INTEGER DEFAULT 0,
    FOREIGN KEY(question) REFERENCES Questions(id) ON UPDATE CASCADE,
    UNIQUE(choice, question)
)
"""

create_code_block_table = """
CREATE TABLE code (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question INTEGER,
    code TEXT,
    deleted INTEGER DEFAULT 0,
    FOREIGN KEY(question) REFERENCES Questions(id) ON UPDATE CASCADE
)
"""

with sqlite3.connect("questions-db.sqlite3") as connection:
    cursor = connection.cursor()
    
    for query in [
        create_subjects_table, 
        create_topics_table, 
        create_questions_table,
        create_choices_tables,
        create_difficulties_table,
        create_code_block_table
    ]:
        try:
            cursor.execute(query)
        except sqlite3.DatabaseError as e:
            print(f"Error executing query: {query}")
            raise e   
    
    cursor.execute("INSERT INTO Subjects (name) VALUES ('PYTHON')")
    
    difficulties = {
        (1, 2): 'Easy',
        (2.1, 3.5): 'Medium',
        (3.5, 4.2): 'Difficult',
        (4.3, 5): 'Advanced'
    }

    for item in difficulties.items():
        cursor.execute("""
                       INSERT INTO Difficulties 
                       (name, min_difficulty_level, max_difficulty_level) 
                       VALUES(?,?,?)""", (item[1], item[0][0], item[0][1]))
        