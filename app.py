import streamlit as st
import spacy
from collections import Counter
import random
from PyPDF2 import PdfReader

# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")

def generate_mcqs(text, num_questions=5):
    if text is None:
        return []

    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences from the text
    sentences = [sent.text for sent in doc.sents]

    # Ensure that the number of questions does not exceed the number of sentences
    num_questions = min(num_questions, len(sentences))

    # Randomly select sentences to form questions
    selected_sentences = random.sample(sentences, num_questions)

    # Initialize list to store generated MCQs
    mcqs = []

    # Generate MCQs for each selected sentence
    for sentence in selected_sentences:
        # Process the sentence with spaCy
        sent_doc = nlp(sentence)

        # Extract entities (nouns) from the sentence
        nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]

        # Ensure there are enough nouns to generate MCQs
        if len(nouns) < 2:
            continue

        # Count the occurrence of each noun
        noun_counts = Counter(nouns)

        # Select the most common noun as the subject of the question
        if noun_counts:
            subject = noun_counts.most_common(1)[0][0]

            # Generate the question stem
            question_stem = sentence.replace(subject, "______")

            # Generate answer choices
            answer_choices = [subject]

            # Add some random words from the text as distractors
            distractors = list(set(nouns) - {subject})

            # Ensure there are at least three distractors
            while len(distractors) < 3:
                distractors.append("[Distractor]")  # Placeholder for missing distractors

            random.shuffle(distractors)
            for distractor in distractors[:3]:
                answer_choices.append(distractor)

            # Shuffle the answer choices
            random.shuffle(answer_choices)

            # Append the generated MCQ to the list
            correct_answer = chr(64 + answer_choices.index(subject) + 1)  # Convert index to letter
            mcqs.append((question_stem, answer_choices, correct_answer))

    return mcqs

def process_pdf(file):
    # Initialize an empty string to store the extracted text
    text = ""

    # Create a PyPDF2 PdfReader object
    pdf_reader = PdfReader(file)

    # Loop through each page of the PDF
    for page_num in range(len(pdf_reader.pages)):
        # Extract text from the current page
        page_text = pdf_reader.pages[page_num].extract_text()
        # Append the extracted text to the overall text
        text += page_text

    return text

st.title("Generate MCQs")
st.write("This application generates multiple-choice questions (MCQs) based on the provided text. You can either upload a PDF or TXT file containing the text.")

uploaded_files = st.file_uploader("Upload File(s) (PDF or TXT)", type=['pdf', 'txt'], accept_multiple_files=True)
num_questions = st.selectbox("Number of Questions:", [5, 10, 15, 20])

text = ""

if uploaded_files:
    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            text += process_pdf(file)
        elif file.name.endswith('.txt'):
            text += file.read().decode('utf-8')

if st.button("Generate MCQs"):
    mcqs = generate_mcqs(text, num_questions=num_questions)  # Pass the selected number of questions
    st.write("### Generated MCQs")
    for index, mcq in enumerate(mcqs, start=1):
        question_stem, answer_choices, correct_answer = mcq
        st.write(f"**Q{index}: {question_stem}?**")
        options = ['A', 'B', 'C', 'D']
        for choice_index, choice in enumerate(answer_choices):
            st.write(f"{options[choice_index]}: {choice}")
        st.write(f"*Correct Answer: {correct_answer}*")
