from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool
from langchain.tools.retriever import create_retriever_tool
from dotenv import load_dotenv
from get_stats import get_dqr_summary

# --- Load vector store and create retriever ---
load_dotenv()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 240})

# --- Define tools ---
# retriever_tool = create_retriever_tool(
#     retriever,
#     name="document_search",
#     description="Use this tool to search DQR knowledge base to find relevant document content."
# )

get_dqr_tool = StructuredTool.from_function(
    func=get_dqr_summary,
    name="get_dqr_summary",
    description=(
        "Returns DQR summary stats for a given state_code, month, LOB, feed, stat_file, and column. "
        "Use this to answer demographic or member count queries."
    )
)

tools = [get_dqr_tool]

# --- Create LLM and memory ---
llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0.5)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="output"
)

# --- Define system prompt ---
system_prompt = (
    "You are an AI assistant that helps users interpret DQR reports using stat files like EDD, FreqDist, DAT, "
    "Merge_Stats, and others. Use the retrieved context to understan which of these files to use and available tools to answer accurately.\n\n"
    "When calling the tool `get_dqr_summary`, always provide the **2-letter state code** "
    "(e.g., use 'FL' instead of 'Florida', 'CA' instead of 'California').\n\n"
    "Instructions:\n"
    "- Always use the provided context to answer questions about DQR reports and stat files.\n"
    "- If a user asks about a specific state, month, LOB, feed, stat_file, or column, ensure you extract and use these details when calling tools.\n"
    "- If information is missing, ask clarifying questions before proceeding.\n"
    "- Prefer concise, factual answers. Do not speculate or fabricate information.\n"
    "- If the context does not contain the answer, reply with 'I don't know.'\n"
    "- When referencing files or measures, use their exact names as shown in the context.\n"
    "- If the user asks for definitions or explanations, use the context or state that the information is not available.\n"
    "{context}\n\n"
    "If the answer isn't found, respond with 'I don't know.'"
)

# --- Assemble prompt ---
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}"),
    MessagesPlaceholder("agent_scratchpad"),
    MessagesPlaceholder("chat_history")
])

# --- Build agent ---
agent = create_openai_functions_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

# --- Helper: Get context ---
def get_context_for_query(query: str) -> str:
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join(doc.page_content for doc in docs)
    print("\n--- Retrieved Context ---\n", context, "\n------------------------\n")
    return context

# --- Query Handler ---
def process_query(query: str) -> str:
    context = get_context_for_query(query)
    response = agent_executor.invoke({
        "question": query,
        "context": context
    })
    return response["output"]

# --- Main Execution ---
if __name__ == "__main__":
    query = "What are the quality measures present in SC."
    answer = process_query(query)
    print("\nAnswer:\n", answer)
