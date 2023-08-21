
import pickle
import openai
import os
import numpy as np

# set openAI key
openai.api_key = ""

# load our pickle files
pickle_path = os.getcwd() + "/pickles/"  # path for output pickle files
index = pickle.load(open(pickle_path+'index.pickle', 'rb'))
chunks = pickle.load(open(pickle_path+'chunks.pickle', 'rb'))
corpus = pickle.load(open(pickle_path+'corpus.pickle', 'rb'))

#Function used for searching through the knowledge base with a specifc question asked
#by the user. Organizes text in terms of relevancy and citations. 
def search_embedding(question):
    print("Searching knowledge base for relevant text...")
    # embed question and search index
    # var indicies will contain the position of the 4 most relevant chunks
    #OpenAI call
    question_embedding = openai.Embedding.create(
        model="text-embedding-ada-002", input=question)["data"][0]["embedding"]
    _, indices = index.search(np.array([question_embedding]), 4)

    relevant_text = []
    citations = []

    for i in indices[0]:
        if i == -1:  # if no relevant text was found return nothing
            break
        # append the corresponding chunk to the embedding
        relevant_text.append(chunks[i])
        counter = 0
        for obj in corpus:
            for chunk in obj['chunks']:
                if (counter == i):
                    citations.append(obj['filename'])
                counter += 1

    for idx in indices[0]:
        if idx != -1:
            obj = corpus[idx // len(chunks)]
            citations.append(obj['filename'])

    print('Sources:')  # cite your sources
    for idx in range(len(relevant_text)):
        print(str(idx + 1) + '. ' + relevant_text[idx])
        print('- found in ' + citations[idx])

    return relevant_text, citations

# Uses the openai API to create a response to the question given the relevant text found 
# within the knowledge base.
def answer_question(question, relevant_text):
    print("GPT will attempt to answer the question based of knowledge base...")
    prompt = f"""Answer the question using only the source text. If you do not know please say that. Give a thorough answer given the source text only.\n\n 
Question: {question}
Source text: {relevant_text}"""
    #OpenAI call
    answer = openai.Completion.create(
        prompt=prompt,
        model="text-davinci-003",
        max_tokens=1500,
        temperature=1
        # model="gpt-3.5-turbo",
        # messages=[
        #     {"role": "system", "content": prompt},
        #     {"role": "user", "content": prompt}
    )
    print('Answer: ')
    # print(answer['choices'][0]['message']['content'].strip())
    # return answer['choices'][0]['message']['content'].strip()
    print(answer["choices"][0]["text"].strip())
    return answer["choices"][0]["text"].strip()

def ask_question(question):
    print("Answering question: ", question)
    relevant_text = search_embedding(question)
    return answer_question(question, relevant_text)


# question = "Why is it important to report PDU's?"  # beyond cdp question
# # third party cookie question
# # question2 = "What does a customer scenario look like?"
# ask_question(question)
# ask_question(question2)
