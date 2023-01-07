import streamlit as st
from prac1 import main
from streamlit_ace import st_ace

# Spawn a new Ace editor
# content = st_ace()

# Display editor's content as you type
# content
# st.write('dio')

placeholder = '''#include <stdio.h>\n\n// your code here...'''
with st.sidebar:
    st.header('C to Assembly')
    choice = st.radio("Choose input method", ("Online Editor", "Pick a file"))
    
if choice == 'Online Editor':
    content = st_ace(language='c_cpp', theme='dracula',
                     value=placeholder, keybinding='vscode',
                     tab_size=4,)
          
    # filename = st.text_input(label='', placeholder='Enter filename')
        
    # if filename is not None:
    
    #     if st.button('Save file'):
    #         if filename != '':
    #             with open(f'{filename}.c', 'w') as file:
    #                 file.write(content)  
        
                
    #             st.download_button(label='Download .C', data=content,file_name=f'{filename}.c')
    
    if st.button('Run'):
        # remove all the #include statements from the code content
        content = content.split('\n')
        content = [line for line in content if not line.startswith('#')]
        content = '\n'.join(content)
        
        main(content)
        st.write('Finished')
        
     
if choice == 'Pick a file':
    uploaded_file = st.file_uploader("Choose a file")
    
    if uploaded_file is not None:
        print(uploaded_file)
        with open(uploaded_file.name, 'r') as file:
            executable = file.read()
    
        content2 = st_ace(language='c_cpp', theme='dracula',
                     value=executable, keybinding='vscode',
                     tab_size=4,)
        
        # create button to run the code just once
        if st.button('Run'):
            main(content2)
            st.write('Finished')
            
        