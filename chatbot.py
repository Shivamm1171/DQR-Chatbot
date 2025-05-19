import openai
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import os
import json
from tabulate import tabulate
import plotly.graph_objects as go
import pandas as pd
from system_message import save_system_message_to_file
from get_stats import get_dqr_summary, plot_chart, adhoc_checks
from cmp_dqr_csvs import cmp_dqr
from tools import tools

load_dotenv()

#constants
MODEL = 'gpt-4.1-mini'
CLIENT = 'Molina'

st.set_page_config(page_title="DQR Chatbot", layout="wide")
st.title("🤖 DQR Chatbot")
st.markdown("Ask me anything about your data quality reports.")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

nameInput = st.text_input("Your Name", placeholder="Your Name")
userInput = st.text_input("Your Query", placeholder="e.g. What is the top Member Gender in Arizona?")

#system message
save_system_message_to_file()
with open("system_message.txt", "r") as f:
    system_message = f.read()

# Saving conversation

def save_chat_to_markdown(filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# 📝 Chat Transcript\n\n")
        for message in st.session_state.chat_history[1:]:  # Skip the system message
            if message["role"] == "user":
                f.write(f"**You:** {message['content']}\n\n")
            elif message["role"] == "function":
                f.write(f"**Function** {message['content']}\n\n")
            elif message["role"] == "assistant":
                f.write(f"**DQR Bot:** {message['content']}\n\n")


def run(name_input=nameInput, user_input=userInput):
    if (name_input == 'Automated Testing' or (st.button("Start new chat")) and user_input.strip()):

        print('-' * 100)

        st.write(f"**You:** {user_input.strip()}")

        response_container = st.empty()

        # Clear chat history for every new request
        st.session_state.chat_history = []
        chat_history = []  # Separate list to return

        # Append system and user message to history
        st.session_state.chat_history = [{"role": "system", "content": system_message}]
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "user", "content": user_input})  # Add to return list

        # Call OpenAI API
        response = openai.chat.completions.create(
            model= MODEL, 
            messages=st.session_state.chat_history,
            temperature = 0.2,
            tools = tools,
            # tool_choice = "required"
        )

        tool_data_chunks = pd.DataFrame()

        message = response.choices[0].message
        print('Message - ', message)
        # If tool was called
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Check if it's get_dqr_summary function
                if function_name == "get_dqr_summary":
                    table_data = get_dqr_summary(**function_args)
                    
                    tool_response = tabulate(table_data, headers='keys', tablefmt='grid', showindex=False)

                    # Return result as string
                    tool_response_str = json.dumps(tool_response, indent=2)

                # Check if it's get_dqr_summary function
                elif function_name == "adhoc_checks":
                    table_data = adhoc_checks(**function_args)
                    print(type(table_data))
                    tool_response = {name: df.to_dict() for name, df in table_data.items()}

                    adhoc_checks_message = """
                    Use this context from the adhoc checks and derive insights from it to present them to the user very concisely.
                    When generating insights for ineligible and pharmacy claims, please also compare them with the respective medical and pharmacy total claim amounts.
                    Hosp and prof medical claims amount should be added and then compared with the total medical claims amount.
                    """

                    # Return result as string
                    tool_response_str = adhoc_checks_message +  str(tool_response)

                    # print('Tool response - ', tool_response_str)
 
                elif function_name == "cmp_dqr":
                    table_data = ''
                    try:
                        tool_response_str = cmp_dqr(**function_args)
                    except:
                        tool_response_str = 'Comparison data not present for this market'

                # Append function result to chat history
                st.session_state.chat_history.append({
                    "role": "function",
                    "name": function_name,  
                    "content": tool_response_str
                })
                chat_history.append({
                    "role": "function",
                    "name": function_name,  
                    "content": tool_response_str
                })
                
                if type(table_data) == pd.DataFrame:
                    tool_data_chunks = pd.concat([tool_data_chunks, table_data])

            # Now make a second call to complete the conversation
            second_response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    *st.session_state.chat_history,
                    {
                        "role": "system",
                        "content": "First provide a complete text response that answers the user's question concisely. After that, you may use the plot_chart tool if a visualization would be helpful."
                    }
                ],
                stream = True,
                tools = [tool for tool in tools if tool["function"]["name"] == "plot_chart"]
                )
            
            
            final_reply = ''
            assistant_reply = {"role": "assistant", "content": ""}
            st.session_state.chat_history.append(assistant_reply)
            chat_history.append(assistant_reply)  # Add to return list

            tool_calls = {}
            current_tool_call = None
            has_content = False

            
            for chunk in second_response:
                delta = chunk.choices[0].delta

                print('delta - ',delta)

                # Handle content
                if delta.content:
                    has_content = True
                    assistant_reply["content"] += delta.content.replace("_", "\\_").replace("\n", "  \n")
                    response_container.markdown(f"**DQR Bot({MODEL}):** {assistant_reply['content']}")
                    final_reply += delta.content
                
                # Only handle tool calls after we've received some content
                if has_content and delta.tool_calls:
                    for call in delta.tool_calls:
                        if call.id:
                            # New tool call
                            current_tool_call = call.id
                            tool_calls[current_tool_call] = {
                                "function": {
                                    "name": call.function.name,
                                    "arguments": call.function.arguments or ""
                                }
                            }
                        elif current_tool_call:
                            # Continue existing tool call
                            if call.function.name:
                                tool_calls[current_tool_call]["function"]["name"] = call.function.name
                            if call.function.arguments:
                                tool_calls[current_tool_call]["function"]["arguments"] += call.function.arguments

            # Displaying the data chunk used for second response
            if not tool_data_chunks.empty:
                st.markdown("**Data Chunk Used:**")             
                st.table(tool_data_chunks)

            # Execute any tool calls that were collected
            for tool_call_id, tool in tool_calls.items():
                function_name = tool["function"]["name"]
                function_arguments = json.loads(tool["function"]["arguments"])
                
                if function_name == "plot_chart":
                    print(f'Function {function_name} called with arguments {function_arguments}')
                    tool_response = plot_chart(**function_arguments)
                    tool_response = json.loads(tool_response["chart"])
                    # Add the tool response to chat history
                    st.session_state.chat_history.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(tool_response, indent=2)
                    })
                    chat_history.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(tool_response, indent=2)
                    })
                    # Display the Plotly chart
                    fig = go.Figure(tool_response)
                    st.plotly_chart(fig)

            # Update the final reply in chat history
            assistant_reply["content"] = final_reply
        
        else:
            # No function call
            reply = message.content
            st.markdown(f"**DQR Bot({MODEL}):**\n\n{reply.replace('\n', '  \n')}")
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            chat_history.append({"role": "assistant", "content": reply})  # Add to return list

        #Saving conversation
        if name_input == 'Automated Testing':
            return chat_history  # Return the separate chat history list
        else:
            os.makedirs(fr"Chat_log/{name_input}", exist_ok=True)
            filename = os.path.join("Chat_log", name_input, f"dqr_chat_log_{datetime.now().strftime("%H%M%S")}.md")

            save_chat_to_markdown(filename)
            st.success(f"Chat saved!")

# print('Chat his', st.session_state.chat_history[1:])


# if st.button("💾 Save Chat"):
    
#     os.makedirs("Chat_log", exist_ok=True)
#     filename = os.path.join("Chat_log", name_input, f"dqr_chat_log_{datetime.now().strftime("%H%M%S")}.md")

#     save_chat_to_markdown(filename)
#     st.success(f"Chat saved to {filename}!")

# --- Display chat history ---

# for message in st.session_state.chat_history[1:]:  # Skip system message
#     if message["role"] == "user":
#         st.markdown(f"**You:** {message['content']}")
#     elif message["role"] == "function":
#         st.markdown(f"**DQR Bot:** {message['content']}")
#     elif message["role"] == "assistant":
#         st.markdown(f"**DQR Bot:** {message['content']}")
    
if __name__ == "__main__":
    run()