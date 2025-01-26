from tracker import Tracker
import plotly.express as px
import plotly.graph_objects as go
from global_variables import Global_variables

import pandas as pd
import plotly.express as px

globals = Global_variables()

def expenses_per_category(tracker):
    """
    Create a bar chart of the expenses per category.
    In red the expenses, in green the earnings, and in blue the savings/investments.
    """
    # Get and sort category expenses
    category_expenses = tracker.get_category_expenses()
    category_expenses = category_expenses.sort_values(by='Value', ascending=True)
    category_expenses['Positive_Total'] = category_expenses['Value'].abs()

    # Custom sorting by category and value
    def custom_sort(value, category):
        if value > 0:
            return 0
        elif value < 0 and category not in globals.invests:
            return 1
        else:
            return 2
        
    category_expenses['Sort'] = category_expenses.apply(
        lambda row: custom_sort(row['Value'], row['Category']),
        axis=1
    )
    category_expenses = category_expenses.sort_values(by='Sort', ascending=True)

    # Function to determine the color for each bar
    def color_selector(value, category):
        if value < 0 and category in globals.invests:  # Corrected from '&' to 'and' and typo in 'Investment'
            return globals.green  # Green for savings/investments
        elif value > 0:
            return globals.blue  # Blue for earnings
        else:
            return globals.red  # Red for expenses

    # Add a Color column to the DataFrame
    category_expenses['Color'] = category_expenses.apply(
        lambda row: color_selector(row['Value'], row['Category']),
        axis=1
    )

    # Create the bar chart
    fig_category = px.bar(
        category_expenses,
        x='Category',
        y='Positive_Total',
        title='Expenses per Category',
        labels={'Category': 'Category', 'Value': 'Amount (€)'}
    )

    fig_category.update_traces(hovertemplate='%{x}: %{y:.2f}€<extra></extra>')

    # Apply the color mapping
    fig_category.update_traces(marker_color=category_expenses['Color'])
    fig_category.update_layout(
        barmode='group',
        showlegend=False,
        bargap=0,
        bargroupgap=0.1,
        title_x=0.5
    )
    fig_category.update_yaxes(title='')
    fig_category.update_xaxes(title='')

    return fig_category

def expenses_pie_chart(tracker, show_investments=False, show_earnings=False):
    """
    Create a pie chart of the expenses per category.
    """
    # Remove the 'Investment' category from the pie chart and the earnings
    category_expenses = tracker.get_category_expenses()
    if not show_investments:
        category_expenses = category_expenses[~category_expenses['Category'].isin(globals.invests)]
    if not show_earnings:
        category_expenses = category_expenses[category_expenses['Value'] < 0]
    category_expenses['Positive_Total'] = category_expenses['Value'].abs()

    # Create the pie chart
    fig_pie = px.pie(
        category_expenses,
        values='Positive_Total',
        names='Category',
        title='Expenses per Category',
        labels={'Category': 'Category', 'Positive_Total': 'Amount (€)'}
    )

    return fig_pie
    

def candlestick_per_month(tracker):
    """
    Create a candlestick chart of the expenses per month.
    """
    # get unique manth/years from the dataframe
    month_years = tracker.df['Date'].dt.to_period('M').unique()
    df_candlestick = pd.DataFrame(columns=['Month', 'Year', 'Total', 'Max', 'Min', 'Start', 'End'])
    start = 0
    for m in month_years:
        month = m.month
        year = m.year
        total, max_state, min_state, end = tracker.monthly_summary(month, year, start)
        new_row = pd.DataFrame([[month, year, total, max_state, min_state, start, end]],    
                               columns=['Month', 'Year', 'Total', 'Max', 'Min', 'Start', 'End'])
        if df_candlestick.empty:
            df_candlestick = new_row
        else:
            df_candlestick = pd.concat([df_candlestick, new_row], ignore_index=True)
        start = end

    print(df_candlestick)
    
    # Create the candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=df_candlestick['Month'].astype(str) + '/' + df_candlestick['Year'].astype(str),
                                         open=df_candlestick['Start'],
                                         high=df_candlestick['Max'],
                                         low=df_candlestick['Min'],
                                         close=df_candlestick['End'])])
    # get rid of slider
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_layout(title='Expenses per Month')
    fig.update_yaxes(title='Amount (€)')
    fig.update_xaxes(title='Month/Year')

    # adjust scale
    fig.update_yaxes(range=[df_candlestick['Min'].min()-100, df_candlestick['Max'].max() + 100])

    # adjust colors
    fig.update_traces(
        increasing_line_color=globals.green,
        decreasing_line_color=globals.red,
        increasing_fillcolor=globals.green,
        decreasing_fillcolor=globals.red)

            
    return fig

def summary_plot(tracker):
    """
    Bar plot with three columns: spendings, earnings, and savings/investments.
    """
    df = tracker.df
    # Function to determine the color for each bar
    def color_selector(value, category):
        if value < 0 and category in globals.invests:  # Corrected from '&' to 'and' and typo in 'Investment'
            return globals.green  # Green for savings/investments
        elif value > 0:
            return globals.blue  # Blue for earnings
        else:
            return globals.red # Red for expenses
    # Add a Color column to the DataFrame
    df['Color'] = df.apply(
        lambda row: color_selector(row['Value'], row['Category']),
        axis=1
    )
        
    # Get the total earnings, expenses, and investments
    earnings = df[df['Color'] == globals.blue]['Value'].sum()
    expenses = abs(df[df['Color'] == globals.red]['Value'].sum())
    investments = abs(df[df['Color'] == globals.green]['Value'].sum())

    data = {'Type': ['Earnings', 'Expenses', 'Investments'],
            'Amount': [earnings, expenses, investments]}
    df_summary = pd.DataFrame(data)

    # Create the bar chart
    fig_summary = px.bar(
        df_summary,
        x='Type',
        y='Amount',
        title='Summary',
        labels={'Type': 'Type', 'Amount': 'Amount (€)'}
    )

    fig_summary.update_traces(marker_color=[globals.blue, globals.red, globals.green])

    return fig_summary