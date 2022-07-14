import numpy as np
import datetime as dt 
import pandas as pd
from collections import Counter
import datetime as dt
from sqlalchemy import asc
from tensorflow.python.keras.models import Sequential, Model
from tensorflow.python.keras.layers import Dense, Dropout, Input, Conv2D, Flatten, LSTM
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MaxAbsScaler, RobustScaler
import time
import tensorflow as tf 
encording_columns = ['MSZoning','Street','Alley','LotShape','LandContour','Utilities','LotConfig',
                    'LandSlope','Neighborhood','Condition1','Condition2','BldgType','HouseStyle',
                    'RoofStyle','RoofMatl','Exterior1st','Exterior2nd','MasVnrType','ExterQual',
                    'ExterCond','Foundation','BsmtQual','BsmtCond','BsmtExposure','BsmtFinType1',
                    'BsmtFinType2','Heating','HeatingQC','CentralAir','Electrical','KitchenQual',
                    'Functional','FireplaceQu','GarageType','GarageFinish','GarageQual','GarageCond',
                    'PavedDrive','PoolQC','Fence','MiscFeature','SaleType','SaleCondition']

non_encording_columns = ['MSSubClass','LotFrontage','LotArea','OverallQual','OverallCond',
                         'YearBuilt','YearRemodAdd','MasVnrArea','BsmtFinSF1','BsmtFinSF2',
                         'BsmtUnfSF','TotalBsmtSF','1stFlrSF','2ndFlrSF','LowQualFinSF',
                         'GrLivArea','BsmtFullBath','BsmtHalfBath','FullBath','HalfBath','BedroomAbvGr',
                         'KitchenAbvGr','TotRmsAbvGrd','Fireplaces','GarageYrBlt','GarageCars','GarageArea',
                         'WoodDeckSF','OpenPorchSF','EnclosedPorch','3SsnPorch','ScreenPorch','PoolArea',
                         'MiscVal','MoSold','YrSold']

#1. 데이터
path = './_data/house/'
train_set = pd.read_csv(path + 'train.csv') # + 명령어는 문자를 앞문자와 더해줌  index_col=n n번째 컬럼을 인덱스로 인식
            
test_set = pd.read_csv(path + 'test.csv') # 예측에서 쓸거임  3

###################### IQR 이용해서 train_set에서 이상치나온 행 삭제########################
def detect_outliers(df, n, features):
    outlier_indices = []
    for col in features:
        Q1 = np.percentile(df[col], 25)
        Q3 = np.percentile(df[col], 75)
        IQR = Q3 - Q1
        
        outlier_step = 1.5 * IQR
        
        outlier_list_col = df[(df[col] < Q1 - outlier_step) | (df[col] > Q3 + outlier_step)].index
        outlier_indices.extend(outlier_list_col)
    outlier_indices = Counter(outlier_indices)
    multiple_outliers = list(k for k, v in outlier_indices.items() if v > n)
        
    return multiple_outliers
        
Outliers_to_drop = detect_outliers(train_set, 2, ['MSSubClass', 'LotFrontage', 'LotArea', 'OverallQual',
       'OverallCond', 'YearBuilt', 'YearRemodAdd', 'MasVnrArea', 'BsmtFinSF1',
       'BsmtFinSF2', 'BsmtUnfSF', 'TotalBsmtSF', '1stFlrSF', '2ndFlrSF',
       'LowQualFinSF', 'GrLivArea', 'BsmtFullBath', 'BsmtHalfBath', 'FullBath',
       'HalfBath', 'BedroomAbvGr', 'KitchenAbvGr', 'TotRmsAbvGrd',
       'Fireplaces', 'GarageYrBlt', 'GarageCars', 'GarageArea', 'WoodDeckSF',
       'OpenPorchSF', 'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea',
       'MiscVal', 'MoSold', 'YrSold'])

train_set.loc[Outliers_to_drop]

train_set = train_set.drop(Outliers_to_drop, axis = 0).reset_index(drop=True)
train_set.shape

print(train_set)
#############################################################################

# 수치형 변수와 범주형 변수 찾기
numerical_feats = train_set.dtypes[train_set.dtypes != "object"].index
categorical_feats = train_set.dtypes[train_set.dtypes == "object"].index
numerical_feats_ = test_set.dtypes[test_set.dtypes != "object"].index
categorical_feats_ = test_set.dtypes[test_set.dtypes == "object"].index
# print("Number of Numberical features: ", len(numerical_feats)) # 37
# print("Number of Categorical features: ", len(categorical_feats)) # 43


