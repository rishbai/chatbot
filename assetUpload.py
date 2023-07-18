import time
import os
import PyPDF2
import pickle
import nltk
import openai
import faiss
import docx2txt
import openpyxl
import numpy as np
# set this to OpenAI API KEY
openai.api_key = "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"

"""
    Global Variables
"""
chunk_size = 500
directory = os.getcwd() + "/documents/"  # path for PDFs
pickle_path = os.getcwd() + "/pickles/"  # path for output pickle files


# import nltk
# nltk.download('punkt')

#Function to read text from each file in the documents folder. Adds 
#each page of txt to a variable names file_text. Returns all of the pages of text 
def extract_text(filename):
    print("Extracting text from " + filename)
    reader = PyPDF2.PdfReader(directory + filename)
    # reader = docx2txt.process(directory + filename)
    print(filename + ' has ' + str(len(reader.pages)) + ' pages')
    file_text = ""
    for page in reader.pages:  # read each page and extract text
        file_text += page.extract_text()
    # get rid of newline characters (makes chunking easier)
    file_text = file_text.replace('\n', ' ')
    return file_text

# Reading text from excel files
def extract_excel(filename):
    print("Extracting text from " + filename)
    workbook = openpyxl.load_workbook(directory + filename)
    sheet = workbook.active

    file_text = ""
    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if cell and isinstance(cell, str):
                file_text += cell + " "

    file_text = file_text.replace('\n', ' ')
    return file_text

#Function to read through word documents in the documents folder 
def extract_word(filename):
    print("Extracting text from " + filename)
    file_text = docx2txt.process(directory + filename)
    file_text = file_text.replace('\n', ' ')
    return file_text

#Creates separate chunks of the file making it easier for searching similarities. 
#Uses the nltk module to ensure text is split by sentence 
#Stores each senetence into a chunks array in order to search through smaller chunks
#rather than large files and paragraphs of text. 
def create_chunks(filename, text):
    print("Chunking text from " + filename)
    sentences = nltk.sent_tokenize(text)  # split text into sentences
    chunks = []  # stores all chunks, sized to nearest complete sentence.
    chunk = ""
    for sentence in sentences:  # append sentences to chunk until it is longer than 1024 characters
        if len(chunk + " " + sentence) <= chunk_size:
            chunk = chunk + " " + sentence
        else:
            chunks.append(chunk)
            chunk = sentence
    # last chunk may be less than chunk size, append it anyways
    chunks.append(chunk)
    print('Generated ' + str(len(chunks)) + ' chunks for ' + filename+'.')
    return chunks

#Function to create unique and specific embeddings for each chunk of content in the large array. 
#Prints the amount of embeddings created.
def create_embeddings(filename, chunks):
    print("Generating embeddings for " + filename)
    embeddings = []
    for chunk in chunks:
        #calls the create embedding function from open ai API
        #OpenAI call
        embeddings.append(openai.Embedding.create(
            model="text-embedding-ada-002", input=chunk)["data"][0]["embedding"])
        time.sleep(1)  # REPLACE THIS W/ EXPONENTIAL BACKOFF EVENTUALLY
    print('Generated ' + str(len(embeddings)) +
          ' embeddings for ' + filename+'.')
    return embeddings

#indexes through the embeddings to find if a path exists for specific chunks and 
#their corresponding embeddings.
def index_embeddings(filename, embeddings, chunks):
    print('Indexing embeddings for ' + filename)
    if os.path.exists(pickle_path + 'index.pickle'):
        print('found index.pickle, appending...')
        index = pickle.load(open(pickle_path+'index.pickle', 'rb'))
        chunk_list = pickle.load(open(pickle_path+'chunks.pickle', 'rb'))
    else:
        print('no index.pickle found, creating new index...')
        index = faiss.IndexFlatL2(len(embeddings[0]))
        chunk_list = []

    index.add(np.array(embeddings))
    chunk_list.extend(chunks)
    pickle.dump(index, open(pickle_path+'index.pickle', 'wb'))
    pickle.dump(chunk_list, open(pickle_path+'chunks.pickle', 'wb'))
    pickle.dump(embeddings, open(pickle_path+'embeddings.pickle', 'wb'))

