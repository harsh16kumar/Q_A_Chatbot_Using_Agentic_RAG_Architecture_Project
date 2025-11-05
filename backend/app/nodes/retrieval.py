def retrieve_docs(state, retriever):
    print("---RETRIEVING DOCUMENTS---")
    question = state.get("question", "")
    if not question:
        return {**state, "documents": []}
    documents = [doc.page_content for doc in retriever.invoke(question)]
    print(f"Retrieved {len(documents)} documents.")
    return {**state, "documents": documents}
