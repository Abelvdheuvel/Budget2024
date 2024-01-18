import streamlit as st
import app_management
import pandas as pd

st.set_page_config(layout="wide")

def old_transactions():
    db_category = app_management.connect_category_deta()
    df_category = pd.DataFrame(db_category.fetch().items)

    db = app_management.connect_main_deta()

    helper_bool = False
     
    with st.form('old_transactions'):
        old_file = st.file_uploader('Oude Transacties', 'csv')
        old_transactions_submitted = st.form_submit_button('Uploaden')

    if old_file:
        with st.form('old_cat', border=True):

            df_old_transactions = pd.read_csv(old_file)

            df_old_categories = pd.DataFrame(df_old_transactions['category'].unique(), columns=['old'])
            

            for category in df_old_categories['old']:
                old_new_translation = df_category.loc[df_category['name'].str.contains(category, na=False), 'name']
                old_new_translation_type = df_category.loc[df_category['name'].str.contains(category, na=False), 'type']
                if not old_new_translation.empty:
                    df_old_categories.loc[df_old_categories['old'] == category, 'new'] = old_new_translation.tolist()[0]
                    df_old_categories.loc[df_old_categories['old'] == category, 'type'] = old_new_translation_type.tolist()[0]

                col1, col2 = st.columns(2)
                with col1:
                    st.write(category)
                with col2:
                    if df_old_categories.loc[df_old_categories['old'] == category, 'new'].notna().any():
                        index = int(df_category[df_category['name'] == df_old_categories[df_old_categories['old'] == category]['new'].tolist()[0]].index[0])
                        chosen_category = st.selectbox('Kies een categorie', key=category + '_new_category_select', options=df_category['name'], index=index)
                        df_old_categories.loc[df_old_categories['old'] == category, 'new'] = chosen_category
                    else:
                        chosen_category = st.selectbox('Kies een categorie', key=category + '_new_category_select', options=df_category['name'], index=1)
                        df_old_categories.loc[df_old_categories['old'] == category, 'new'] = chosen_category
                        df_old_categories.loc[df_old_categories['old'] == category, 'type'] = df_category[df_category['name'] == chosen_category]['type'].tolist()[0]

                st.divider()
            submit = st.form_submit_button('Indienen')
        if submit:
            df_old_transactions_translated = pd.merge(df_old_transactions, df_old_categories, how='inner', left_on='category', right_on='old').drop(['category', 'old'], axis=1).rename(columns={'new':'category'})
            
            progressbar = st.progress(0, 'Transacties worden opgeslagen')
            transactions = df_old_transactions_translated.to_dict(orient='records')
            
            for i, record in enumerate(transactions):
                db.put(record)
                progressbar.progress(i / len(transactions), 'Transacties worden opgeslagen')

def main():
    st.title('Categorieën en Filters')

    # Start by logging in with the password
    if not app_management.check_password():
        st.stop()

    # Categories
    col1, col2 = st.columns([2/3, 1/3])

    db_category = app_management.connect_category_deta()

    with col1:
        with st.container(border=True):
            st.subheader('Huidige categorieën')
            db_category_content = db_category.fetch().items
            if db_category_content:
                df_category = pd.DataFrame(db_category.fetch().items)
                col11, col12, col13 = st.columns(3)
                
                with col11:
                    st.markdown(f'**Uitgaven**')
                    for category in df_category[df_category['type'] == 'Uitgaven']['name'].sort_values(key=lambda x: x.apply(app_management.get_first_letter)):
                        st.write(category)

                with col12:
                    st.markdown('**Inkomen**')
                    for category in df_category[df_category['type'] == 'Inkomen']['name']:
                        st.write(category)

                with col13:
                    st.markdown('**Sparen**')
                    for category in df_category[df_category['type'] == 'Sparen']['name']:
                        st.write(category)
            else:
                st.warning('⚠️ Er zijn nog geen categorieën ingesteld ⚠️')
    with col2:
        with st.form('category_form', clear_on_submit=True):
            st.subheader('Voeg categorieën toe')

            categoryname = st.text_input('Naam category')
            categorytype = st.radio('Type categorie', options=['Uitgaven', 'Inkomen', 'Sparen'])
    
            new_category_submit = st.form_submit_button('Indienen')
        if new_category_submit:
            db_category.put({'name':categoryname, 'type':categorytype})

            st.rerun()
        

    # Filters
    col1, col2 = st.columns([2/3, 1/3])

    db_filter = app_management.connect_filter_deta()

    with col1:
        with st.container(border=True):
            st.subheader('Huidige Filters')
            db_filter_content = db_filter.fetch().items
            if db_filter_content:
                df_filter = pd.DataFrame(db_filter.fetch().items)
                st.dataframe(df_filter.loc[:, ['name', 'filter', 'category', 'category type']].sort_values('name').rename(columns={'name':'Naam', 'filter':'Filter', 'category':'Categorie', 'category type':'Categorie Type'}), hide_index=True)
            else:
                st.warning('⚠️ Er zijn nog geen filters ingesteld ⚠️')
    with col2:
        if db_category_content:
            df_category = pd.DataFrame(db_category.fetch().items)
            with st.form('filter_form', clear_on_submit=True):
                st.subheader('Voeg filters toe')

                filtername = st.text_input('Naam filter')
                filterstring = st.text_input('Filter')
                filtertype = st.radio('Filter type', options=['Beschrijving','Rekeningnummer'])
                filtercategory = st.selectbox('Categorie', options=df_category['name'])

                new_filter_submit = st.form_submit_button('Indienen')
            if new_filter_submit:
                filtertype_encoded = 0 if filtertype == 'Rekeningnummer' else 1
                filtercategorytype = df_category[df_category['name'] == filtercategory]['type'].iloc[0]

                db_filter.put({'name':filtername, 'filter':filterstring, 'category':filtercategory, 'category type':filtercategorytype, 'type':filtertype_encoded})
                st.rerun()

        else:
            st.warning('⚠️ Je moet eerst categorieën instellen')

    old_transactions()

if __name__ == '__main__':
    main()