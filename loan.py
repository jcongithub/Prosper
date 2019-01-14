import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import confusion_matrix, classification_report

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
pd.options.display.width = 1000


loan36 = pd.read_csv('loan36.csv')
print('load {} 36-month loans from loan36.csv'.format(len(loan36)))
print('loan status:{}'.format(loan36['loan_status_description'].unique()))
loan36['loan_status_description'].value_counts()
sns.countplot(x='loan_status_description', data=loan36, palette='hls')

loan36['prosper_rating'].value_counts()
sns.countplot(x='prosper_rating', data=loan36, palette='hls')

def summary(data):
	print('Total Count:{}'.format(len(data)))
	print('Completed Count:{}'.format(len(data[data['status'] == 'COMPLETED'])))
	print('DEFAULTED Count:{}'.format(len(data[data['status'] == 'DEFAULTED'])))
	actual_completion_rate = len(data[data['status'] == 'COMPLETED'])/len(data)
	actual_default_rate = len(data[data['status'] == 'DEFAULTED'])/len(data)
	print('Actual completion rate:{}'.format(actual_completion_rate))
	print('Actual default rate:{}'.format(actual_completion_rate))
	amount=data['amount_funded'].sum()
	principal=data['principal_paid'].sum()
	interest=data['interest_paid'].sum()
	roi = (principal+interest-amount)/amount

	print('Total amount funded:{} principal paid:{} interest paid:{} ROI:{}'.format(amount, principal, interest, roi))
	stats = data.groupby(['prosper_rating']).borrower_rate.agg(['size','min', 'max', 'mean', 'median'])
	stats = stats.rename(columns={'size':'count', 'min':'min_rate', 'max':'max_rate', 'mean':'mean_rate', 'median':'median_rate'})
	counts = data.groupby(['prosper_rating', 'status']).size()
	stats['completed_count'] = stats.apply(lambda row : counts.loc[(row.name, 'COMPLETED')], axis=1)
	stats['defaulted_count'] = stats.apply(lambda row : counts.loc[(row.name, 'DEFAULTED')], axis=1)
	stats['completion_rate'] = stats.apply(lambda row : row['completed_count']/row['count'], axis=1)
	print(stats)

def loan_summary(data):
	summary(data)
	ratings = data['prosper_rating'].unique()
	ratings.sort()

	rate_completions = pd.DataFrame()
	for rating in ratings:
		print('Prosper Rating:{}'.format(rating))
		loans = data[data['prosper_rating']==rating]
		counts = loans.groupby(['rate_range']).size()
		completed_count = loans[loans['status']=='COMPLETED'].groupby(['rate_range']).size()
		defaulted_count = loans[loans['status']=='DEFAULTED'].groupby(['rate_range']).size()
		stats = pd.concat([counts, completed_count, defaulted_count], axis=1).rename(columns={0:'count', 1:'completed_count', 2:'defaulted_count'})
		stats['completion_rate'] = stats.apply(lambda row : row['completed_count']/row['count'], axis=1)
		stats['default_rate'] = stats.apply(lambda row : row['defaulted_count']/row['count'], axis=1)
		print(stats)

		s = stats[stats['count'] > 1000][['completion_rate']].rename(columns={'completion_rate':'completion_rate_' + rating})

		rate_completions = pd.concat([rate_completions, s], axis=1)

	print(rate_completions)
	#return stats
def clean_up_loan_data(data):
	data['principal_paid'] = data.apply(lambda row: float(row['principal_paid']), axis=1)
	data['interest_paid'] = data.apply(lambda row: float(row['interest_paid']), axis=1)


#start to clean/normalize data
#1. Remove CURRENT and CANCELLED loans
working_data = pd.DataFrame(loan36[(loan36['loan_status_description'] !='CURRENT') & (loan36['loan_status_description'] !='CANCELLED')])
#2. Make CHARGEOFF as DEFAULTED
working_data['status'] = working_data.apply(lambda row: 'COMPLETED' if row.loan_status_description =='COMPLETED' else 'DEFAULTED', axis=1)
#3. borrower_rate range
working_data['rate_range'] = working_data.apply(lambda row: int(row['borrower_rate']*100)/100, axis=1)

