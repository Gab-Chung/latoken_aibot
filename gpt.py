import sys
import openai
import os
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

combined_text = "\n".join(pdf_texts.values())


@dp.message_handler(commands=["start", "help"])
async def welcome(message: types.Message):
    await message.reply("Hello! I am Latoken AI assistant, ask me something.")


@dp.message_handler()
async def gpt(message: types.Message):

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message.text},
            {
                "role": "system",
                "content": f"Here is relevant information {combined_text}",
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
