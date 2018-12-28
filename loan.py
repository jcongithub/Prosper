import sqlite3
import pandas as pd

pd.options.display.width = 1000

conn = sqlite3.connect("prosper.db")

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

sql4 = '''
with hr as (
	select loan_number, amount_borrowed as amount, cast(amount_borrowed/1000 as int) *1000 as amount_range, borrower_rate as rate,origination_date as start_date, borrower_rate as rate, loan_status_description as status 
	from loan where term=36 and age_in_months*1.0>42 and prosper_rating = 'HR'
)
select a.amount_range, b.status, b.count, b.count*1.0/a.total_count as status_rate, a.total_count from (
	select amount_range, count(*) as total_count 
	from hr group by amount_range
) a
left join (
	select amount_range, status, count(*) as count 
	from hr group by amount_range, status
) b ON a.amount_range = b.amount_range
'''

sql5 = '''
with hr as (
	select loan_number, amount_borrowed as amount, cast(borrower_rate*100 as int) rate_rage, borrower_rate as rate, origination_date as start_date, loan_status_description as status 
	from loan where term=36 and age_in_months*1.0>42 and prosper_rating = 'HR'
)
select a.rate_rage, b.status, b.count, b.count*1.0/a.total_count as status_rate, a.total_count from (
	select rate_rage, count(*) as total_count 
	from hr group by rate_rage
) a
left join (
	select rate_rage, status, count(*) as count 
	from hr group by rate_rage, status
) b ON a.rate_rage = b.rate_rage
'''

def query(sql):
	return pd.read_sql(sql, conn)


def import_listing(file_name):
	tmp_table = 'tmp_table'
	i = 1
	conn = sqlite3.connect("loan.db")
	for chunk in pd.read_csv(file_name, low_memory=False, chunksize=1000):
		print(str(i) + ':' + str(len(chunk)))
		
		chunk.to_sql(tmp_table , conn)
		conn.execute("drop table " + tmp_table)

		i = i + 1
	
	conn.close()
