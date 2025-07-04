# -*- coding: utf-8 -*-
"""Education Under Attack 2020 to 2025.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-KCL6RlGhti53Baycke98f90RRUK-5eP

**Library**
"""

import pandas as pd

"""**Dataset**"""

from google.colab import drive
drive.mount('/content/drive')
file_path = '/content/drive/My Drive/1_Latihan Colabs/1_Education Under Attack 2020 to 2025/dataset_education_danger_incident.csv'
df = pd.read_csv(file_path)

"""# **Preprocessing**"""

print(df)

df.isnull().sum()

df.duplicated().sum()

df = df.dropna(subset=['Latitude'])
df = df.dropna(subset=['Longitude'])
df = df.dropna(subset=['Geo Precision'])

df['Admin 1'] = df['Admin 1'].fillna('Unknown')
df['Location of event'] = df['Location of event'].fillna('Unknown')

df['Event Description'] = df['Event Description'].fillna('-')

df['Known Educators Kidnap Or Arrest Outcome'] = df['Known Educators Kidnap Or Arrest Outcome'].fillna('Unknown')
df['Known Student Kidnap Or Arrest Outcome'] = df['Known Student Kidnap Or Arrest Outcome'].fillna('Unknown')

df.isnull().sum()

df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df['Year'] = df['Date'].dt.year

df.info()

df.describe()

print(df)

"""# **Visualisasi 1**

**Visualisasi Geografis Kejadian**
"""

import folium

map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
education_map = folium.Map(location=map_center, zoom_start=2)

for index, row in df.iterrows():
    folium.Marker([row['Latitude'], row['Longitude']],
                  popup=f"Country: {row['Country']}<br>Date: {row['Date'].strftime('%Y-%m-%d')}<br>Location: {row['Location of event']}").add_to(education_map)

education_map

"""**Analisis Pelaku yang Dilaporkan**"""

perpetrator_counts = df['Reported Perpetrator'].value_counts()

print("Jumlah Kejadian per Pelaku yang Dilaporkan:")
print(perpetrator_counts)

plt.figure(figsize=(12, 7))
sns.barplot(x=perpetrator_counts.index, y=perpetrator_counts.values, hue=perpetrator_counts.index, palette='viridis', legend=False)
plt.title('Jumlah Kejadian per Pelaku yang Dilaporkan')
plt.xlabel('Pelaku yang Dilaporkan')
plt.ylabel('Jumlah Kejadian')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

"""**Analisis Dampak pada Siswa dan Pendidik**"""

impact_columns = ['Educators Killed', 'Educators Injured', 'Educators Kidnapped', 'Educators Arrested',
                  'Students Killed', 'Students Injured', 'Students Kidnapped', 'Students Arrested']

total_impact = df[impact_columns].sum()

print("Total Dampak pada Siswa dan Pendidik (2020-2025):")
print(total_impact)

plt.figure(figsize=(12, 7))
sns.barplot(x=total_impact.index, y=total_impact.values, hue=total_impact.index, palette='plasma', legend=False)
plt.title('Total Dampak pada Siswa dan Pendidik (2020-2025)')
plt.xlabel('Kategori Dampak')
plt.ylabel('Jumlah')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

"""**Visualisasi tren global per tahun**"""

yearly_counts = df['Year'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x=yearly_counts.index, y=yearly_counts.values, marker='o')
plt.title('Tren Kejadian Global per Tahun')
plt.xlabel('Tahun')
plt.ylabel('Jumlah Kejadian')
plt.grid(True)
plt.show()

"""**Analisis tren per wilayah/negara**"""

yearly_country_counts = df.groupby(['Year', 'Country']).size().reset_index(name='Incident Count')

N = 10
top_countries = yearly_country_counts.groupby('Country')['Incident Count'].sum().nlargest(N).index.tolist()

top_countries_yearly_counts = yearly_country_counts[yearly_country_counts['Country'].isin(top_countries)]

print("Top 10 Countries by Total Incident Count:")
print(top_countries)

plt.figure(figsize=(15, 8))
sns.lineplot(data=top_countries_yearly_counts, x='Year', y='Incident Count', hue='Country', marker='o')

