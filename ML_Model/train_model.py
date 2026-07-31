import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

# Load Dataset
df = pd.read_csv("dataset/heart.csv")

print(df.head())
print(df.columns)

# Convert text columns to numbers
encoder = LabelEncoder()

for col in df.select_dtypes(include="object").columns:
    df[col] = encoder.fit_transform(df[col])

# Features
X = df.drop("HeartDisease", axis=1)

# Target
y = df["HeartDisease"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Accuracy
pred = model.predict(X_test)

accuracy = accuracy_score(y_test, pred)

print("Accuracy :", accuracy)

# Save
joblib.dump(model, "ml_model/model.pkl")

print("Model Saved Successfully")