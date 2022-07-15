# 29 - cifar10 

from asyncio import to_thread
from json import encoder
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.callbacks import EarlyStopping
from tensorflow.python.keras.models import Sequential, Input
from tensorflow.python.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D, Dropout, Conv1D, LSTM # 이미지는 2차원 2d 
from tensorflow.keras.datasets import mnist
from keras.datasets import cifar100
import numpy as np
import time
import tensorflow as tf 
import pandas as pd
from sklearn.metrics import accuracy_score, r2_score
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import OneHotEncoder, RobustScaler, StandardScaler

# 1 data

(x_train, y_train), (x_test, y_test) = cifar100.load_data()


print(x_train.shape, y_train.shape)   # ( 50000, 32, 32 3) ( 50000, 1 )
print(x_test.shape, y_test.shape)     # ( 10000, 32, 32 3) ( 10000, 1 )

x_train = x_train.reshape( 50000, 32*32*3 )
x_test = x_test.reshape( 10000, 32*32*3 )

print(x_train.shape)      # (60000, 28, 28, 1)
print(y_train.shape)

print(np.unique(y_train, return_counts=True))
print(np.unique(y_test, return_counts=True))

# scaler = RobustScaler()
scaler = StandardScaler()
scaler.fit(x_train)
scaler.fit(x_test)
x_train = scaler.transform(x_train)
x_test = scaler.transform(x_test)
print(np.min(x_train))   # 0.0
print(np.max(x_train))   # 0.0 컬럼별로 나누어주어야 한다
print(np.min(x_test))
print(np.max(x_test))

x_train = x_train.reshape( 50000, 32, 96 )
x_test = x_test.reshape( 10000, 32, 96 )

# 만들어봐 
# acc 0.98 이상 
# Conv2D 3줄 이상 
# onehotencoding 잊지말기

model = Sequential()

# y_train = pd.get_dummies(y_train)
# y_test = pd.get_dummies(y_test)

y_train = to_categorical(y_train)
y_test = to_categorical(y_test)


model = Sequential()
model.add(LSTM(units=10, return_sequences=True,
               input_shape=(32,96)))
model.add(LSTM(10, return_sequences=False,
               activation='relu'))
model.add(Dense(10, activation='relu'))
model.add(Dense(10, activation='softmax'))
model.add(Dense(100, activation='softmax'))


# compile. epochs

start_time = time.time()

earlystopping = EarlyStopping(monitor='val_loss', patience=300, mode='min', verbose=1,
                              restore_best_weights=True)

model.compile(loss = 'categorical_crossentropy', optimizer = 'adam',
              metrics = ['accuracy'])

a = model.fit(x_train, y_train, epochs=450, batch_size=5000,
              validation_split=0.2, callbacks= [earlystopping], verbose=1)

end_time = time.time()-start_time
print(a)
print(a.history['val_loss'])


# 4. evaluate , predict

loss = model.evaluate(x_test, y_test)
print('loss : ', loss)

y_predict = model.predict(x_test)

r2 = r2_score(y_test, y_predict)
print('r2score : ', r2)
# acc = accuracy_score(y_test, y_predict)

# print('acc.score : ', acc)
print('걸린시간 : ', end_time)



# accuracy: 0.2561 

# accuracy: 0.2602

# accuracy: 0.2783

# accuracy: 0.2828

# loss :  [3.991943836212158, 0.06930000334978104]
# 걸린시간 :  963.2978763580322

