# Alarm-Correlation-Network-Fault-Prediction
Alarm Correlation Network Fault  Prediction

# Root Cause Prediction Using XGBoost and Alarm Correlation with Association Rule Mining 

In a telecom network with 100 devices organized in a hierarchical structure, a fault affecting 
all devices is often traceable to a single root cause—typically a parent device whose failure 
cascades downstream. For example, a power outage in a parent router can trigger alarms in 
all connected switches and endpoints, resulting in 100 simultaneous error reports. Identifying 
the root cause amidst this flood of alarms is a critical challenge for network reliability and 
efficient troubleshooting. The goal of this approach is to: 

● Identify the root cause device(s) responsible for widespread faults. 
● Uncover patterns in alarms associated with root cause devices to improve future fault 
detection. 
● Reduce the noise from correlated alarms, focusing on actionable insights. 
Methodology 
This approach combines a machine learning algorithm (XGBoost) for root cause prediction 
with association rule mining to analyze alarm correlations among root cause devices. Here’s 
a detailed breakdown of the process: 

# 1. Root Cause Prediction with XGBoost: 

○ Why XGBoost? XGBoost is a powerful gradient-boosting algorithm widely 
used for classification tasks, particularly with tabular data. It excels in 
handling imbalanced datasets (as IsRootCause is likely imbalanced, with 
fewer root cause devices) and provides feature importance scores, which 
help understand the drivers of faults. Its ability to capture complex, non-linear 
relationships between features makes it ideal for this task. 

○ Data Preparation: The dataset was preprocessed by encoding categorical 
variables (e.g., EquipmentType, Location) using one-hot encoding and scaling 
numerical features (e.g., CPUUtilization, DownstreamImpactScore) with 
MinMaxScaler to normalize their values. Irrelevant columns like Timestamp, 
EquipmentID, and ParentDeviceID were excluded from the prediction task but 
retained for later temporal analysis. 

○ Model Training: The dataset was split into training (80%) and testing (20%) 
sets. XGBoost was trained on the training set to predict IsRootCause, using 
features like alarms, status indicators, and impact scores.The model was 
evaluated on the test set, yielding an accuracy of 96%. The classification 
report showed: 

○ Precision for class 0 (non-root cause): 0.99 

○ Precision for class 1 (root cause): 0.88 

○ Recall for class 1: 0.95 

○ F1-score for class 1: 0.92 

○ Confusion Matrix: [[155 5], [2 38]], indicating only 7 misclassifications out of 
200 test samples. 

○ Purpose: The trained model analyzes historical data to identify devices likely 
to be root causes of faults. For example, a router with a PowerOutage and 
high DownstreamImpactScore might be flagged as a root cause, as its failure 

could explain errors in downstream devices. 
# 2. Alarm Correlation with Association Rule Mining: 

○ Why Association Rule Mining? Once root cause devices are identified, 
understanding the patterns in their alarms is crucial for future fault prediction. 
Association rule mining, implemented using the Apriori algorithm, identifies 
frequent co-occurrences of alarms (e.g., Alarm_Voltage → Alarm_SpanLoss), 
revealing relationships that can be used to trace faults back to their source. 

○ Process: 

■ Data Selection: Focus on devices labeled as root causes (either 
predicted by XGBoost or actual IsRootCause = 1). Extract 
alarm-related features (Alarm_SpanLoss, Alarm_Voltage, etc.) for 
these devices. 

■ Apriori Algorithm: Convert alarm data into a boolean format (e.g., 
alarm triggered = 1, not triggered = 0). Apply the Apriori algorithm with 
a minimum support threshold (e.g., 0.05) to identify frequent alarm 
combinations, followed by generating association rules with a 
minimum confidence threshold (e.g., 0.5). 

■ Example Rule: A rule like Alarm_Voltage → Alarm_SpanLoss with 
high confidence (e.g., 0.9) indicates that when a voltage alarm is 
triggered in a root cause device, a span loss alarm is likely to follow, 
suggesting a causal relationship. 