# # ##############변수명 출력
# print(train_set[numerical_feats].columns)      
# print("*"*79)
# print(train_set[categorical_feats].columns)      
# print(test_set[numerical_feats_].columns)      
# print("*"*79)
# print(test_set[categorical_feats_].columns)   

# ###################범주형변수값 수치형으로 변환###############
# train_set_encoded = train_set.drop(numerical_feats,axis=1)
# print(train_set_encoded)

# test_set_encoded = test_set.drop(numerical_feats_,axis=1)
# print(test_set_encoded)

# le = LabelEncoder()

# train_set_encoded.loc[:,:] = \
# train_set_encoded.loc[:,:].apply(LabelEncoder().fit_transform)    

# print(train_set_encoded)

# train_set = pd.concat([train_set_encoded, train_set.loc[:,numerical_feats]], axis=1)

# print(train_set)

# test_set_encoded.loc[:,:] = \
# test_set_encoded.loc[:,:].apply(LabelEncoder().fit_transform)    

# print(test_set_encoded)

# test_set = pd.concat([test_set_encoded, test_set.loc[:,numerical_feats_]], axis=1)

# print(test_set)

#################긁어온거####################################

num_strong_corr = ['SalePrice','OverallQual','TotalBsmtSF','GrLivArea','GarageCars',
                   'FullBath','YearBuilt','YearRemodAdd']

num_weak_corr = ['MSSubClass', 'LotFrontage', 'LotArea', 'OverallCond', 'MasVnrArea', 'BsmtFinSF1',
                 'BsmtFinSF2', 'BsmtUnfSF', '1stFlrSF', '2ndFlrSF','LowQualFinSF', 'BsmtFullBath',
                 'BsmtHalfBath', 'HalfBath', 'BedroomAbvGr', 'KitchenAbvGr', 'TotRmsAbvGrd',
                 'Fireplaces', 'GarageYrBlt', 'GarageArea', 'WoodDeckSF','OpenPorchSF',
                 'EnclosedPorch', '3SsnPorch', 'ScreenPorch', 'PoolArea', 'MiscVal', 'MoSold', 'YrSold']

catg_strong_corr = ['MSZoning', 'Neighborhood', 'Condition2', 'MasVnrType', 'ExterQual',
                    'BsmtQual','CentralAir', 'Electrical', 'KitchenQual', 'SaleType']

catg_weak_corr = ['Street', 'Alley', 'LotShape', 'LandContour', 'Utilities', 'LotConfig', 
                  'LandSlope', 'Condition1',  'BldgType', 'HouseStyle', 'RoofStyle', 
                  'RoofMatl', 'Exterior1st', 'Exterior2nd', 'ExterCond', 'Foundation', 
                  'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2', 'Heating', 
                  'HeatingQC', 'Functional', 'FireplaceQu', 'GarageType', 'GarageFinish', 
                  'GarageQual', 'GarageCond', 'PavedDrive', 'PoolQC', 'Fence', 'MiscFeature', 
                  'SaleCondition' ]

cols_fillna = ['PoolQC','MiscFeature','Alley','Fence','MasVnrType','FireplaceQu',
               'GarageQual','GarageCond','GarageFinish','GarageType', 'Electrical',
               'KitchenQual', 'SaleType', 'Functional', 'Exterior2nd', 'Exterior1st',
               'BsmtExposure','BsmtCond','BsmtQual','BsmtFinType1','BsmtFinType2',
               'MSZoning', 'Utilities']

for col in cols_fillna : 
    train_set[col].fillna('None', inplace=True)
    test_set[col].fillna('None', inplace=True)

total = train_set.isnull().sum().sort_values(ascending=False)
percent = (train_set.isnull().sum()/train_set.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total','Percent'])

train_set.fillna(train_set.mean(), inplace=True)
test_set.fillna(test_set.mean(), inplace=True)

total = train_set.isnull().sum().sort_values(ascending=False)
percent = (train_set.isnull().sum()/train_set.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])

print(train_set.isnull().sum().sum(), test_set.isnull().sum().sum()) # 0 0 출력시 결측치 확인 끝

id_test = test_set['Id']

to_drop_num = num_weak_corr
to_drop_catg = catg_weak_corr

cols_to_drop = ['Id'] + to_drop_num + to_drop_catg

for df in [train_set, test_set] :
    df.drop(cols_to_drop, inplace=True, axis = 1)
    
