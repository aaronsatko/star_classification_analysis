import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

df = pd.read_csv('star_classification.csv')


# Distribution of Redshift
plt.figure(figsize=(10, 6))
plt.hist(df['redshift'], bins=50)
min_redshift = 0
max_redshift = 4
plt.xlim(min_redshift, max_redshift)
plt.xlabel('Redshift')
plt.ylabel('Frequency')
plt.title('Distribution of Redshift')
plt.savefig('plots/redshift_dist.png')

# Redshift Distribution By Class (GALAXY, QSO, STAR )
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='class', y='redshift')
plt.xlabel('Class')
plt.ylabel('Redshift')
plt.title('Redshift Distribution by Class')
plt.savefig('plots/redshift_class_dist.png')

# Correlation Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, fmt=".2f")
plt.title('Correlation Heatmap')
plt.savefig('plots/correlation_heatmap.png')
