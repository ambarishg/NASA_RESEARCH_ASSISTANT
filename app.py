import streamlit as st
from config import *
from qdrant_helper import *
from pathlib import Path
from azure_openai_helper import *
from streamlit_chat import message

conversation=[{"role": "system", "content": "You are a helpful assistant."}]

st.set_page_config(page_title="NASA Search Engine", 
                   page_icon="🔍",
                   layout="wide",)


st.title("NASA Search Engine")

search_upload = st.sidebar.radio("Select the Analysis Type", \
                                 ('Recommend ARXIV Papers',
                                  'Recommend ARXIV Influential Papers',
                                  'Recommend NTRS Papers',
                                  'Upload Docs',
                                  'Q&A Docs',
                                 'Chat with Research Documents',
                                 'Documents Info'))

if (search_upload == 'Recommend ARXIV Papers') or (search_upload == 'Q&A Docs'):

    if search_upload == 'Recommend ARXIV Papers':
            st.header("Recommend ARXIV Papers")
            user_input = st.text_area('Enter your question here:',
                                      key="ARXIV")
            author = st.text_input('Enter the author name')
            year = st.text_input('Enter the year')
    else:
        st.header("Q&A Docs")
        user_input = st.text_area('Enter your question here:',key="Q&A_user_input")
        

    if st.button('Get Results'):
        if search_upload == 'Recommend ARXIV Papers':
            reply = get_search_results(user_input,
                                       author.strip(),
                                       year.strip())
            st.dataframe(reply)
        else:
            reply = get_search_document_results(user_input,CATEGORY="")
            st.write(reply)

if search_upload == 'Upload Docs':
     st.header("Upload Docs")
     uploaded_file = st.file_uploader(label = "Upload file", type=["pdf"])
     category = st.text_input('Enter the category of the document')
     short_description = st.text_input('Enter the short description of the document')
     if uploaded_file is not None:
        if st.button('Save File'):
            save_path = Path(SAVED_FOLDER, uploaded_file.name)
            with open(save_path, mode='wb') as w:
                w.write(uploaded_file.getvalue())
            insert_qdrant_doc(uploaded_file.name, short_description,category,)
            st.success('File saved successfully')
            st.balloons()

if search_upload == 'Chat with Research Documents':
    st.header("Chat with Research Documents")
    user_input = st.text_input("Your Question","")
    if user_input !='':
        
        if 'generated' not in st.session_state:
                st.session_state['generated'] = []

        if 'past' not in st.session_state:
            st.session_state['past'] = []

       
        conversation.append({"role": "user", "content": user_input})
        context = get_search_document_results_chat(user_input,CATEGORY="")

        prompt = create_prompt(context,user_input)
        conversation.append({"role": "assistant", "content": prompt})

        reply = generate_answer(conversation)


        st.session_state.past.append(user_input)
        st.session_state.generated.append(reply)

        if st.session_state['generated']:    
            for i in range(len(st.session_state['generated'])-1, -1, -1):
                message(st.session_state["generated"][i], key="NASA" + str(i))
                message(st.session_state['past'][i], is_user=True, key="NASA" + str(i) + "_user")

if search_upload == 'Recommend NTRS Papers':
    st.header("Recommend NTRS Papers")
    user_input = st.text_area('Enter your question here:',
                              key="NTRS")
    year=st.text_input('Enter the year')
    if st.button('Get Results'):
        reply = get_search_results_NTRS(user_input,year.strip())
        st.dataframe(reply)

##################################################################

# SECTION NAME - Documents Info

###################################################################
if search_upload == 'Documents Info':
    st.header("Documents Info")
    reply = get_documents_metadata()
    st.dataframe(reply)

##################################################################

# SECTION NAME - ARXIV Influential papers

###################################################################
if search_upload == 'Recommend ARXIV Influential Papers':
    st.header("ARXIV Influential papers")
    user_input = st.text_area('Enter your question here:',
                              key="ARXIV_INFLUENTIAL")
    category = st.selectbox('Select the category of the document', \
                                ('','Computer Science',
                                 'Quantitative Biology'))
    print(category)
    authors = st.text_input('Enter the author name')
    if st.button('Get Results'):
        reply = get_influential_papers(user_input,
                                       category.strip(),
                                       authors.strip())
        st.dataframe(reply)