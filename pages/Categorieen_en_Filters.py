import streamlit as st
import app_management
import pandas as pd

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
                filtertype = st.radio('Filter type', options=['Beschrijving','Rekeningnaam'])
                filtercategory = st.selectbox('Categorie', options=df_category['name'])

                new_filter_submit = st.form_submit_button('Indienen')
            if new_filter_submit:
                filtertype_encoded = 0 if filtertype == 'Rekeningnaam' else 1
                filtercategorytype = df_category[df_category['name'] == filtercategory]['type'].iloc[0]

                db_filter.put({'name':filtername, 'filter':filterstring, 'category':filtercategory, 'category type':filtercategorytype, 'type':filtertype_encoded})
                st.rerun()

        else:
            st.warning('⚠️ Je moet eerst categorieën instellen')

if __name__ == '__main__':
    main()