import streamlit as st

from dotenv import load_dotenv # langfuse or opik
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.memory import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import (
                                        SystemMessagePromptTemplate,
                                        HumanMessagePromptTemplate,
                                        ChatPromptTemplate,
                                        MessagesPlaceholder
                                        )


from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

from langchain_core.output_parsers import StrOutputParser

load_dotenv()

st.set_page_config(page_title="DQR Chatbot", page_icon="🤖", layout="wide")
st.title("📊 DQR Chatbot - Data Quality Reporting")

llm = ChatOpenAI(model="o1-mini")
user_id = st.text_input("Enter your user id", "FirstName")
input_text = st.text_input("Enter your message", "")


def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///chat_history.db")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Start New Conversation"):
    st.session_state.chat_history = []
    history = get_session_history(user_id)
    history.clear()


for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Define prompt template for intent classification
human = HumanMessagePromptTemplate.from_template("""                                          
   You are an AI assistant that has access to the below tables:
    Table 1: State or Market and LOB (Line of business) information
    ---------------------------------------------------------------
| LOB       | Shore     | Group | State              |
---------------------------------------------------------------
| Medicaid  | onshore  | 0     | Arizona            |
| Medicaid  | onshore  | 0     | Virginia           |
| Medicaid  | onshore  | 3     | New Mexico         |
| Medicaid  | onshore  | 1     | Mississippi        |
| Medicaid  | onshore  | 0     | Ohio               |
| Medicaid  | onshore  | 1     | Kentucky           |
| Medicaid  | onshore  | 1     | New York           |
| Medicaid  | onshore  | 0     | Texas              |
| Medicaid  | onshore  | 2     | Washington         |
| Medicaid  | offshore | 0     | Nevada             |
| Medicaid  | offshore | 0     | Florida            |
| Medicaid  | offshore | 1     | South Carolina     |
| Medicaid  | offshore | 1     | Michigan           |
| Medicaid  | offshore | 2     | Utah               |
| Medicaid  | offshore | 2     | Wisconsin          |
| Medicaid  | offshore | 2     | Illinois           |
| Medicaid  | offshore | 3     | Idaho              |
| Medicaid  | offshore | 3     | Massachusetts      |
| Medicaid  | offshore | 3     | Nebraska           |
| Medicaid  | offshore | 3     | Iowa               |
| Medicare  | onshore  | 1     | Washington         |
| Medicare  | onshore  | 1     | Arizona            |
| Medicare  | onshore  | 2     | Virginia           |
| Medicare  | onshore  | 1     | Ohio               |
| Medicare  | onshore  | 2     | Texas              |
| Medicare  | offshore | 2     | Nevada             |
| Medicare  | offshore | 2     | South Carolina     |
| Medicare  | offshore | 1     | Utah               |
| Medicare  | offshore | 3     | Massachusetts      |
| Medicare  | offshore | 1     | Idaho              |
| Medicare  | offshore | 2     | Kentucky           |
| Medicare  | offshore | 2     | New York           |
| Medicare  | offshore | 2     | Wisconsin          |
| Medicare  | offshore | 1     | Illinois           |
| Medicare  | offshore | 1     | Michigan           |

Table 2: file type and column present in file information
--------------------------------------------------------------
file_type                | InternalColumnName                
--------------------------------------------------------------
Members                  | Coverage_Effective_Date          
Members                  | Coverage_Term_Date              
Members                  | Health_Plan_State_Code          
Members                  | Medicaid_State_ID               
Members                  | Member_Date_Of_Birth           
Members                  | Member_Date_Of_Death           
Members                  | Member_Ethnicity_or_Race       
Members                  | Member_First_Name              
Members                  | Member_Gender                  
Members                  | Member_GL_Product_Name         
Members                  | Member_Health_Plan_COB_Effective_Date
Members                  | Member_Health_Plan_COB_Status  
Members                  | Member_Health_Plan_COB_Termination_Date
Members                  | Member_Health_Plan_Enrollment_Effective_Date
Members                  | Member_Health_Plan_Enrollment_Termination_Date
Members                  | Member_Health_Plan_Line_Of_Business
Members                  | Member_Health_Plan_Product     
Members                  | Member_ID                      
Members                  | Member_Language                
Members                  | Member_Last_Name               
Members                  | Member_Middle_Name             
Members                  | Member_Relationship           
Members                  | Member_Residence_Country      
Members                  | Member_Residence_Mailing_City 
Members                  | Member_Residence_Mailing_County_Code
Members                  | Member_Residence_Mailing_County_Code_Description
Members                  | Member_Residence_Mailing_State
Members                  | Member_Residence_Mailing_Street_Address1
Members                  | Member_Residence_Mailing_Street_Address2
Members                  | Member_Residence_Mailing_ZIP_Code
Members                  | Member_Residence_Physical_City
Members                  | Member_Residence_Physical_County_Code
Members                  | Member_Residence_Physical_County_Code_Description
Members                  | Member_Residence_Physical_State
Members                  | Member_Residence_Physical_Street_Address1
Members                  | Member_Residence_Physical_Street_Address2
Members                  | Member_Residence_Physical_ZIP_Code
Members                  | Plan_ID                        
Members                  | Program_Description           
Members                  | Program_ID                    
Members                  | Rate_Code                     
Members                  | SegType                       
Members                  | Subscriber_ID                 
Members                  | SysSourceName                 
--------------------------------------------------------------
Non Claims Expenses      | Member_ID                      
Non Claims Expenses      | payto_name                     
Non Claims Expenses      | payto_provider_id              
Non Claims Expenses      | planid                         
Non Claims Expenses      | cap_1                          
Non Claims Expenses      | cap_2                          
Non Claims Expenses      | cap_3                          
Non Claims Expenses      | cap_4                          
Non Claims Expenses      | cap_5                          
Non Claims Expenses      | cap_dcr                        
Non Claims Expenses      | cap_dental                     
Non Claims Expenses      | cap_dme                        
Non Claims Expenses      | cap_global                     
Non Claims Expenses      | cap_hearing                    
Non Claims Expenses      | cap_hospital                   
Non Claims Expenses      | cap_incentive_pool_liab        
Non Claims Expenses      | cap_lab                        
Non Claims Expenses      | cap_mental_health              
Non Claims Expenses      | cap_nonrisk                    
Non Claims Expenses      | cap_nurse                      
Non Claims Expenses      | cap_pcp                        
Non Claims Expenses      | cap_specialty                  
Non Claims Expenses      | cap_therapy                    
Non Claims Expenses      | cap_total                      
Non Claims Expenses      | cap_transportation             
Non Claims Expenses      | cap_vision                     
Non Claims Expenses      | exp_med_1                      
Non Claims Expenses      | exp_med_2                      
Non Claims Expenses      | exp_med_3                      
Non Claims Expenses      | exp_med_4                      
Non Claims Expenses      | exp_med_5                      
Non Claims Expenses      | exp_med_addl_total             
Non Claims Expenses      | exp_med_addl_total_excl_qa     
Non Claims Expenses      | exp_med_csr                    
Non Claims Expenses      | exp_med_hc_saving_fee          
Non Claims Expenses      | exp_med_ntwk_access_fee        
Non Claims Expenses      | exp_med_other_cost             
Non Claims Expenses      | exp_med_other_recov            
Non Claims Expenses      | exp_med_part_d_reins_lics      
Non Claims Expenses      | exp_med_pat_transportation     
Non Claims Expenses      | exp_med_prov_incentive         
Non Claims Expenses      | exp_med_qa                     
Non Claims Expenses      | exp_med_reins_prem             
Non Claims Expenses      | exp_med_reins_prem_fed         
Non Claims Expenses      | exp_med_reins_recov            
Non Claims Expenses      | exp_med_reins_recov_fed        
Non Claims Expenses      | exp_med_value_added            
Non Claims Expenses      | SysSourceName                  
--------------------------------------------------------------
PCP Attribution          | Member_ID                      
PCP Attribution          | PCP_Provider_ID                
PCP Attribution          | PayTo_Provider_ID              
PCP Attribution          | PayTo_Affil_Type               
PCP Attribution          | PCP_Effective_Date             
PCP Attribution          | PCP_Termination_Date           
PCP Attribution          | SysSourceName                  
--------------------------------------------------------------
Pharmacy Claims         | AHFS_Therapeutic_ClassCode      
Pharmacy Claims         | AHFS_Therapeutic_ClassCode_Description
Pharmacy Claims         | Check_Number                   
Pharmacy Claims         | Claim_Health_Plan_Code         
Pharmacy Claims         | Claim_Line_of_Business         
Pharmacy Claims         | Claim_Number                   
Pharmacy Claims         | Claim_Sequence_Number          
Pharmacy Claims         | Claim_Status                   
Pharmacy Claims         | Compound_DrugFlag              
Pharmacy Claims         | Dispense_as_Written_Status_Indicator
Pharmacy Claims         | Dispensing_Provider_Network_Status
Pharmacy Claims         | Dispensing_ProviderID          
Pharmacy Claims         | Drug_Type                      
Pharmacy Claims         | Fill_Number                    
Pharmacy Claims         | Formulary_Indicator            
Pharmacy Claims         | Maintenance_Drug_Indicator     
Pharmacy Claims         | Member_Enrollment_Period       
Pharmacy Claims         | Member_Full_Name               
Pharmacy Claims         | Member_Health_Plan_Coverage_Tier
Pharmacy Claims         | Member_ID                      
Pharmacy Claims         | NDC_Description_DrugName       
Pharmacy Claims         | Not_Covered_Reason_Code        
Pharmacy Claims         | Pharmacy_Name                  
Pharmacy Claims         | Pharmacy_Number_NABP           
Pharmacy Claims         | Pharmacy_ZIP_Code              
Pharmacy Claims         | Prescriber_Address             
Pharmacy Claims         | Prescriber_City                
Pharmacy Claims         | Prescriber_Zip_Code            
Pharmacy Claims         | Prescribing_ProviderID         
Pharmacy Claims         | Prescribing_ProviderName       
Pharmacy Claims         | Prescribing_ProviderNPI        
Pharmacy Claims         | Prescription_number            
Pharmacy Claims         | Primary_Payer_Indicator        
Pharmacy Claims         | Prior_Claim_Number             
Pharmacy Claims         | Date_Claim_Received            
Pharmacy Claims         | Date_Claim_Processed_or_Adjudicated
Pharmacy Claims         | Date_Claim_Paid                
Pharmacy Claims         | Claim_Create_Date              
Pharmacy Claims         | product_NDC_code               
Pharmacy Claims         | Fill_Date                      
Pharmacy Claims         | Days_Supply_Dispensed          
Pharmacy Claims         | Unit_Quantity_Dispensed        
Pharmacy Claims         | Copayment_Amount               
Pharmacy Claims         | Deductible_Amount              
Pharmacy Claims         | Coinsurance_Amount             
Pharmacy Claims         | Coordination_of_BenefitsSavings_Amount
Pharmacy Claims         | Allowed_Amount                 
Pharmacy Claims         | Rx_Paid_Amount                 
Pharmacy Claims         | Billed_Amount                  
Pharmacy Claims         | Not_Covered_Amount             
Pharmacy Claims         | Provider_Discount_Amount       
Pharmacy Claims         | Rx_Administrative_Fee          
Pharmacy Claims         | Rx_ClaiM_Type_Retail_Mail_Order
Pharmacy Claims         | Rx_Dispensing_Fee              
Pharmacy Claims         | Rx_Ingredient_Cost             
Pharmacy Claims         | Rx_Sales_Tax                   
Pharmacy Claims         | Transaction_Type               
Pharmacy Claims         | SysSourceName                  
--------------------------------------------------------------

Table 3 : Data Checks implemented on various files
---------------------------------------------------------------
| File Type                | Check                                        |
---------------------------------------------------------------
| Members                  | Members with overlapping enrollment spells  |
| Members                  | Members with overlapping COB enrollment spells  |
| Members                  | Members with overlapping coverage spells  |
| Members                  | Members with Enrollment Effective Date after Enrollment Termination Date  |
| Members                  | Members with COB Effective Date after COB Termination Date  |
| Members                  | Members with Deceased Date after Enrollment Termination Date  |
| Members                  | Members with Deceased Date before Enrollment Termination Date  |
| Members                  | Members with Deceased Date before COB Termination Date  |
| Medical Claims           | Claim IDs/Line-Item Numbers associated with multiple members  |
| Medical Claims           |                                              |
| Medical Claims           | Records with invalid Servicing Provider IDs  |
| Medical Claims           | Records with invalid Payto Provider IDs      |
| Medical Claims           | Records with invalid Servicing Provider NPIs  |
| Medical Claims           | Records with invalid Referring Provider NPIs  |
| Medical Encounters       | Claim IDs/Line-Item Numbers associated with multiple members  |
| Medical Encounters       |                                              |
| Medical Encounters       | Records with invalid Servicing Provider IDs  |
| Medical Encounters       | Records with invalid Payto Provider IDs      |
| Medical Encounters       | Records with invalid Servicing Provider NPIs  |
| Medical Encounters       | Records with invalid Referring Provider NPIs  |
| Pharmacy Claims          | Claim IDs/Line-Item Numbers associated with multiple members  |
| Pharmacy Claims          |                                              |
| Pharmacy Claims          | Records with invalid Prescribing Provider NPIs  |
| Pharmacy Claims          | Records where NDC codes are missing or all same digit  |
| Capitation               | Records with $0 Capitated Amount            |
| Capitation               | Records with invalid Provider IDs           |
| Revenue                  | Records with $0 Premium Amount              |
| PCP Attribution          | Records with Termination Date less than Effective Date  |
| PCP Attribution          | Records with invalid Payto Provider IDs      |
| PCP Attribution          | Records with invalid Provider IDs           |
| PCP Attribution          | Overlapping enrollment spells               |
| Provider                 | Records with invalid Provider IDs           |
| Provider                 | Records with invalid Provider Payto IDs     |
| Provider                 | Records with invalid Provider NPIs          |
| Provider                 | Records with invalid Provider Payto NPIs    |
| Provider Service Location| Records with invalid Provider IDs           |
| Provider Service Location| Records with invalid Provider Payto IDs     |
| Provider Service Location| Records with invalid Provider Payto Facility IDs  |
| Provider Service Location| Records with Service Location Termination Date less than Effective Date  |
| Provider Contract History| Records with invalid Provider IDs           |
| Provider Contract History| Records with Payto Provider Termination Date less than Payto Provider Effective Date  |
| TINs and APM             | Records with Termination Date less than Effective Date  |
| TINs and APM             | Records with Start Date less than End Date  |
| VBP Roster               | Records with Effective Date less than Termination Date  |
---------------------------------------------------------------

Table 4: Merge Statistics between files on given columns mentioned as merge keys
--------------------------------------------------------------------------------------------------------
| File Type 1                 | File 1 Merge Key             | File Type 2             | File 2 Merge Key         |
--------------------------------------------------------------------------------------------------------
| Capitation                   | Member_ID                   | Members                 | Member_ID                 |
| Revenue                      | Member_ID                   | Members                 | Member_ID                 |
| PCP Attribution              | Member_ID                   | Members                 | Member_ID                 |
| Non Claims Expenses          | Member_ID                   | Members                 | Member_ID                 |
| Quality Gaps Pro             | Member_ID                   | Members                 | Member_ID                 |
| Quality Gaps Retro           | Member_ID                   | Members                 | Member_ID                 |
| Risk Gaps                    | Member_ID                   | Members                 | Member_ID                 |
| Medical Claims               | Member_ID                   | Members                 | Member_ID                 |
| Medical Encounters           | Member_ID                   | Members                 | Member_ID                 |
| Pharmacy OTC                 | Member_ID                   | Members                 | Member_ID                 |
| Pharmacy Claims              | Member_ID                   | Members                 | Member_ID                 |
| Risk Score                   | Member_ID                   | Members                 | Member_ID                 |
| Capitation                   | Provider_ID                 | Provider                | Provider_ID               |
| Capitation                   | Provider_NPI                | Provider                | Provider_NPI              |
| Capitation                   | PayTo_Provider_ID           | Provider                | Provider_Payto_ID         |
| Capitation                   | PayTo_NPI                   | Provider                | Provider_Payto_NPI        |
| Capitation                   | PayTo_TIN                   | Provider                | Provider_Payto_TIN        |
| PCP Attribution              | PCP_Provider_ID             | Provider                | Provider_ID               |
| PCP Attribution              | PayTo_Provider_ID           | Provider                | Provider_Payto_ID         |
| Revenue                      | Rate_Code                   | Rate Code               | Rate_Code                 |
| Non Claims Expenses          | Rate_Code                   | Rate Code               | Rate_Code                 |
| Medical Claims               | Servicing_Provider_ID       | Provider                | Provider_ID               |
| Medical Claims               | PayTo_Provider_ID           | Provider                | Provider_Payto_ID         |
| Medical Claims               | Servicing_Provider_NPI      | Provider                | Provider_NPI              |
| Medical Claims               | Referring_Provider_NPI      | Provider                | Provider_NPI              |
| Medical Claims               | PayTo_Provider_TIN          | Provider                | Provider_Payto_TIN        |
| Medical Encounters           | Servicing_Provider_ID       | Provider                | Provider_ID               |
| Medical Encounters           | PayTo_Provider_ID           | Provider                | Provider_Payto_ID         |
| Medical Encounters           | Servicing_Provider_NPI      | Provider                | Provider_NPI              |
| Medical Encounters           | Referring_Provider_NPI      | Provider                | Provider_NPI              |
| Medical Encounters           | PayTo_Provider_TIN          | Provider                | Provider_Payto_TIN        |
| Pharmacy Claims              | Dispensing_ProviderID       | Provider                | Provider_ID               |
| Pharmacy Claims              | Prescribing_ProviderID      | Provider                | Provider_ID               |
| Pharmacy Claims              | Prescribing_ProviderNPI     | Provider                | Provider_NPI              |
| Provider Contract History     | Provider_ID                 | Provider                | Provider_ID               |
| Provider Contract History     | Payto_Provider_ID           | Provider                | Provider_Payto_ID         |
| Provider Contract History     | Program_ID                 | Members                 | Program_ID                |
| Provider Service Location     | Provider_ID                 | Provider                | Provider_ID               |
| Provider Service Location     | Provider_Payto_ID          | Provider                | Provider_Payto_ID         |
| Medical Claims Supl          | Claim_Number                | Medical Claims          | Claim_Number              |
| Medical Encounters Supl      | Claim_Number                | Medical Encounters      | Claim_Number              |
| VBP Roster                   | PayTo_Provider_TIN         | Provider                | Provider_Payto_TIN        |
| VBP Roster                   | PayTo_Provider_TIN         | UAC File                | PaytoTIN                  |
| Medical Encounters           | PayTo_Provider_TIN         | UAC File                | PaytoTIN                  |
| Medical Claims               | PayTo_Provider_TIN         | UAC File                | PaytoTIN                  |
| Capitation                   | PayTo_TIN                   | UAC File                | PaytoTIN                  |
| Medical Claims               | Servicing_Provider_NPI      | UAC File                | RenderingProviderNPI      |
| Medical Claims               | Referring_Provider_NPI      | UAC File                | RenderingProviderNPI      |
| Medical Encounters           | Servicing_Provider_NPI      | UAC File                | RenderingProviderNPI      |
| Medical Encounters           | Referring_Provider_NPI      | UAC File                | RenderingProviderNPI      |
| Pharmacy Claims              | Prescribing_ProviderNPI     | UAC File                | RenderingProviderNPI      |
| Operational Membership       | Member_ID                   | Quality Gaps Pro QDRM   | member_id                 |
--------------------------------------------------------------------------------------------------------

Also what kind of summary the user is looking for should lie in one of the below categories:

EDD : Contains statistics like sum, average or mean, unique count, min and max, total count, null count for each of the columns. Doesnot know the value present in the column.
                                                 Just has the 1 number for each stat for each column

FREQ DIST : Contains the unique values of the column and the frequency of each  value in the column.
            Example : What values of 'Claim Type' are we receiving in the data and what is it's frequency

DAT : Contains the data distributed by Year. Has the number of records for each year based on a date column.
      Example: WHat is the distinct count of claims in the Medical Claims file in 2024?

MERGE : If the user is asking for any of the merges specified in TABLE 4 above.
    Example: No of Mermbers common in merber file and medical claims file.

DQC :  If the user is asking for any of the custom checks specified in TABLE 3 above.

Claim Distribution : If the user want to see the breakout of claims by year or month or anything related to that then select this.

Member Attribution : If the user wants to see the count of attributed members by program or aco or year.

Lastly, files received in which paid though cycle should be used for the analysis.

SOme examples are :
 --PTDEC 2024 if the user wants to use feed files received in Paid though december data in 2024.
 -- PTNOV 2024 if the user wants to use feed files received in Paid though November data in 2024.

    Carefully read the user question below and determine the following .You need to return the following values 
    1. state,
    2. line of business
    3. paid through cycle
    4. file and column
    5. summary type 
                                                 
    User Question: {input}
    Answer:
    """)

messages = [MessagesPlaceholder(variable_name='history'), human]

prompt = ChatPromptTemplate(messages=messages)

intent_chain = prompt | llm | StrOutputParser()


runnable_with_history = RunnableWithMessageHistory(intent_chain, get_session_history, 
                                                   input_messages_key='input', 
                                                   history_messages_key='history')

def chat_with_llm(session_id, input):
    for output in runnable_with_history.stream({'input': input}, config={'configurable': {'session_id': session_id}}):

        yield output

if input_text:
    st.session_state.chat_history.append({'role': 'user', 'content': input_text})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(chat_with_llm(user_id, input_text))

    st.session_state.chat_history.append({'role': 'assistant', 'content': response})