#4. Rename prosper_rating AA to '0' for easy sorting
working_data['prosper_rating'] = working_data.apply(lambda row: '0' if row.prosper_rating =='AA' else row.prosper_rating, axis=1)

loan_summary(working_data)


def pred(working, rating):
	data = working[working['prosper_rating']==rating]
	#https://stackoverflow.com/questions/38250710/how-to-split-data-into-3-sets-train-validation-and-test
	#60%, 20% 20% for traing, test and validation
	train, validation, test = np.split(data.sample(frac=1), [int(.6*len(data)), int(.8*len(data))])
	print("total:{} train:{} test:{} validation:{}".format(len(data), len(train), len(validation), len(test)))
	mod = smf.glm('status ~ borrower_rate', data=train, family=sm.families.Binomial()).fit()

	print(test_model(mod, test))

def test_model(mod, data):
	pre = mod.predict(test)
	result = pd.DataFrame()
	for i in np.arange(pre.min(), pre.max(), 0.01):
		cm = confusion_matrix(test["status"], ['COMPLETED' if x > i else 'DEFAULTED' for x in pre])
		result = result.append({'p':i, 'count':(cm[0][0] + cm[1][0]), 'accurace':(cm[0][0]/(cm[0][0] + cm[1][0]))}, ignore_index=True)

	return result


pred(working_data, '0')
pred(working_data, 'A')
pred(working_data, 'C')
pred(working_data, 'D')
pred(working_data, 'E')
pred(working_data, 'HR')

#a = mod.model.endog
#type(a)
#np.where(a == 0)
#train.iloc[np.where(a == 0)]['status']
#mod.model.endog

#listing_loan
conn = sqlite3.connect("prosper.db")
loan_listings = pd.read_sql('select * from listing_loan', conn)
np.where(loan_listings.columns.tolist() == 'status')

#clean data
loan_listings.loan_status_description.unique()
##1. Remove "CURRENT"
loan_listings = loan_listings[loan_listings['loan_status_description'] != 'CURRENT']
loan_listings.loan_status_description.unique()
loan_listings['status'] = loan_listings.apply(lambda row : 'DEFAULTED' if row['loan_status_description']=='CHARGEOFF' else row['loan_status_description'], axis=1)
loan_listings['status'].unique()
## 2. generate rate_range
loan_listings['rate_range'] = loan_listings.apply(lambda row: int(row['borrower_rate']*100)/100, axis=1)

clean_up_loan_data(loan_listings)

loan_listings.listing_term.unique()
loan_listings.fico_score.unique()
loan_listings.income_range_description.unique()
loan_listings.income_verifiable.unique()
loan_listings.employment_status_description.unique()
loan_listings.occupation.unique()

summary(loan_listings)
summary(loan_listings[loan_listings['prosper_rating']=='A'])
summary(loan_listings[loan_listings['prosper_rating']=='B'])

summary(loan_listings[loan_listings['prosper_rating']=='D'])
summary(loan_listings[loan_listings['prosper_rating']=='C'])

summary(loan_listings[loan_listings['prosper_rating']=='E'])

summary(loan_listings[loan_listings['prosper_rating']=='HR'])



train, validation, test = np.split(loan_listings.sample(frac=1), [int(.6*len(loan_listings)), int(.8*len(loan_listings))])
print("total:{} train:{} test:{} validation:{}".format(len(data), len(train), len(validation), len(test)))
mod1 = smf.glm('status ~ fico_score', data=train, family=sm.families.Binomial()).fit()
test_model(mod1, test)
mod2 = smf.glm('status ~ fico_score+income_range_description', data=train, family=sm.families.Binomial()).fit()
test_model(mod2, test)

mod3 = smf.glm('status ~ fico_score+income_range_description+income_verifiable', data=train, family=sm.families.Binomial()).fit()
mod3.summary()
test_model(mod3, test)

mod4 = smf.glm('status ~ fico_score+income_range_description+income_verifiable+employment_status_description', data=train, family=sm.families.Binomial()).fit()
mod4.summary()
test_model(mod4, test)

