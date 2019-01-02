# A classfication example using Python
#https://www.quantinsti.com/blog/machine-learning-classification-strategy-python?utm_campaign=News&utm_medium=Community&utm_source=DataCamp.com

# machine learning classification
from sklearn.svm import SVC
from sklearn.metrics import scorer
from sklearn.metrics import accuracy_score
# For data manipulation
import pandas as pd
import numpy as np
# To plot
import matplotlib.pyplot as plt
import seaborn
# To fetch data
from pandas_datareader import data as pdr


#Df = pdr.get_data_google('SPY', start="2012-01-01", end="2017-10-01")
df = pd.read_csv('SPY.csv')
df = df.dropna()
df.Close.plot(figsize=(10,5))
plt.ylabel("S&P500 Price")
plt.show()