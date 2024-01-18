import streamlit as st 
import app_management
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

def filter_new_transactions(df_new_transaction):
    db = app_management.connect_main_deta()
    db_filter = app_management.connect_filter_deta()
    db_category = app_management.connect_category_deta()
    db_to_be_categorised = app_management.connect_to_be_categorised_deta()

    df_category = pd.DataFrame(db_category.fetch().items)
    df_filter = pd.DataFrame(db_filter.fetch().items)

    for index, row in df_filter[df_filter['type'] == 1].iterrows():
        df_new_transaction.loc[df_new_transaction.iloc[:, 17].str.contains(row["filter"], na=False), 'category'] = row["category"]
    
    for index, row in df_filter[df_filter['type'] == 0].iterrows():
        df_new_transaction.loc[df_new_transaction.iloc[:, 2].str.contains(row["filter"], na=False), 'category'] = row["category"]

    df_filtered_transactions = df_new_transaction.loc[df_new_transaction['category'].notna(), [0, 10, 'category']].rename(columns={0:'date', 10:'amount'})
    df_filtered_transactions = pd.merge(df_filtered_transactions, df_category.loc[:, ['name', 'type']], how='left', left_on='category', right_on='name').drop('name', axis=1)
    df_to_be_filtered = df_new_transaction.loc[df_new_transaction['category'].isna(), [0, 2, 3, 10, 17]].rename(columns={0:'date', 2:'accountnumber', 3:'accountname', 10:'amount', 17:'description'})
    df_to_be_filtered = df_to_be_filtered.fillna('-')

    db.put_many(df_filtered_transactions.to_dict(orient='records'))
    db_to_be_categorised.put_many(df_to_be_filtered.to_dict(orient='records'))


def add_new_transactions(db_to_be_categorised):
    with st.form('new_transaction'):
        st.subheader('Upload een bankafschrift')
        new_transaction_file = st.file_uploader('Upload een csv', type='csv')
        new_transaction_submit = st.form_submit_button('Uploaden')

    if new_transaction_submit:
        df_new_transaction = pd.read_csv(new_transaction_file, header=None)
        filter_new_transactions(df_new_transaction)

def filter_transactions():
    db = app_management.connect_main_deta()

    db_to_be_categorised = app_management.connect_to_be_categorised_deta()
    df_to_be_categorised = pd.DataFrame(db_to_be_categorised.fetch().items)

    db_category = app_management.connect_category_deta()
    df_category = pd.DataFrame(db_category.fetch().items)

    if not df_to_be_categorised.empty:
        with st.form('to_categorise', clear_on_submit=True):
            st.subheader('Nog te categoriseren')
            st.info(f'ℹ️ Nog {df_to_be_categorised.shape[0]} transactie om te categoriseren')
            col1, col2, col3 = st.columns([0.25, 0.25, 0.5])
            with col1:
                st.write('Rekening naam: ' + df_to_be_categorised.iloc[0, 0])
                st.write('Rekening Nummer: ' + df_to_be_categorised.iloc[0, 1])
            with col2:
                st.write('Bedrag: ' + str(df_to_be_categorised.iloc[0, 2]))
                st.write('Datum: ' + df_to_be_categorised.iloc[0, 3])

            st.write('Omschrijving: ' + df_to_be_categorised.iloc[0, 4])
            if df_to_be_categorised.iloc[0, 2] > 0:
                possible_categories = df_category[(df_category['type'] == 'Inkomen') | (df_category['type'] == 'Sparen')]['name']
            else:
                possible_categories = df_category[(df_category['type'] == 'Uitgaven') | (df_category['type'] == 'Sparen')]['name']
            category = st.selectbox('Kies een categorie', options=possible_categories, index=6)

            col1, col2, col3 = st.columns([0.1, 0.75, 0.15])
            with col1:
                to_be_categorised_submit = st.form_submit_button('Indienen')
            with col3:
                delete_submit = st.form_submit_button('Verwijder Transactie')
        if delete_submit:
            db_to_be_categorised.delete(df_to_be_categorised.iloc[0, 5])
            st.rerun()
        if to_be_categorised_submit:
            db.put({'amount':df_to_be_categorised.iloc[0, 2],
                    'category':category,
                    'date':df_to_be_categorised.iloc[0, 3],
                    'type':df_category[df_category['name'] == category]['type'].tolist()[0]})
            db_to_be_categorised.delete(df_to_be_categorised.iloc[0, 5])
            st.rerun()
    else:
        with st.container(border=True):
            st.subheader('Nog te categoriseren')
            st.success('✅ Je hebt geen transacties om te categoriseren')

def show_transactions():    
    db = app_management.connect_main_deta()
    df_transactions = pd.DataFrame(db.fetch().items)
    if not df_transactions.empty:
        df_transactions = df_transactions.rename(columns={'amount':"Bedrag", 'category':'Categorie', 'type':'Type'})
        df_transactions['Datum'] = pd.to_datetime(df_transactions['date'])
        df_transactions['date'] = pd.to_datetime(df_transactions['date'])
        df_transactions = df_transactions.sort_values(by='date', ascending=False)
        df_transactions['Datum'] = df_transactions['Datum'].dt.strftime('%d %m %Y')
        with st.container(border=True):
            st.subheader('Alle recente transacties')
            st.dataframe(df_transactions.sort_values('date', ascending=False).loc[:, ["Bedrag",'Categorie','Datum', 'Type']], use_container_width=True, hide_index=True)
    else:
        with st.container(border=True):
            st.subheader('Alle recente transacties')
            st.warning('Upload een eerste bankafschrift')

def metrics():
    db = app_management.connect_main_deta()
    df_transactions = pd.DataFrame(db.fetch().items)

    if not df_transactions.empty:
        df_transactions['date'] = pd.to_datetime(df_transactions['date'], dayfirst=True)
        df_transactions_current_month = df_transactions[(df_transactions['date'].dt.strftime('%Y-%m') == datetime.now().strftime('%Y-%m'))]
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Uitgaven deze maand',df_transactions_current_month.loc[df_transactions_current_month['type'] == 'Uitgaven', 'amount'].abs().sum().round(2))
            with col2:
                st.metric('Inkomen deze maand',df_transactions_current_month.loc[df_transactions_current_month['type'] == 'Inkomen', 'amount'].sum().round(2))
            with col3:
                st.metric('Gespaard deze maand',df_transactions_current_month.loc[df_transactions_current_month['type'] == 'Sparen', 'amount'].sum().round(2) * -1)

def main():
    # Start by logging in with the password
    if not app_management.check_password():
        st.stop()

    st.title('Financieel Overzicht')

    db = app_management.connect_main_deta()
    db_filter = app_management.connect_filter_deta()
    db_to_be_categorised = app_management.connect_filter_deta()

    add_new_transactions(db_to_be_categorised)
    metrics()
    filter_transactions()
    show_transactions()

if __name__ == '__main__':
    main()