import os
import sqlite3
import tkinter
import tkinter.messagebox

import customtkinter

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

path_to_db = os.path.join(
    os.path.dirname(__file__),
    "questions-db.sqlite3"
)

class QuestionAndAnswers(customtkinter.CTkFrame):
    def __init__(self, question, choices, *args, code=None, on_question_save=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.question = question
        self.choices = choices

        self.difficulty = 1
        new_line = '\n\n'

        self.question_textbox = customtkinter.CTkTextbox(self, width=250, height=100)
        self.question_textbox.grid(row=0, column=0)
        self.question_textbox.insert("0.0", f"{self.question[1]} {new_line + code if code else ''}" )

        self.choice_radio_var = tkinter.IntVar(value=0)
        self.choices_frame = customtkinter.CTkFrame(self)
        self.choices_frame.grid(row=1, column=0, padx=(20, 20), pady=(20, 0))
        
        self.choices_label = customtkinter.CTkLabel(master=self.choices_frame, text="choices")

        longest_string_length = max(len(choice[2]) for choice in choices)

        for index, choice in enumerate(choices):
            choice_text = choice[2].ljust(
                longest_string_length, " "
            ) # adding spaces to the right of the string
            choice_text += "(A)" if choice[3] == 1 else ""
            radio_button = customtkinter.CTkRadioButton(master=self.choices_frame, variable=self.choice_radio_var, value=choice[0], text=choice_text)
            radio_button.grid(row=index, column=0)

        self.difficulty_frame = customtkinter.CTkFrame(self)
        self.difficulty_frame.grid(row=2, column=0, pady=(20, 0))
        self.difficulty_label = customtkinter.CTkLabel(self.difficulty_frame, text=f"Difficulty: {self.question[3] if self.question[3] else self.difficulty}")
        self.difficulty_label.grid(column=0, row=0)

        self.difficulty_slider = customtkinter.CTkSlider(self.difficulty_frame, from_=1, to=5, number_of_steps=25, command=self.on_slide)
        self.difficulty_slider.grid(row=1, column=0)
        self.difficulty_slider.set( question[3] if question[3] else self.difficulty )

        self.save_button = customtkinter.CTkButton(self, text="Save", command=self.save_to_db)
        self.save_button.grid(row=3, column=0, pady=(20, 0))
        self.set_save_button_state()

        self.on_question_save = on_question_save
    
    def on_slide(self, difficulty):
        self.difficulty = round(difficulty, 1)
        self.difficulty_label.configure(text=f"Difficulty: {self.difficulty}")

        self.enable_save_button() if self.difficulty != self.question[3] else self.disable_save_button()

    def save_to_db(self):
        print("Saving to DB")

        with sqlite3.connect(path_to_db) as connection:
            cursor = connection.cursor()

            cursor.execute("UPDATE questions SET difficulty=? WHERE id=?", (self.difficulty, self.question[0]))

        print("Query executed successfully")
        
        self.disable_save_button()
        self.question = list(self.question)
        self.question[3] = self.difficulty
        self.question = tuple(self.question)

        if callable(self.on_question_save):
            self.on_question_save()
        else:
            print(f"In QuestionAndAnswers: {self.on_question_save} is not callable")

    def disable_save_button(self):
        self.save_button.configure(state="disabled")

    def enable_save_button(self):
        self.save_button.configure(state="enabled")

    def set_save_button_state(self):
        self.disable_save_button() if self.difficulty == self.question[3] else self.enable_save_button()
class App(customtkinter.CTk):
    def __init__(self, fg_color=None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.title("Questions generator")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Questions", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="Language 🌐", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["English", "Francais"],                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.scrollable_frame = None
        
        self.data = None
        self.get_data()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def get_data(self):
        print("Getting the data from the database")
        # get the questions and choices from the database
        with sqlite3.connect(path_to_db) as connection:
            cursor = connection.cursor()

            query = """
                SELECT q.*, c.id, c.question, c.choice, c.is_correct_answer, c.explanation, co.code FROM 
                questions q JOIN Choices c ON q.id = c.question 
                LEFT JOIN code co ON co.question=q.id
                WHERE q.difficulty IS NULL
            """

            results = cursor.execute(query).fetchall()

            self.data = {}
            for row in results:
                question = row[:4]
                choice = row[4:-1]

                self.data.setdefault(question, {
                    "choices": set([]),
                    "code": row[-1]
                })

                self.data[question]["choices"].add(choice) 

        print("Displaying the data")
        self.display_data()

    def display_data(self, number_of_rows=5):
        print("In the display_data method")
        if not self.scrollable_frame is None:
            self.scrollable_frame.destroy()

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=1, rowspan=4, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        for index, item in enumerate(self.data.items()):
            if index >= number_of_rows:
                break

            print(f"Adding the {index+1} question to the frame")
            qa = QuestionAndAnswers(
                item[0], item[1]["choices"], self.scrollable_frame, 
                on_question_save=lambda question=item[0]: self.remove_question(question),
                code=item[1]["code"]
            )
            qa.grid(row=index, column=0, pady=(0, 40))

        print("Done displaying the data")

    def remove_question(self, question: tuple):
        print("Calling remove question")
        del self.data[question]

        self.display_data()

app = App()

app.mainloop()