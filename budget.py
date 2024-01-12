import streamlit as st 
import app_management
import deta

def main():
    # Start by logging in with the password
    if not app_management.check_password():
        st.stop()

    st.title('Financieel Overzicht')

    db = app_management.connect_deta()

    with st.form("form"):
        name = st.text_input("Your name")
        age = st.number_input("Your age")
        submitted = st.form_submit_button("Store in database")
    if submitted:
        db.put({"name": name, "age": age})

    db_content = db.fetch().items
    st.write(db_content)

if __name__ == '__main__':
    main()