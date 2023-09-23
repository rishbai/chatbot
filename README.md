# Knowledge Base Search System
This repository contains a Python project that provides functionalities for searching through a knowledge base of text documents, extracting relevant information, and generating summaries and statistics based on the contents of these documents. The system utilizes the OpenAI API for text embedding, chat completion, and other natural language processing tasks.

## Introduction
The Knowledge Base Search and Summarization System is designed to assist users in efficiently searching through a collection of documents, extracting relevant information, and generating summaries and statistics. The system employs various natural language processing techniques provided by the OpenAI API.

## Examples
Below are some example use cases:

## Searching for Relevant Text
The search_embedding(question) function in queryKnowledgeBase.py searches the knowledge base for relevant text based on a user's question. The system retrieves relevant text chunks and displays their sources.

## Generating Answers
The answer_question(question, relevant_text) function in queryKnowledgeBase.py uses the OpenAI API to generate answers to questions using relevant text from the knowledge base. The generated answers are displayed on the interface.

## Interactive Web Interface
The Flask web interface provides an interactive platform for users to enter questions, receive answers, and explore relevant text and document summaries.




