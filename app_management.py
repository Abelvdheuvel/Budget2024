import streamlit as st
import hmac
from deta import Deta

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

def connect_main_deta():
    """Connect to the main database from deta"""
    deta = Deta(st.secrets["key"])
    db = deta.Base("budget_app")
    return db

def connect_filter_deta():
    """Connect to the database with the filters from deta"""
    deta = Deta(st.secrets["key"])
    db = deta.Base("budget_filter_app")
    return db

def connect_category_deta():
    """Connect to the database with the category from deta"""
    deta = Deta(st.secrets["key"])
    db = deta.Base("budget_category_app")
    return db

def connect_to_be_categorised_deta():
    """Connect to the database with the category from deta"""
    deta = Deta(st.secrets["key"])
    db = deta.Base("budget_to_be_cat_app")
    return db

def get_first_letter(s):
    for char in s:
        if char.isalpha() and char.isascii():  # Check if the character is an ASCII alphabet letter
            return char
    return ''