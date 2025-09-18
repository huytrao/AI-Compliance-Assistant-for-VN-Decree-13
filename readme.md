![Media1.gif](images/Media1.gif)

# Vietnamese AI Checker for Data Privacy

## Project Goal

Build a simple application where you can:

*   **Upload a document:** For example, a company's "Privacy Policy".
*   **Ask questions related to that document:** For example, "Does this policy mention obtaining user consent before processing sensitive data? Which article in Decree 13 regulates this?"
*   **Receive intelligent answers:** The system will use its knowledge from Decree 13 to analyze the document and answer your question, citing the relevant articles.

## How does the RAG architecture work in this project?

*   **"Knowledge Base":** The entire text of Decree 13/2023/NĐ-CP.
*   **Retrieval:** When you ask a question, the system searches the "knowledge base" to find the most relevant articles and regulations in Decree 13.
*   **Augmentation:** The system takes the retrieved articles + the document you uploaded + your question, and "packages" them all into a context-rich prompt.
*   **Generation:** This package of information is sent to a Large Language Model (LLM). The LLM will generate the final answer based on the provided context.