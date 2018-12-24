import sqlite3
import pandas as pd

pd.options.display.width = 1000

conn = sqlite3.connect("loan.db")
sql_summary = (
	'select prosper_rating as rating, count(*) as total_count,'
	" min(amount_borrowed*1.0) as min_amount, max(amount_borrowed*1.0) as max_amount, avg(amount_borrowed*1.0) as avg_amount, sum(amount_borrowed) as total_amount,"
	" min(borrower_rate*1.0) as min_rate, max(borrower_rate*1.0) as max_rate, avg(borrower_rate*1.0) as avg_rate"
	" from loan"
	" where loan_status_description <> 'CANCELLED' AND prosper_rating <> 'N/A' group by prosper_rating"
	)

sql_summary_2 = (
	"select prosper_rating as rating, loan_status_description as status_desc, loan_status as status,  count(*) as total_count,"
	" min(amount_borrowed*1.0) as min_amount, max(amount_borrowed*1.0) as max_amount, avg(amount_borrowed*1.0) as avg_amount, sum(amount_borrowed) as total_amount,"
	" min(borrower_rate*1.0) as min_rate, max(borrower_rate*1.0) as max_rate, avg(borrower_rate*1.0) as avg_rate"
	" from loan"
	" where loan_status_description <> 'CANCELLED' AND prosper_rating <> 'N/A' group by prosper_rating, loan_status_description, loan_status"
	)

sql_summary_3 = "select a.*, b.total_count from (" + sql_summary_2 + ") a JOIN (" + sql_summary + ") b ON a.rating = b.rating"