import streamlit as st
import chromadb
import pandas as pd

# Initialize the chromadb client
CLIENT = chromadb.Client()

def get_or_create_collection(df):
    # Check if the collection already exists
    try:
        collection = CLIENT.create_collection(name="source_document")
        # Add documents and their IDs from the dataframe
        collection.add(
            documents=df['Description'].tolist(),
            ids=df['Criteria'].astype(str).tolist()
        )
    except chromadb.errors.UniqueConstraintError:
        collection = CLIENT.get_collection(name="source_document")
    return collection

# Streamlit UI
st.title('Document Similarity Finder')

# File upload
first_doc = st.file_uploader("Upload the first document", type="csv")
second_doc = st.file_uploader("Upload the second document", type="csv")

# Number of results to return
n_results = st.number_input("Number of results to return", min_value=1, value=2)

# Query input
query_text = st.text_area("Enter your query", value="""Obligation of the manufacturer to provide information about the legitimate purpose and processing of personal data.
The manufacturer MUST disclose the legitimate purposes of the application and the processing of personal data before installation (e.g. in the description of the app store; see Appendix A) and inform the user about this at least upon initial use.
The evaluator checks whether a description exists and corresponds to the legitimate purposes of the application. The legitimate purposes defined by the manufacturer are used as a basis. A legal review of legality is not necessary.""")

# Session state to keep track of whether the collection has been created
if 'collection_created' not in st.session_state:
    st.session_state.collection_created = False

if first_doc and second_doc and not st.session_state.collection_created:
    df1 = pd.read_csv(first_doc)
    df2 = pd.read_csv(second_doc)

    # Build the collection using the second document
    collection = get_or_create_collection(df2)
    st.session_state.collection_created = True
    st.session_state.collection = collection

if st.session_state.collection_created and query_text:
    # Query the collection
    collection = st.session_state.collection
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )

    # Display the results in a table
    result_df = pd.DataFrame({
        'ID': results['ids'][0],
        'Text': results['documents'][0]
    })
    st.write(result_df)
