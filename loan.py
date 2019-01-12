import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
pd.options.display.width = 1000

loan36 = pd.read_csv('loan36.csv')
loan36.head()
print('load {} 36-month loans from loan36.csv'.format(len(loan36)))

print('loan status:{}'.format(loan36['loan_status_description'].unique()))
loan36['loan_status_description'].value_counts()
sns.countplot(x='loan_status_description', data=loan36, palette='hls')

loan36['prosper_rating'].value_counts()
sns.countplot(x='prosper_rating', data=loan36, palette='hls')

#start to clean/normalize data
#1. Remove CURRENT and CANCELLED loans
working_data = pd.DataFrame(loan36[(loan36['loan_status_description'] !='CURRENT') & (loan36['loan_status_description'] !='CANCELLED')])
print("Removed 'CURRENT' and 'CANCELLED' loans from {} loans. {} loans left".format(len(loan36), len(working_data)))
print('loan status:{}'.format(working_data['loan_status_description'].unique()))

#2. Make CHARGEOFF as DEFAULTED
working_data['status'] = working_data.apply(lambda row: 'COMPLETED' if row.loan_status_description =='COMPLETED' else 'DEFAULTED', axis=1)
working_data[working_data['loan_status_description'] != 'COMPLETED'].head()


#stats based on prosper_rating
stats = working_data.groupby(['prosper_rating', 'status']).size()
stats = pd.DataFrame(stats, columns=['count'])
stats = stats.reset_index()
stats

rating_stats = working_data.groupby(['prosper_rating']).borrower_rate.agg(['size', 'min', 'max', 'mean', 'median'])
rating_stats = rating_stats.reset_index()
rating_stats = rating_stats.rename(columns={'size':'count', 'min':'min_rate', 'max':'max_rate', 'mean':'mean_rate', 'median':'median_rate'})

rating_stats['num_completed'] = rating_stats.apply(lambda row : stats.loc[(stats['prosper_rating'] == row['prosper_rating']) & (stats['status']=='COMPLETED')].iloc[0]['count'], axis=1)
rating_stats['num_defaulted'] = rating_stats.apply(lambda row : stats.loc[(stats['prosper_rating'] == row['prosper_rating']) & (stats['status']=='DEFAULTED')].iloc[0]['count'], axis=1)
rating_stats['completion_rate'] = rating_stats.apply(lambda row : row['num_completed']/row['count'], axis=1)
rating_stats['default_rate'] = rating_stats.apply(lambda row : row['num_defaulted']/row['count'], axis=1)

rating_stats['expected_return'] = rating_stats.apply(lambda row : row['mean_rate']*row['completion_rate'], axis=1)
rating_stats

expected_return = rating_stats['expected_return'].sum()/len(rating_stats)
print('Expected Return for an equlally allocated portfolio: {}'.format(expected_return))

ratings = working_data['prosper_rating'].unique()
ratings
#for rating in ratings:
rating = 'C'
print(rating)
data = working_data[working_data['prosper_rating']==rating]
#https://stackoverflow.com/questions/38250710/how-to-split-data-into-3-sets-train-validation-and-test
#60%, 20% 20% for traing, test and validation
train, validation, test = np.split(data.sample(frac=1), [int(.6*len(data)), int(.8*len(data))])
print("total:{} traing:{} test:{} validation:{}".format(len(data), len(train), len(validation), len(test)))
mod = smf.glm('status ~ borrower_rate', data=train, family=sm.families.Binomial()).fit()
mod.summary()
pre = mod.predict(test)
test['pred'] = test.apply(lambda row : pre.loc[row.name], axis=1)
test['pred_status'] = test.apply(lambda row : 'COMPLETED' if pre.loc[row.name] > 0.5 else 'DEFAULTED', axis=1)
pred_correct_rate = len(test[test['pred_status'] == test['status']])/len(test[test['pred_status'] == 'COMPLETED'])
actu_correct_rate = len(test[test['status'] == 'COMPLETED'])/len(test)

print('Rating:{} acturail correct rate:{} predict correct rate:{}'.format(rating, ))








































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

# select * from listing a, loan b where a.loan_origination_date=b.origination_date limit 10;
# and a.amount_funded=b.amount_borrowed and a.borrower_rate=b.borrower_rate and a.prosper_rating=b.prosper_rating and a.listing_term = b.term limit 10;




def query(sql):
	return pd.read_sql(sql, conn)


def import_listing(file_name):
	tmp_table = 'tmp_table'
	i = 1
	conn = sqlite3.connect("prosper.db")
	for chunk in pd.read_csv(file_name, low_memory=False, chunksize=1000):
		print(str(i) + ':' + str(len(chunk)))

		chunk.to_sql(tmp_table , conn)
		conn.execute('insert into listing select * from ' + tmp_table)
		conn.execute("drop table " + tmp_table)

		i = i + 1

	conn.close()