#Generates an overarching summary for the filename read in and the text found between 
#different files. Gives the role of reading to the openai module and returns the 
#summary generated. 
def generate_summary(filename, text):
    print('Generating summary for ' + filename)
    #Calls the create chat function from openAI API to generate output for the uploaded asset
    #OpenAI call
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Your goal is to read EBooks and provide concise summaries of the contents. "},
                  {"role": "user", "content": text},]
    )
    summary = completion['choices'][0]['message']['content']
    print('Summary:', summary)
    return summary

#Generates statistics frome a passed in file and with a statistic parameter to find or relate the best to. 
def generate_statistics(filename, text):
    print('Generating statistics for ' + filename)
    #OpenAI call
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Your goal is to read EBooks and respond with a list of the most important statistics you find. Your response should only be a list of these statistics."},
                  {"role": "user", "content": text},]
    )
    statistics = completion['choices'][0]['message']['content']
    print('Statistics:', statistics)
    return statistics

#Processes the file by calling all helper functions for extracting the text and creating 
#chunks of infomration. Also calls generate summary and generate statistics for the purpose of
#assembling the file. 
def process_asset(filename):
    print("Processing asset " + filename)
    asset = {'filename': filename}

    # Checks what kind of file is being loaded
    file_extension = os.path.splitext(filename)[1]
    if file_extension == '.pdf':
        asset['text'] = extract_text(asset['filename'])
    elif file_extension == '.xlsx':
        asset['text'] = extract_excel(asset['filename'])
    elif file_extension == '.docx':
        asset['text'] = extract_word(asset['filename'])
    else:
        print("Unsupported file type:", file_extension)
        return
    asset['chunks'] = create_chunks(asset['filename'], asset['text'])
    asset['embeddings'] = create_embeddings(asset['filename'], asset['chunks'])
    index_embeddings(asset['filename'], asset['embeddings'], asset['chunks'])
    asset['summary'] = generate_summary(asset['filename'], asset['text'])
    asset['statistics'] = generate_statistics(asset['filename'], asset['text'])

    if os.path.exists(pickle_path + 'corpus.pickle'):
        print('found corpus.pickle, appending...')
        corpus = pickle.load(open(pickle_path+'corpus.pickle', 'rb'))
        corpus.append(asset)
    else:
        corpus = []
        corpus.append(asset)
    pickle.dump(corpus, open(pickle_path+'corpus.pickle', 'wb'))
    print('Corpus now containts ' + str(len(corpus)) + ' documents.')


"""
Example for indexing a single file: 
"""
#the test file for reading and processing 
# test_file = "beyond-cdp.pdf"  # filename in /documents directory
# process_asset(test_file)
# test_file = "third-party-cookies.pdf"
# process_asset(test_file)

# test_file = "USPS_Git_Best_Practices_v1.1 (1)-part-2-part-1.pdf"  # filename in /documents directory
# process_asset(test_file)

# test_file2 = "USPS_Git_Best_Practices_v1.1 (1)-part-2-part-2.pdf"  # filename in /documents directory
# process_asset(test_file2)

# test_file3 = "PDUs.docx"  # filename in /documents directory
# process_asset(test_file3)


# test_file4 = "USPS_Git_Best_Practices_v1.1 (1)-part-1-part-2.pdf"  # filename in /documents directory
# process_asset(test_file4)

# test_file4 = "USPS_Git_Best_Practices_v1.1 (1)-part-1-part-1.pdf"  # filename in /documents directory
# process_asset(test_file4)

"""
Example for indexing the entire /documents directory: 
"""
# for filename in os.listdir(directory):
#     filepath = os.path.join(directory, filename)
#     if os.path.isfile(filepath) and filename != '.DS_Store':
#         process_asset(filename)
