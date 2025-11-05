import faiss
index = faiss.read_index("C:/Users/Harsh/Downloads/Q_A_Chatbot_Using_Agentic_RAG_Architecture/q_a_chatbot/data/embeddings/resume/resume_index/index.faiss")
print("Stored FAISS vector dimension:", index.d)
index_2 = faiss.read_index("C:/Users/Harsh/Downloads/Q_A_Chatbot_Using_Agentic_RAG_Architecture/q_a_chatbot/data/embeddings/projects/projects_index.faiss")
print("Stored FAISS vector dimension:", index_2.d)
