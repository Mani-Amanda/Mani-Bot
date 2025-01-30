import random
import time
import nltk
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
import tkinter as tk
import customtkinter as ctk
from tabulate import tabulate
from fpdf import FPDF

# Reading the corpus of text
with open('data.txt', 'r', errors='ignore') as f:
    raw_doc = f.read()

raw_doc = raw_doc.lower()  # Converting entire text to lowercase

# Tokenize the text into lines and then into words
line_tokens = raw_doc.splitlines()

# Create a dictionary to map goods to their shelf numbers
goods_to_shelf = {}
for line in line_tokens:
    parts = line.split(':', 1)  # Split only on the first colon
    if len(parts) == 2:
        item, shelf = parts
        goods_to_shelf[item.strip()] = shelf.strip()

# Initialize NLTK Lemmatizer
lemmatizer = WordNetLemmatizer()

# Defining Greeting function
greet_inputs = (
    'hello', 'hi', 'hey', 'whassup', 'how are you', 'good morning', 'good afternoon', 'good evening', 
    'what’s up', 'how’s it going', 'yo', 'hi there', 'greetings', 'howdy', 'morning', 'afternoon', 
    'evening', 'sup', 'hiya', 'salutations', 'hi bot', 'hello bot'
)

greet_response = (
    "Hello! Welcome to MAH Super-Market. How can I assist you today?",
    "Hi there! I'm here to help you find anything you need. What are you looking for?",
    "Hey! Great to see you at MAH Super-Market. How can I help you today?",
    "Greetings! I'm MANI Bot, your shopping assistant. What can I help you find?",
    "Hello! Ready for some shopping? Tell me what you need and I'll guide you to the right shelf.",
    "Hi! I'm here to make your shopping experience easier. What items are you looking for?",
    "Welcome! Let's find what you need. Just tell me the items you're looking for.",
    "Hey there! I'm here to help you locate your items. What can I assist you with today?",
    "Hello and welcome! I'm MANI Bot, at your service. What can I help you find?",
    "Hi! Need assistance finding something? Let me guide you to the right shelf."
)

def greet(sentence):
    for word in sentence.split():
        if word.lower() in greet_inputs:
            return random.choice(greet_response)

# Global list to accumulate items for report
accumulated_items = []

def generate_pdf_report(items):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="MAH Super-Market - Item Location Report", ln=True, align='C')
    pdf.ln(10)

    for item, shelf in items:
        pdf.cell(200, 10, txt=f"{item.capitalize()}: Shelf {shelf}", ln=True)

    pdf.output("report.pdf")

def response(user_response):
    global accumulated_items
    user_response = user_response.lower()

    # Filter out single-letter words before processing (improvement)
    tokens = [word for word in word_tokenize(user_response) if len(word) > 1]

    # Check for greetings
    if any(greet_word in user_response for greet_word in greet_inputs):
        return greet(user_response)

    # Handle 'thank you' or 'thanks'
    if 'thank you' in tokens or 'thanks' in tokens:
        return "You are welcome. Anything else do you want to find?"

    # Handle 'report' if present in the user response tokens
    if 'report' in tokens or 'bye' in tokens:
        if accumulated_items:
            report_table = tabulate(accumulated_items, headers=['Item', 'Shelf Number'], tablefmt='simple')
            generate_pdf_report(accumulated_items)  # Generate PDF report
            return f"Here is the location for your items:\n\n{report_table}\nA PDF report has also been generated. Have a Nice day!! If you need further assistance, I'm here to help."
        else:
            return "Bye. No items have been queried yet."

    # Check for "want" or "find" before processing nouns (improvement)
    if "want" in tokens or "find" in tokens:
        # Find the index of the first occurrence of "want" or "find"
        if "want" in tokens:
            index = tokens.index("want")
        else:
            index = tokens.index("find")
        tokens = tokens[index + 1:]  # Get words after "want" or "find"

    # Lemmatize and identify nouns
    nouns = []
    for word, tag in pos_tag(tokens):
        if tag.startswith('NN'):  # NN for nouns
            lemma = lemmatizer.lemmatize(word)
            nouns.append(lemma)

    # Handle item inquiries
    response_list = []
    for noun in nouns:
        # Check if noun is in goods_to_shelf dictionary
        if noun in goods_to_shelf:
            shelf_info = [noun, goods_to_shelf[noun]]
            accumulated_items.append(shelf_info)
            response_list.append(random.choice([
                f"The shelf for {noun} is {goods_to_shelf[noun]}.",
                f"You can find {noun} on {goods_to_shelf[noun]}.",
                f"{noun} is located at {goods_to_shelf[noun]}.",
                f"{noun} is available on {goods_to_shelf[noun]}."
            ]))
        else:
            # If noun not found, inform user directly about the missing item
            response_list.append(f"Sorry, {noun} is not available today.")

    return '\n'.join(response_list)


def simulate_typing(chat_window, message):
    delay = 0.03  # Adjust the delay time between characters (in seconds)
    for char in message:
        chat_window.insert(tk.END, char, 'bot')
        chat_window.update()  # Refresh the chat window to show the new character
        time.sleep(delay)  # Introduce a delay to simulate typing speed

def send():
    user_input = user_text.get("1.0", 'end-1c').strip()
    if user_input:
        user_text.delete("1.0", 'end')
        chat_window.config(state=tk.NORMAL)
        chat_window.insert(tk.END, f"You: \n{user_input}\n", 'user')
        simulate_typing(chat_window, f"Bot: \n{response(user_input)}\n\n")
        chat_window.config(state=tk.DISABLED)
        chat_window.yview(tk.END)

# GUI Setup
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

root = ctk.CTk()
root.title("MAH Super-Market")
root.geometry("500x600")

# Chat Window
chat_frame = ctk.CTkFrame(root)
chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

chat_window = tk.Text(chat_frame, width=50, height=20, bg="#1e2125", fg="#ffffff", wrap=tk.WORD)
chat_window.pack(padx=10, pady=10, fill="both", expand=True)
chat_window.config(state=tk.NORMAL)
chat_window.insert(tk.END, "Bot: \nHello! I’m MANI Bot, and I'm here to assist you in finding the items you need. What can I help you shop for today?\n\n", 'bot')
chat_window.config(state=tk.DISABLED)

# Adding custom tags for styling chat
chat_window.tag_configure('user', foreground='#00ff00', justify='right', lmargin1=10, lmargin2=10, font=("Arial", 15))
chat_window.tag_configure('bot', foreground='#00ffff', justify='left', rmargin=10, font=("Arial", 15))

# User Input
user_text = ctk.CTkTextbox(root, width=400, height=50)
user_text.pack(padx=10, pady=10, fill="x")

# Send Button
send_button = ctk.CTkButton(root, text="Send", command=send)
send_button.pack(pady=10)

# Main loop to run the GUI
root.mainloop()
