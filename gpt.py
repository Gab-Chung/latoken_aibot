import sys
import openai
import os
import json
from aiogram import Bot, Dispatcher, executor, types
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("BOT_TOKEN")

if not token:
    print("ERROR: Token var is missing: BOT_TOKEN")
    sys.exit(-1)

bot = Bot(token=token)
dp = Dispatcher(bot)

openai.api_key = os.getenv("OPENAI_API_KEY")


# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# Load and store text from your PDF files
pdf_texts = {}
pdf_files = ["./Latoken+Hachathon_compressed.pdf"]
for pdf_file in pdf_files:
    pdf_texts[pdf_file] = extract_text_from_pdf(pdf_file)

combined_pdf_text = "\n".join(pdf_texts.values())

# Load JSON data
with open("./culture.json") as json_file:
    data = json.load(json_file)


def compare_texts(text1, text2):
    # Split the texts into sets of words
    words_text1 = set(text1.lower().split())
    words_text2 = set(text2.lower().split())

    # Find the intersection of both sets (common words)
    common_words = words_text1.intersection(words_text2)

    # Return True if there are any common words, False otherwise
    return bool(common_words)


# Function to retrieve relevant information from the JSON dataset
def retrieve_relevant_info(query, data):
    relevant_info = []
    for _, item in data.items():
        # Check if any of the fields in the JSON item match the query
        for _, line in item.items():
            if compare_texts(query, line):
                print("found match!\n")
                relevant_info.append(line)
    return relevant_info


@dp.message_handler(commands=["start", "help"])
async def welcome(message: types.Message):
    await message.reply("Hello! I am Latoken AI assistant, ask me something.")


@dp.message_handler()
async def gpt(message: types.Message):
    # Retrieve relevant information from the JSON dataset
    relevant_info = retrieve_relevant_info(message.text, data)

    # Combine the retrieved information into a single string
    retrieved_text = "\n".join([json.dumps(info) for info in relevant_info])

    # Combine retrieved text with PDF text
    combined_text = f"Retrieved Information: {retrieved_text}\n\nPDF Information: {combined_pdf_text}"

    # Pass the combined information to GPT-4
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in Latoken website data."},
            {"role": "user", "content": message.text},
            {
                "role": "system",
                "content": f"Here is relevant information: {combined_text}",
            },
        ],
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    await message.reply(response.choices[0].message["content"])


if __name__ == "__main__":
    executor.start_polling(dp)