mod5 = smf.glm('status ~ fico_score+income_range_description+income_verifiable+employment_status_description+occupation', data=train, family=sm.families.Binomial()).fit()
mod5.summary()
test_model(mod5, test)

mod6 = smf.glm('status ~ fico_score+income_range_description+income_verifiable+employment_status_description+occupation+months_employed', data=train, family=sm.families.Binomial()).fit()
mod6.summary()
test_model(mod6, test)
pre = mod6.predict(test)
np.where(pre.isnull())
pre.iloc[2]
pre


res = pd.concat([test[['listing_number', 'loan_number', 'prosper_rating', 'borrower_rate', 'status']], pre], axis=1)
result = pd.DataFrame()
for i in np.arange(pre.min(), pre.max(), 0.01):
	res['pre_status'] = res.apply(lambda row : 'COMPLETED' if row[0] > i else 'DEFAULTED', axis=1)
	pre_complete_loans = res[res['pre_status']=='COMPLETED']
	pre_correct_loans = pre_complete_loans[pre_complete_loans['status']=='COMPLETED']

	aa_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'AA'])
	a_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'A'])
	b_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'B'])
	c_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'C'])
	d_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'D'])
	e_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'E'])
	hr_count = len(pre_complete_loans[pre_complete_loans['prosper_rating'] == 'HR'])

	cm = confusion_matrix(test["status"], ['COMPLETED' if x > i else 'DEFAULTED' for x in pre])

	result = result.append({'p':i,
							'count':(cm[0][0] + cm[1][0]),
							'accurace':(cm[0][0]/(cm[0][0] + cm[1][0])),
							'aa_count':aa_count,
							'aa':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='AA'])/aa_count if aa_count>0.0 else 'N/A',
							'a_count':a_count,
							'a':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='A'])/a_count if a_count>0.0 else 'N/A',
							'b_count':b_count,
							'b':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='B'])/b_count if b_count>0.0 else 'N/A',
							'c_count':c_count,
							'c':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='C'])/c_count if c_count>0.0 else 'N/A',
							'd_count':d_count,
							'd':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='D'])/d_count if d_count>0.0 else 'N/A',
							'e_count':e_count,
							'e':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='E'])/e_count if e_count>0.0 else 'N/A',
							'hr_count':hr_count,
							'hr':len(pre_correct_loans[pre_correct_loans['prosper_rating']=='HR'])/hr_count if hr_count>0.0 else 'N/A'},
							ignore_index=True)


result[['p', 'aa_count', 'aa', 'a_count','a', 'b_count','b', 'c_count','c','d_count','d','e_count','e','hr_count','hr','count', 'accurace']]

loan_summary(test)

len(test)
len(test[test['amount_funded']>0])
len(test[test['amount_funded']==test['amount_borrowed']])
test.amount_funded.sum()
test[test.status=='COMPLETED'].listing_monthly_payment.sum()*36
test['principal_paid_1']  = test.apply(lambda row : float(row['principal_paid']), axis=1)
test['principal_paid_1'].sum()
test['interest_paid_1'] = test.apply(lambda row : float(row['interest_paid']), axis=1)
test['interest_paid_1'].sum()
roi = test['principal_paid_1'].sum() + test['interest_paid_1'].sum() - test.amount_funded.sum()
roi
y = roi/test.amount_funded.sum()
y

loan_summary(test)





roi = test[test.status=='COMPLETED'].listing_monthly_payment.sum()*36 - test.amount_funded.sum()
roi

test[test.loan_status_description=='COMPLETED'].amount_funded.sum()

test.status.unique()




test['amount'] = test.apply(lambda row:row['amount_borrowed']*1.0, axis=1)
test.iloc[26460]['amount_funded']*1.0
test.iloc[26459]
['listing_monthly_payment']
*1.0

test[test.loan_status_description=='COMPLETED'].amount_borrowed
test[test.loan_status_description=='COMPLETED'].listing_monthly_payment


test[test.loan_status_description=='COMPLETED'].groupby(['prosper_rating']).agg({'amount_borrowed':['sum'], 'listing_monthly_payment':['sum']})













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
