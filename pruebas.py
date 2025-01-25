from tracker import Tracker

t = Tracker()
t.add_transaction('salary', 1000, '2020-01-01', 'income', store=True)
t.add_transaction('rent', -500, '2020-01-01', 'housing', store=True)
t.add_transaction('salary', 1000, '2020-02-01', 'income', store=True)
t.add_transaction('rent', -500, '2020-02-01', 'housing', store=True)
t.add_transaction('Electricity', -50, '2020-02-01', 'utilities', store=False)
t.save_tracker('test.csv')

t = Tracker()
t.load_tracker('test.csv')
print(t.concept_to_category)
print(t.df)

print(t.get_monthly_expenses(2, 2020))