○ Purpose: These rules help in understanding alarm patterns specific to root 
cause devices. For instance, if a future device exhibits both Alarm_Voltage 
and Alarm_SpanLoss, it can be quickly identified as a potential root cause 
based on historical patterns, streamlining troubleshooting. 
Temporal Analysis: Sequence Analysis 
Temporal analysis was conducted to explore the sequence of alarms in root cause devices. 

● Process: 

○ The dataset was grouped by EquipmentID, and Timestamp was converted to 
a datetime format for chronological sorting. 

○ Focused on devices with IsRootCause == 1, extracting their alarm columns 
and timestamps. 

○ A function (check_sequence) was defined to check if Alarm_Voltage precedes 
Alarm_SpanLoss in the timeline for each device. For each device, the 
timestamps of Alarm_Voltage and Alarm_SpanLoss were compared; if a span 
loss alarm occurred after a voltage alarm, the pair was marked as causal. 

● Result: In 21.3% of cases, Alarm_Voltage preceded Alarm_SpanLoss, suggesting a 
potential temporal relationship where voltage issues may lead to signal degradation. 

● Purpose: This analysis provides a temporal clue for root cause tracing. In a network 
hierarchy, a parent device’s voltage failure might occur first, followed by downstream 
effects like span loss, helping engineers prioritize voltage-related checks. 

# Granger Causality Test for Causal Inference 
The Granger Causality Test was applied to statistically test the causal relationship between 
Alarm_Voltage and Alarm_SpanLoss. 

● Why Granger Causality Test? The Granger Causality Test is a statistical method 
used to determine if one time series can predict another. In this context, it tests 
whether Alarm_Voltage can predict Alarm_SpanLoss, providing a more rigorous 
assessment of causality beyond simple temporal precedence. 

● Process: 

○ Data Selection: Focused on a single EquipmentID with sufficient 
observations for time-series analysis. The dataset was filtered to include 
Timestamp, Alarm_Voltage, and Alarm_SpanLoss for the selected device. 

○ Observation Check: The number of observations per EquipmentID was 
checked. The test requires at least 10 observations for a maxlag of 3 (to 
examine up to 3 time steps in the past). However, the maximum observations 
per device was 9, so the maxlag was reduced to 1. 

○ Data Preparation: The data was converted into a time-series format by 
setting Timestamp as the index, and alarm columns were cast to integers (0 
or 1). 

○ Granger Causality Test: The test was run using grangercausalitytests from 
statsmodels, with Alarm_SpanLoss as the dependent variable and 
Alarm_Voltage as the predictor. The test evaluates whether past values of 
Alarm_Voltage improve the prediction of Alarm_SpanLoss beyond using only 
past values of Alarm_SpanLoss. 

● Result: 

○ With maxlag=1, the test yielded a p-value of 0.6462 (F-test: F=0.2381, 
df_denom=5, df_num=1). Since the p-value is greater than 0.05, there is no 
statistically significant evidence that Alarm_Voltage Granger-causes 
Alarm_SpanLoss. 

○ Other test statistics (chi2, likelihood ratio) also confirmed this finding (p-values 
> 0.5). 

● Interpretation: 

○ The lack of statistical significance suggests that Alarm_Voltage does not 
Granger-cause Alarm_SpanLoss in this dataset. This could be due to the 
limited number of observations (9 per device), which reduces the test’s power 
to detect causality. 

○ Despite the statistical result, the temporal sequence analysis (21.3% 
precedence) still provides practical evidence of a potential relationship, which 
may be validated with more data. 

● Purpose: The Granger Causality Test adds a statistical layer to the temporal 
analysis, aiming to confirm whether the observed sequence of alarms reflects a 
causal relationship. While the test was inconclusive here, it highlights the need for 
more data to perform robust causal inference 
The network fault prediction approach implemented for identifying root cause devices in a 
telecom network proved to be highly effective, achieving a prediction accuracy of 96% using 
the XGBoost classifier. By integrating multiple techniques XGBoost for root cause prediction, 
association rule mining for alarm correlation, temporal sequence analysis, and the Granger 
Causality Test for causal inference this methodology provided a robust framework for 
diagnosing network faults.
