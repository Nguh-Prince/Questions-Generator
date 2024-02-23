import re
import os

question_regex = re.compile("^(\d+\.)((\s*\w*\s*)*) (?<![\r])")
question_with_answers = re.compile("^(\d+\.)((\s*\w*\s*)*)")

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup

questions_directory_path = os.path.join(
    os.path.dirname(__file__), "questions"
)

already_downloaded_questions = set([
    f.strip(".txt") for f in os.listdir(questions_directory_path)
])

def get_questions_from_page(page, url, topic="Basics"):
    page.goto(url, timeout=0)
    try:
        soup = BeautifulSoup(page.content(), "html.parser")

        file_path = os.path.join(questions_directory_path, f"{topic}.txt")

        get_questions_from_soup(soup, topic, file_path=file_path)

        # get the questions and save to a text file (questions.txt)
    except Exception as e:
        print("Error in get_questions_from_page")
        breakpoint()

def get_questions_from_soup(soup, topic="Basics", file_path="questions.txt"):
    paragraphs = soup.select(".entry-content>p")
    answers = soup.select(".entry-content>.collapseomatic_content")
    code_blocks = soup.select(".entry-content .hk1_style pre")

    paragraph_index, answer_index, code_block_index = 0, 0, 0

    texts = []

    while answer_index < len(answers):
        paragraph = paragraphs[paragraph_index].text.replace('\r', '')
        paragraph_index += 1
        
        if not question_regex.search(paragraph):
            print(f"paragraph: {paragraph} did not match test, continuing")
            continue

        answer = answers[answer_index].text.replace('\r', '')
        
        answer_index += 1

        text =  f"({topic}) {paragraph}"

        if len(paragraph.split('\n')) >= 2:
            print(f"The question has the options in it, setting text to the question")
            # write the question directly to the file
            text = f"{paragraph.strip('View Answer')}\n\n{answer}"
        else:
            print(f"This question has a code block, code_blocks_index: {code_block_index}")
            # The paragraph is a code block
            answer_paragraph = paragraphs[paragraph_index].text.strip('View Answer').replace('\r', '') # this is now the paragraph with the answers
            try:
                code_block = code_blocks[code_block_index].text#.replace('\r', '')
            except IndexError as e:
                breakpoint()
                raise e

            print("This question has a code block, the block is: ")
            print(code_block)

            text = f"{text}\n\n{code_block}\n\n{answer_paragraph}\n\n{answer}"

            code_block_index += 1
            paragraph_index += 1

        texts.append(text)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(
            '\n\n\n\n'.join(texts)
        )

url = "https://www.sanfoundry.com/1000-python-questions-answers/"

def run(playwright: Playwright) -> None:
    try:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, timeout=0)
        
        soup = BeautifulSoup(page.content(), "html.parser")

        basics_file_name = os.path.join(questions_directory_path, "Basics.txt")
        get_questions_from_soup(soup, file_path=basics_file_name)

        links = soup.select(".sf-2col-tbl li a")
        number_of_links = len(links)
        for index, link in enumerate(links):
            print(f"Getting questions from link #{index+1} of {number_of_links}")
            text = link.text

            if text in already_downloaded_questions:
                print(f"Already downloaded the {text} questions, continuing")
                continue
            href = link.get("href")

            get_questions_from_page(page, href, topic=text)
        
        context.close()
        browser.close()
    except Exception as e:
        breakpoint()
        raise e

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
