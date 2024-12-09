import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the dataset
data = pd.read_csv("Flight Data.csv")  

# Preprocess data
data['IsDelayed'] = (data['Departure delay (Minutes)'] > 15).astype(int)
data['Scheduled Hour'] = pd.to_datetime(data['Scheduled departure time'], format='%H:%M').dt.hour

# Prepare features and target
X = data[['Carrier Code', 'Origin Airport', 'Destination Airport', 'Weather Conditions', 'Holiday Indicator', 'Scheduled Hour', 'Date (MM/DD/YYYY)']]
y = data['IsDelayed']

# Encode categorical data
X = pd.get_dummies(X)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save the trained model to a file
with open("trained_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model has been trained and saved to 'trained_model.pkl'")
