import streamlit as st
import app_management
import pandas as pd

st.set_page_config(layout="wide")

def reset_base():
    with st.form('delete_base'):
        st.subheader('Verwijder alle transacties')
        st.info('ℹ️ Dit verwijdered alle transacties, dit kan niet teruggedraaid worden!')
        submit = st.form_submit_button('Verwijderen')
    if submit:
        db = app_management.connect_main_deta()
        df = pd.DataFrame(db.fetch().items)

        for key in df['key']:
            db.delete(key)


def main():
    # Start by logging in with the password
    if not app_management.check_password():
        st.stop()

    reset_base()

if __name__ == '__main__':
    main()