import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
import os
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

# Set page layout to wide
st.set_page_config(layout="wide")

# Load the dataset
file_path = 'trash_detection_data.csv'
df = pd.read_csv(file_path)
df['date'] = pd.to_datetime(df['date'])

# Calculate the waste produced this week and last week
df['week'] = df['date'].dt.isocalendar().week
current_week = df['week'].max()
last_week = current_week - 1

current_week_count = df[df['week'] == current_week].shape[0]
last_week_count = df[df['week'] == last_week].shape[0]

if last_week_count != 0:
    percentage_change = ((current_week_count - last_week_count) / last_week_count) * 100
    more_less = 'more' if percentage_change > 0 else 'less'
else:
    percentage_change = 0
    more_less = 'more'

# Header
st.title('TrashDash Analytics')
st.subheader(f'You produced {abs(percentage_change):.2f}% {more_less} waste than last week.')

# Divider
st.markdown('---')

# Sidebar filters
st.sidebar.header('Filters')
location = st.sidebar.multiselect('Location', df['place'].unique())
trash_type = st.sidebar.multiselect('Trash Type', df['type'].unique())
recyclability_status = st.sidebar.multiselect('Recyclability Status', df['recyclability'].unique())

# Apply filters to dataframe
filtered_df = df.copy()
if location:
    filtered_df = filtered_df[filtered_df['place'].isin(location)]
if trash_type:
    filtered_df = filtered_df[filtered_df['type'].isin(trash_type)]
if recyclability_status:
    filtered_df = filtered_df[filtered_df['recyclability'].isin(recyclability_status)]

# Create two columns for the layout
col1, col2, col3 = st.columns(3)

# First row, column 1 - Distribution of Trash Types
with col1:
    st.markdown('#### Distribution of Trash Types')
    trash_type_counts = filtered_df['type'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(trash_type_counts, labels=trash_type_counts.index, autopct='%1.1f%%', startangle=140)
    ax1.axis('equal')
    st.pyplot(fig1)

# First row, column 2 - Monthly Trash Detection Trend
with col2:
    st.markdown('#### Monthly Trash Detection Trend')
    filtered_df['month'] = filtered_df['date'].dt.to_period('M')
    monthly_counts = filtered_df['month'].value_counts().sort_index()
    fig2, ax2 = plt.subplots()
    monthly_counts.plot(kind='line', marker='o', linestyle='-', color='purple', ax=ax2)
    ax2.set_title('Monthly Trash Detection Trend')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Count')
    ax2.set_xticklabels(monthly_counts.index, rotation=45)
    st.pyplot(fig2)

# Second row, column 1 - Recyclability Status Distribution
with col1:
    st.markdown('#### Recyclability Status Distribution')
    recyclability_counts = filtered_df['recyclability'].value_counts()
    fig3, ax3 = plt.subplots()
    recyclability_counts.plot(kind='bar', color=['green', 'red', 'blue'], ax=ax3)
    ax3.set_title('Recyclability Status Distribution')
    ax3.set_xlabel('Recyclability Status')
    ax3.set_ylabel('Count')
    st.pyplot(fig3)

# Second row, column 2 - Most Frequently Disposed Items (Bar Chart with Color According to Recyclability)
with col2:
    st.markdown('#### Most Frequently Disposed Items')
    top_items = filtered_df['item'].value_counts().head(10)
    top_items_df = filtered_df[filtered_df['item'].isin(top_items.index)]
    top_items_recyclability = top_items_df.groupby(['item', 'recyclability']).size().unstack(fill_value=0)
    fig4, ax4 = plt.subplots()
    top_items_recyclability.plot(kind='bar', stacked=True, color=['green', 'red', 'blue'], ax=ax4)
    ax4.set_title('Recyclability Status of Top Disposed Items')
    ax4.set_xlabel('Item')
    ax4.set_ylabel('Count')
    st.pyplot(fig4)

# Third row, column 1 - Time-Based Analysis of Trash Disposal
with col1:
    st.markdown('#### Time-Based Analysis of Trash Disposal')
    time_counts = filtered_df['time'].apply(lambda x: int(x.split(':')[0])).value_counts().sort_index()
    fig5, ax5 = plt.subplots()
    time_counts.plot(kind='bar', color='skyblue', ax=ax5)
    ax5.set_title('Time-Based Analysis of Trash Disposal')
    ax5.set_xlabel('Hour of the Day')
    ax5.set_ylabel('Count')
    st.pyplot(fig5)

# Third row, column 2 - Chatbot Interface
with col3:
    st.header('Talk to your data!')

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    # Initialize OpenAI client
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Create the language model and agent executor
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    agent_executor = create_pandas_dataframe_agent(
        llm,
        df,
        agent_type="tool-calling",
        verbose=False,
        allow_dangerous_code=True
    )

    # Chat display container
    chat_container = st.container()

    
    # User input container at the bottom
    user_input = st.chat_input("Enter your query here >")
    
                    
    if user_input:
        

        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.spinner("Thinking..."):
            answer = agent_executor.run(user_input)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        #st.chat_message("assistant").write(answer)
    with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] == "assistant":
                    st.chat_message(msg["role"]).write(msg["content"])
                else:
                    st.chat_message("user").write(msg["content"])