# 'MSZoning'
msz_catg2 = ['RM', 'RH']
msz_catg3 = ['RL', 'FV'] 

# Neighborhood
nbhd_catg2 = ['Blmngtn', 'ClearCr', 'CollgCr', 'Crawfor', 'Gilbert', 'NWAmes', 'Somerst', 'Timber', 'Veenker']
nbhd_catg3 = ['NoRidge', 'NridgHt', 'StoneBr']

# Condition2
cond2_catg2 = ['Norm', 'RRAe']
cond2_catg3 = ['PosA', 'PosN'] 

# SaleType
SlTy_catg1 = ['Oth']
SlTy_catg3 = ['CWD']
SlTy_catg4 = ['New', 'Con']

for df in [train_set, test_set]:
    
    df['MSZ_num'] = 1  
    df.loc[(df['MSZoning'].isin(msz_catg2) ), 'MSZ_num'] = 2    
    df.loc[(df['MSZoning'].isin(msz_catg3) ), 'MSZ_num'] = 3        
    
    df['NbHd_num'] = 1       
    df.loc[(df['Neighborhood'].isin(nbhd_catg2) ), 'NbHd_num'] = 2    
    df.loc[(df['Neighborhood'].isin(nbhd_catg3) ), 'NbHd_num'] = 3    

    df['Cond2_num'] = 1       
    df.loc[(df['Condition2'].isin(cond2_catg2) ), 'Cond2_num'] = 2    
    df.loc[(df['Condition2'].isin(cond2_catg3) ), 'Cond2_num'] = 3    
    
    df['Mas_num'] = 1       
    df.loc[(df['MasVnrType'] == 'Stone' ), 'Mas_num'] = 2 
    
    df['ExtQ_num'] = 1       
    df.loc[(df['ExterQual'] == 'TA' ), 'ExtQ_num'] = 2     
    df.loc[(df['ExterQual'] == 'Gd' ), 'ExtQ_num'] = 3     
    df.loc[(df['ExterQual'] == 'Ex' ), 'ExtQ_num'] = 4     
   
    df['BsQ_num'] = 1          
    df.loc[(df['BsmtQual'] == 'Gd' ), 'BsQ_num'] = 2     
    df.loc[(df['BsmtQual'] == 'Ex' ), 'BsQ_num'] = 3     
 
    df['CA_num'] = 0          
    df.loc[(df['CentralAir'] == 'Y' ), 'CA_num'] = 1    

    df['Elc_num'] = 1       
    df.loc[(df['Electrical'] == 'SBrkr' ), 'Elc_num'] = 2 


    df['KiQ_num'] = 1       
    df.loc[(df['KitchenQual'] == 'TA' ), 'KiQ_num'] = 2     
    df.loc[(df['KitchenQual'] == 'Gd' ), 'KiQ_num'] = 3     
    df.loc[(df['KitchenQual'] == 'Ex' ), 'KiQ_num'] = 4      
    
    df['SlTy_num'] = 2       
    df.loc[(df['SaleType'].isin(SlTy_catg1) ), 'SlTy_num'] = 1  
    df.loc[(df['SaleType'].isin(SlTy_catg3) ), 'SlTy_num'] = 3  
    df.loc[(df['SaleType'].isin(SlTy_catg4) ), 'SlTy_num'] = 4 

train_set.drop(['MSZoning','Neighborhood' , 'Condition2', 'MasVnrType', 'ExterQual', 'BsmtQual','CentralAir', 'Electrical', 'KitchenQual', 'SaleType', 'Cond2_num', 'Mas_num', 'CA_num', 'Elc_num', 'SlTy_num'], axis = 1, inplace = True)
test_set.drop(['MSZoning', 'Neighborhood' , 'Condition2', 'MasVnrType', 'ExterQual', 'BsmtQual','CentralAir', 'Electrical', 'KitchenQual', 'SaleType', 'Cond2_num', 'Mas_num', 'CA_num', 'Elc_num', 'SlTy_num'], axis = 1, inplace = True)

##############################긁어온거끝################################

x = train_set.drop(['SalePrice'], axis=1)
y = train_set['SalePrice']

x_train, x_test, y_train, y_test = train_test_split(x,y,
                                                    train_size=0.8,
                                                    random_state=30
                                                    )

print(x_train.shape, x_test.shape) # (1070, 12) (268, 12)
print(y_train.shape, y_test.shape) # (1070,) (268,)

