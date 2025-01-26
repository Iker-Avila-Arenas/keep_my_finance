import pandas as pd
import numpy as np
import datetime as dt
import os

class Tracker():
    def __init__(self):
        """
        Initialize the tracker with an empty dataframe and an empty dictionary
        the dataframe has the following columns:
        - Concept: the name of the concept (String)
        - Value: the value of the transaction (Float)
        - Date: the date of the transaction (Datetime)
        - Category: the category of the transaction (String)
        - Subcategory: the subcategory of the transaction (String)
        - Store: a boolean indicating if the concept needs to be stored (Boolean)

        the dictionary concept_to_category has the following structure:
        - key: the name of the concept (String)
        - value: the category of the concept (String)
        """
        self.df = pd.DataFrame(columns=['Concept', 'Value', 'Date', 'Category', 'Subcategory', 'Store'])
        self.concept_to_category = dict()

    def update_concept_to_category(self):
        """
        iterate the dataframe to add those concepts with Store==True to the concept_to_category dictionary
        """
        for index, row in self.df.iterrows():
            if row['Store'] and row['Concept'] not in self.concept_to_category:
                self.concept_to_category[row['Concept']] = row['Category']

    def save_tracker(self, path):
        self.df.to_csv(path, index=False)

    def load_tracker(self, path):
        self.df = pd.read_csv(path)
        # Ensure the Date column is converted to datetime objects
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.update_concept_to_category()

    def add_transaction(self, concept, value, date, category, subcategory=None, store=False):
        """
        Add a transaction to the dataframe
        """
        # Ensure the date is a datetime object
        date = pd.to_datetime(date)
        new_row = pd.DataFrame([[concept, value, date, category, subcategory, store]], 
                               columns=['Concept', 'Value', 'Date', 'Category', 'Subcategory', 'Store'])
        if self.df.empty:
            self.df = new_row
        else:
            self.df = pd.concat([self.df, new_row], ignore_index=True)
        if store and concept not in self.concept_to_category:
            self.concept_to_category[concept] = category

    def filter_by_dates(self, start_date, end_date):
        # Ensure Date column is datetime before filtering
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        filtered = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)]
        filtered_tracker = Tracker()
        filtered_tracker.df = filtered
        filtered_tracker.update_concept_to_category()
        return filtered_tracker
    
    def get_category_expenses(self):
        """
        Get the total expenses per category
        """
        category_expenses = self.df.groupby('Category')['Value'].sum()
        return category_expenses

    def get_monthly_transactions(self, month, year):
        # Ensure Date column is datetime before filtering
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        month = self.df[(self.df['Date'].dt.month == month) & (self.df['Date'].dt.year == year)]
        month = month.sort_values('Date')
        return month

    def monthly_summary(self, month, year):
        """
        Return a summary of the monthly expenses
        """
        monthly_expenses = self.get_monthly_transactions(month, year)
        # calculate cumulative per day
        cumulative = monthly_expenses['Value'].cumsum()
        total = monthly_expenses['Value'].sum()
        max_state = cumulative.max()
        min_state = cumulative.min()

        return total, max_state, min_state
    
    def get_daily_transactions(self, date):
        # Ensure Date column is datetime before filtering
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        day = self.df[self.df['Date'] == date]
        day = day.sort_values('Date')
        return day
    
    def daily_summary(self, date):
        """
        Return a summary of the daily expenses
        """
        daily_expenses = self.get_daily_transactions(date)
        # calculate cumulative per day
        cumulative = daily_expenses['Value'].cumsum()
        total = daily_expenses['Value'].sum()
        max_state = cumulative.max()
        min_state = cumulative.min()

        return total, max_state, min_state