plt.title('Tren Kejadian per Negara (Top 10)')
plt.xlabel('Tahun')
plt.ylabel('Jumlah Kejadian')
plt.grid(True)
plt.legend(title='Negara')
plt.xticks(top_countries_yearly_counts['Year'].unique())
plt.tight_layout()
plt.show()

"""# **Machine Learning**

**Feature engineering**
"""

df['Month'] = df['Date'].dt.month

def categorize_risk(row):
    total_casualties = row['Students Killed'] + row['Students Injured'] + row['Educators Killed'] + row['Educators Injured']
    if total_casualties == 0:
        return 0 # Low risk
    elif total_casualties <= 5:
        return 1 # Medium risk
    else:
        return 2 # High risk

df['Risk_Level'] = df.apply(categorize_risk, axis=1)
df.head()

monthly_incidents = df.groupby(['Country', 'Admin 1', 'Year', 'Month']).size().reset_index(name='Monthly_Incident_Count')
df = pd.merge(df, monthly_incidents, on=['Country', 'Admin 1', 'Year', 'Month'], how='left')
df.head()

"""**Data preparation for modeling**"""

import numpy as np
from sklearn.model_selection import train_test_split

features = ['Year', 'Latitude', 'Longitude', 'Attacks on Schools', 'Attacks on Universities',
            'Military Occupation of Education facility', 'Arson attack on education facility',
            'Forced Entry into education facility', 'Damage/Destruction To Ed facility Event',
            'Attacks on Students and Teachers', 'Educators Killed', 'Educators Injured',
            'Educators Kidnapped', 'Educators Arrested', 'Students Attacked in School',
            'Students Killed', 'Students Injured', 'Students Kidnapped', 'Students Arrested',
            'Sexual Violence Affecting School Age Children', 'Monthly_Incident_Count']
target = 'Risk_Level'

X = df[features]
y = df[target]

categorical_features = X.select_dtypes(include=['object', 'bool']).columns
X = pd.get_dummies(X, columns=categorical_features, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("Training set shape:", X_train.shape)
print("Testing set shape:", X_test.shape)

"""**Model selection**"""

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
print("Chosen model: RandomForestClassifier")

"""**Model training**"""

model.fit(X_train, y_train)

"""**Model evaluation**"""

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1-score: {f1}")

"""**Risk zone identification**"""

df['predicted_risk_level'] = model.predict(X)
high_risk_zones = df[df['predicted_risk_level'] == 2]
display(high_risk_zones.head())

"""**Visualization of risk zones**"""

import folium

map_center = [high_risk_zones['Latitude'].mean(), high_risk_zones['Longitude'].mean()]
high_risk_map = folium.Map(location=map_center, zoom_start=2)

for index, row in high_risk_zones.iterrows():
    folium.Marker([row['Latitude'], row['Longitude']],
                  popup=f"Country: {row['Country']}<br>Date: {row['Date'].strftime('%Y-%m-%d')}<br>Location: {row['Location of event']}").add_to(high_risk_map)

high_risk_map

"""## Summary:

### Data Analysis Key Findings

*   The analysis successfully created a 'Risk\_Level' feature by categorizing incidents based on the total number of casualties, with 0 indicating low risk, 1 for medium risk (up to 5 casualties), and 2 for high risk (more than 5 casualties).
*   A 'Monthly\_Incident\_Count' feature was engineered by aggregating the number of incidents per country, administrative region, year, and month.
*   A `RandomForestClassifier` model was selected and trained to predict the 'Risk\_Level'.
*   The trained model demonstrated high performance on the test set with an accuracy of 0.9937, precision of 0.9939, recall of 0.9937, and an F1-score of 0.9935.
*   The model was used to predict risk levels across the entire dataset, and incidents predicted as high risk (level 2) were identified.
*   The identified high-risk zones were successfully visualized on a map using `folium`, with markers indicating the location of each high-risk incident and providing details on country, date, and location in popups.

### Insights or Next Steps

*   The high performance metrics suggest the model is very effective at identifying high-risk zones based on the current features. Further investigation could explore feature importance to understand which factors contribute most to high risk.
*   The visualization on the map provides a clear geographical representation of high-risk areas, which can be used for targeted intervention and resource allocation. The next step could involve exploring temporal trends within these high-risk zones.

"""