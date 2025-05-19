from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS


load_dotenv()

loader = TextLoader("./system_message.txt")
docs = loader.load()

# print((docs[30]))
# print(f"Total characters: {len(docs[30].page_content)}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # chunk size (characters)
    chunk_overlap = 100,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
    # separators=['--Section End--'], 
    keep_separator=False
)
all_splits = text_splitter.split_documents(docs)

print(f"Split data into {len(all_splits)} sub-documents.")
# print(all_splits)

# #Embedding the chunks
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

embedding_dim = len(embeddings.embed_query("hello world"))
index = faiss.IndexFlatL2(embedding_dim)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

vector_store.add_documents(documents=all_splits)


vector_store.save_local("faiss_index")



