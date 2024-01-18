import streamlit as st
import app_management
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(layout="wide")

def metrics(time_duration):
    db = app_management.connect_main_deta()
    df_transactions = pd.DataFrame(db.fetch().items)

    if not df_transactions.empty:
        df_transactions['date'] = pd.to_datetime(df_transactions['date'],dayfirst=True)
        
        if time_duration == 'Maand':
            df_transactions_current_month = df_transactions[(df_transactions['date'].dt.strftime('%Y-%m') == datetime.now().strftime('%Y-%m'))]
        elif time_duration == 'Week':
            df_transactions_current_month = df_transactions[(df_transactions['date'].dt.strftime('%Y-%U') == datetime.now().strftime('%Y-%U'))]
        else:
            df_transactions_current_month = df_transactions[(df_transactions['date'].dt.strftime('%Y') == datetime.now().strftime('%Y'))]

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Uitgaven',df_transactions_current_month.loc[df_transactions_current_month['type'] == 'Uitgaven', 'amount'].abs().sum().round(2))
            with col2:
                st.metric('Inkomen',df_transactions_current_month.loc[df_transactions_current_month['type'] == 'Inkomen', 'amount'].sum().round(2))
            with col3:
                st.metric('Gespaard',df_transactions_current_month.loc[df_transactions_current_month['type'] == 'Sparen', 'amount'].sum().round(2) * -1)

def graphs(time_duration, netto_savings):
    db = app_management.connect_main_deta()
    df_transactions = pd.DataFrame(db.fetch().items)

    db_category = app_management.connect_category_deta()
    df_categories = pd.DataFrame(db_category.fetch().items)

    time_duration_map = {'Jaar':'Y', 'Maand':'M', 'Week': 'W'}

    if df_transactions.empty:
        st.warning('No transactions')
        return 
    
    df_transactions['date'] = pd.to_datetime(df_transactions['date'],dayfirst=True)

    # Expenses
    df_expenses_grouped = df_transactions[df_transactions['type'] == 'Uitgaven'].groupby([pd.Grouper(key='date', freq=time_duration_map[time_duration]), 'category']).sum(numeric_only=True).abs().reset_index()
    fig_stacked_bar_expenses = px.bar(df_expenses_grouped, x='date', y='amount', color='category', title='Uitgaven per categorie per maand')

    fig_stacked_bar_expenses.update_xaxes(title_text='Maand', type='category', tickmode='array', tickvals=df_expenses_grouped['date'], ticktext=df_expenses_grouped['date'].dt.strftime('%Y-%b'))
    fig_stacked_bar_expenses.update_yaxes(title_text='Bedrag')

    # Income
    df_income_grouped = df_transactions[df_transactions['type'] == 'Inkomen'].groupby([pd.Grouper(key='date', freq=time_duration_map[time_duration]), 'category']).sum(numeric_only=True).reset_index()
    fig_stacked_bar_income = px.bar(df_income_grouped, x='date', y='amount', color='category', title='Inkomen per categorie per maand', category_orders={'date': df_income_grouped['date'].tolist()})

    fig_stacked_bar_income.update_xaxes(title_text='Maand', type='category', tickmode='array', tickvals=df_income_grouped['date'], ticktext=df_income_grouped['date'].dt.strftime('%Y-%b'))
    fig_stacked_bar_income.update_yaxes(title_text='Bedrag')

    # Savings
    if not netto_savings:
        df_savings_grouped = df_transactions[df_transactions['type'] == 'Sparen'].groupby([pd.Grouper(key='date', freq=time_duration_map[time_duration]), 'category']).sum(numeric_only=True).reset_index()
        df_savings_grouped['amount'] *= -1
        fig_stacked_bar_savings = px.bar(df_savings_grouped, x='date', y='amount', color='category', title='Gespaard per categorie per maand', category_orders={'date': df_savings_grouped['date'].tolist()})

        fig_stacked_bar_savings.update_xaxes(title_text='Maand', type='category', tickmode='array', tickvals=df_savings_grouped['date'], ticktext=df_savings_grouped['date'].dt.strftime('%Y-%b'))
        fig_stacked_bar_savings.update_yaxes(title_text='Bedrag')
    else:
        df_savings_grouped = df_transactions[df_transactions['type'] == 'Sparen'].groupby([pd.Grouper(key='date', freq=time_duration_map[time_duration])]).sum(numeric_only=True).reset_index()
        df_savings_grouped['amount'] *= -1
        fig_stacked_bar_savings = px.bar(df_savings_grouped, x='date', y='amount', title='Gespaard per categorie per maand', category_orders={'date': df_savings_grouped['date'].tolist()})

        fig_stacked_bar_savings.update_xaxes(title_text='Maand', type='category', tickmode='array', tickvals=df_savings_grouped['date'], ticktext=df_savings_grouped['date'].dt.strftime('%Y-%b'))
        fig_stacked_bar_savings.update_yaxes(title_text='Bedrag')


    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(fig_stacked_bar_expenses, use_container_width=True)
    with col2:
        st.plotly_chart(fig_stacked_bar_income, use_container_width=True)
    with col3:
        st.plotly_chart(fig_stacked_bar_savings, use_container_width=True)

    col1, col2 = st.columns([2/3, 1/3])

    with col1:
        selected_categories = st.multiselect('Kies de categorieën', options=df_categories['name'], default=df_categories['name'][6])
        df_expenses_selected = df_transactions[df_transactions['category'].isin(selected_categories)]
        df_expenses_grouped_selected = df_expenses_selected[df_expenses_selected['type'] == 'Uitgaven'].groupby([pd.Grouper(key='date', freq=time_duration_map[time_duration]), 'category']).sum(numeric_only=True).abs().reset_index()
        fig_stacked_bar_expenses_selected = px.bar(df_expenses_grouped_selected, x='date', y='amount', color='category', title='Uitgaven per categorie per maand')

        fig_stacked_bar_expenses_selected.update_xaxes(title_text='Maand', type='category', tickmode='array', tickvals=df_expenses_grouped_selected['date'], ticktext=df_expenses_grouped_selected['date'].dt.strftime('%Y-%b'))
        fig_stacked_bar_expenses_selected.update_yaxes(title_text='Bedrag')

        st.plotly_chart(fig_stacked_bar_expenses_selected, use_container_width=True)





def main():
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            time_duration = st.radio('Kies een tijdsdimensie', options=['Jaar', 'Maand', 'Week'], index=1, horizontal=True)
        with col2:
            st.write('Netto gespaard')
            netto_savings = st.toggle('Netto sparen', )
    metrics(time_duration)
    with st.container(border=True):
        st.subheader('Grafieken')
        graphs(time_duration, netto_savings)

if __name__ == '__main__':
    main()