scaler = StandardScaler()
scaler.fit(x_train)
sctrain = scaler.transform(x_train)
x_test = scaler.transform(x_test)
print(np.min(x_train))   # 0.0
print(np.max(x_train))   # 0.0 컬럼별로 나누어주어야 한다
print(np.min(x_test))
print(np.max(x_test))



x_train = x_train.reshape(1070,12,1)
x_test = x_test.reshape(268,12,1)


# scaler = MinMaxSc# from sklearn.preprocessing import MinMaxScaler, StandardScaler
# from sklearn.preprocessing import MaxAbsScaler, RobustScaler
# scaler = RobustScaler()
# scaler = MaxAbsScaler()

#scaler = MinMaxScaler()
# scaler = StandardScaler()
# scaler.fit(x_train)
# sctrain = scaler.transform(x_train)
# x_test = scaler.transform(x_test)
# print(np.min(x_train))   # 0.0
# print(np.max(x_train))   # 0.0 컬럼별로 나누어주어야 한다
# print(np.min(x_test))
# print(np.max(x_test))

#2. 모델구성

model = Sequential()

model.add(LSTM(units=64, return_sequences=True,
               input_shape=(12,1)))
model.add(LSTM(32, return_sequences=False,
               activation='relu'))
model.add(Dense(30, activation='relu'))
model.add(Dense(1, activation='linear'))
model.summary()
# model.add(Dense(24, input_dim=12))
# model.add(Dense(48, activation = 'swish'))
# model.add(Dense(96, activation = 'swish'))
# model.add(Dense(48))
# model.add(Dense(24))
# model.add(Dense(12, activation = 'swish'))
# model.add(Dense(1))

# input1 = Input(shape=(12,))
# dense1 = Dense(10)(input1)
# drop1 = Dropout(0.12)(dense1)
# dense2 = Dense(5, activation='relu')(drop1)
# dense3 = Dense(3, activation='relu')(dense2)
# output1 = Dense(1)(dense3)
# model = Model(inputs=input1, outputs=output1)

# model.save('./_save/k23_smm_house.h5')



#3. 컴파일, 훈련

start_time = time.time()
model.compile(loss='mse', optimizer='adam')

from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint


earlystopping = EarlyStopping(monitor='val_loss', patience=100, mode='min', verbose=1, # mode='min'뿐아니라 max도 있음  디폴드값 찾아볼것 모르면 오토 
              restore_best_weights=True)

a = model.fit(x_train, y_train, epochs=100, batch_size=5000,
          validation_split=0.2,
          callbacks = [earlystopping],
          verbose=1)   # a 대신에 hist 라고 쓰임 콜백을 하겠다 얼리 스탑잉을               

print(a)
print(a.history['val_loss']) # 대괄호로 loss , val loss 값 출력 가능

#4. 평가, 예측
loss = model.evaluate(x_test, y_test)
print('loss : ', loss)

y_predict = model.predict(x_test)

def RMSE(a, b):
    return np.sqrt(mean_squared_error(a, b))

rmse = RMSE(y_test, y_predict)
print("RMSE : ", rmse)

r2 = r2_score(y_test, y_predict)
print('r2스코어 : ', r2)

# y_summit = model.predict(test_set)

# print(y_summit)
# print(y_summit.shape) # (1459, 1)

# submission_set = pd.read_csv(path + 'sample_submission.csv',   #      + 명령어는 문자를 앞문자와 더해줌
#                              index_col=0)   #          index_col=n n번째 컬럼을 인덱스로 인식

# print(submission_set)

# submission_set['SalePrice'] = y_summit
# print(submission_set)

# submission_set.to_csv(path + 'submission.csv', index = True)

end_time = time.time()-start_time
print('걸린시간 : ', end_time)
model.summary()

# 없음 
# loss :  1455271808.0
# RMSE :  38148.02488323841
# r2스코어 :  0.7300449386231636
# 걸린시간 :  10.263057947158813


# min max 
# loss :  499806240.0
# RMSE :  22356.34617029612
# r2스코어 :  0.907285211622269
# 걸린시간 :  23.78767156600952

# stardard
# loss :  895411648.0
# RMSE :  29923.431044146364
# r2스코어 :  0.8338998069718222
# 걸린시간 :  21.214653253555298

# 함수형 모델 
# loss :  1548992384.0
# RMSE :  39357.239970521274
# r2스코어 :  0.7126596413211777
# 걸린시간 :  31.436527729034424


