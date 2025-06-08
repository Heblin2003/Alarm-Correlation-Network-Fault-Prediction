import pandas as pd
import numpy as np
import random
import re
from datetime import datetime, timedelta
from collections import deque

# --- Configuration ---
num_devices = 120
num_data_points = 1000
start_datetime = datetime(2023, 6, 6, 0, 0, 0)
end_datetime = datetime(2024, 1, 1, 23, 45, 0)
interval_minutes = 15
locations = ["New York", "London", "Tokyo", "Sydney", "Frankfurt"]

# --- Device IDs ---
device_ids = [
    "ce-ro-2", "cpe-sw-12", "cpe-sw-4", "ce-ro-24", "cpe-sw-10", "ce-ro-21", "ce-ro-17", "ce-ro-8",
    "ce-ro-14", "cpe-ro-4", "cpe-sw-6", "core-sw-1", "cpe-sw-1", "cpe-sw-7", "cpe-sw-5", "ce-ro-10",
    "ce-ro-6", "ce-ro-22", "cpe-sw-8", "core-sw-7", "cpe-ro-6", "cpe-sw-24", "cpe-ro-28", "core-sw-4",
    "ce-ro-15", "ce-ro-20", "ce-ro-19", "cpe-ro-27", "cpe-ro-31", "ce-ro-16", "pe-ro-1", "ce-ro-4",
    "cpe-sw-22", "ce-ro-7", "cpe-ro-7", "pe-ro-7", "cpe-sw-21", "cpe-ro-8", "pe-ro-3", "pe-ro-6",
    "core-sw-8", "cpe-ro-29", "cpe-ro-12", "cpe-sw-25", "cpe-ro-33", "ce-ro-12", "core-sw-6", "cpe-ro-14",
    "cpe-sw-23", "cpe-ro-3", "cpe-ro-9", "ce-ro-18", "cpe-ro-1", "cpe-ro-2", "ce-ro-9", "pe-ro-5",
    "cpe-ro-25", "pe-ro-4", "cpe-ro-34", "core-sw-5", "cpe-ro-17", "ce-ro-11", "cpe-ro-39", "cpe-sw-19",
    "cpe-fw-1", "cpe-ro-20", "cpe-ro-16", "cpe-ro-26", "cpe-ro-30", "ce-ro-3", "cpe-ro-41", "core-sw-2",
    "cpe-sw-3", "ce-ro-5", "core-sw-3", "cpe-ro-18", "cpe-ro-42", "cpe-sw-9", "cpe-sw-18", "cpe-ro-11",
    "core-ro-7", "ce-ro-1", "cpe-ro-32", "cpe-ro-10", "core-ro-1", "cpe-ro-35", "cpe-ro-5", "cpe-sw-2",
    "cpe-ro-37", "pe-ro-2", "ce-ro-13", "pe-ro-8", "cpe-ro-36", "cpe-ro-24", "ce-ro-23", "core-ro-8",
    "cpe-ro-15", "cpe-ro-40", "cpe-sw-11", "cpe-ro-38", "cpe-ro-22", "cpe-ro-23", "cpe-sw-27", "core-ro-2",
    "cpe-fw-11", "core-ro-3", "cpe-ro-21", "core-ro-4", "core-ro-5", "cpe-ro-19", "core-ro-6", "cpe-sw-29",
    "cpe-sw-26", "cpe-sw-30", "cpe-sw-31", "cpe-sw-35", "cpe-sw-32", "cpe-ro-13", "cpe-sw-28", "cpe-sw-40"
]

# --- Function to determine EquipmentType ---
def get_equipment_type(device_id):
    if re.search(r'-ro-', device_id):
        return "Router"
    elif re.search(r'-sw-', device_id):
        return "Switch"
    elif re.search(r'-fw-', device_id):
        return "Firewall"
    return "Unknown"

# --- Assign parent device based on type ---
def assign_parent_devices(device_ids):
    routers = [d for d in device_ids if '-ro-' in d]
    switches = [d for d in device_ids if '-sw-' in d]
    firewalls = [d for d in device_ids if '-fw-' in d]
    parents = {}
    for d in device_ids:
        dtype = get_equipment_type(d)
        if dtype == "Router":
            parents[d] = d
        elif dtype == "Switch":
            parents[d] = random.choice(routers)
        elif dtype == "Firewall":
            parents[d] = random.choice(routers + switches)
        else:
            parents[d] = ""
    return parents

# --- Normal Operating Ranges ---
normal_ranges = {
    "SpanLoss": {
        "initial": (1.0, 1.5),
        "degradation_rate": (0.01, 0.1),
        "alarm_threshold": 2.0
    },
    "OpticalReturnLoss": {
        "initial": (55.0, 60.0),
        "degradation_rate": (-0.005, -0.001),
        "alarm_threshold": 50.0
    },
    "Temperature": {
        "initial": (30.0, 35.0),
        "degradation_rate": (0.007, 0.015),
        "alarm_threshold": 40.0
    },
    "Voltage": {
        "initial": (11.8, 12.2),
        "degradation_rate": (-0.003, -0.001),
        "alarm_threshold": 11.0
    }
}

# --- External Fault Probabilities ---
external_fault_probabilities = {
    "PowerOutage": 0.02,
    "FiberCut": 0.015,
    "SevereWeather": 0.03
}

# --- Generate random metric with noise ---
def generate_metric(start, end, noise_level=0.1):
    value = random.uniform(start, end)
    noise = random.uniform(-noise_level, noise_level) * (end - start)
    return round(value + noise, 1)

# --- Simulate degradation ---
def simulate_degradation(start_value, degradation_rate, timestamp, last_maintenance, maintenance_impact=0.5):
    time_since_maintenance = (timestamp - last_maintenance).days / 365
    degradation = start_value + (degradation_rate * time_since_maintenance)
    if degradation > start_value:
        degradation *= (1 - maintenance_impact)
    return degradation

# --- Generate additional metrics ---
def generate_metrics():
    upstream_status = random.choices(['up', 'down', 'degraded'], weights=[0.75, 0.15, 0.10])[0]
    downstream_status = random.choices(['all_up', 'partial_down', 'all_down'], weights=[0.6, 0.3, 0.1])[0]
    interface_status = random.choices(['up', 'down', 'testing'], weights=[0.50, 0.40, 0.10])[0]
    in_errors = random.randint(0, 400)
    out_errors = random.randint(0, 400)
    cpu = random.randint(20, 100)
    memory = random.randint(20, 100)
    temp = random.choices(['normal', 'warning', 'critical'], weights=[0.8, 0.15, 0.05])[0]
    fan = random.choices(['normal', 'warning', 'failed'], weights=[0.85, 0.10, 0.05])[0]
    power = random.choices(['normal', 'warning', 'failed'], weights=[0.85, 0.10, 0.05])[0]
    alarms = random.randint(0, 5)
    impact_score = round(random.uniform(0, 1), 2)
    return {
        "upstream_status": upstream_status,
        "downstream_status": downstream_status,
        "interface_status": interface_status,
        "interface_in_errors": in_errors,
        "interface_out_errors": out_errors,
        "cpu_utilization": cpu,
        "memory_utilization": memory,
        "temperature_status": temp,
        "fan_status": fan,
        "power_status": power,
        "alarms_count": alarms,
        "downstream_impact_score": impact_score
    }

# --- Determine root cause ---
def determine_root_cause(row):
    if row['upstream_status'] == 'up' and row['downstream_status'] == 'all_down':
        return 1
    if row['interface_out_errors'] > 250 and row['temperature_status'] != 'normal':
        return 1
    if row['downstream_status'] == 'partial_down' and row['interface_status'] == 'down' and row['alarms_count'] > 2:
        return 1
    if row['cpu_utilization'] > 90 and row['memory_utilization'] > 90 and row['fan_status'] == 'failed':
        return 1
    if row['temperature_status'] == 'critical' and row['interface_in_errors'] > 300:
        return 1
    return 0

# --- Device Initialization ---
devices = {}
parent_map = assign_parent_devices(device_ids)
for device_id in device_ids:
    devices[device_id] = {
        "EquipmentType": get_equipment_type(device_id),
        "Location": random.choice(locations),
        "InstallationDate": start_datetime - timedelta(days=random.randint(1, 1825)),
        "LastMaintenance": start_datetime - timedelta(days=random.randint(30, 730)),
        "SpanLoss": generate_metric(*normal_ranges["SpanLoss"]["initial"]),
        "OpticalReturnLoss": generate_metric(*normal_ranges["OpticalReturnLoss"]["initial"]),
        "Temperature": generate_metric(*normal_ranges["Temperature"]["initial"]),
        "Voltage": generate_metric(*normal_ranges["Voltage"]["initial"]),
        "DegradationRate_SpanLoss": random.uniform(*normal_ranges["SpanLoss"]["degradation_rate"]),
        "DegradationRate_OpticalReturnLoss": random.uniform(*normal_ranges["OpticalReturnLoss"]["degradation_rate"]),
        "DegradationRate_Temperature": random.uniform(*normal_ranges["Temperature"]["degradation_rate"]),
        "DegradationRate_Voltage": random.uniform(*normal_ranges["Voltage"]["degradation_rate"]),
        "TemperatureHistory": deque(maxlen=4)
    }

# --- Data Generation ---
data = []
total_intervals = (end_datetime - start_datetime) // timedelta(minutes=interval_minutes)
intervals_needed = (num_data_points + num_devices - 1) // num_devices  # Ceiling division
intervals_needed = min(intervals_needed, total_intervals)  # Limit to available intervals

current_timestamp = start_datetime
for _ in range(intervals_needed):
    for device_id in device_ids[:min(num_devices, num_data_points - len(data))]:  # Limit devices
        if len(data) >= num_data_points:
            break
        device = devices[device_id]
        timestamp = current_timestamp

        # Simulate Degradation
        device["SpanLoss"] = simulate_degradation(
            device["SpanLoss"], device["DegradationRate_SpanLoss"], timestamp, device["LastMaintenance"]
        )
        device["OpticalReturnLoss"] = simulate_degradation(
            device["OpticalReturnLoss"], device["DegradationRate_OpticalReturnLoss"], timestamp, device["LastMaintenance"]
        )
        device["Temperature"] = simulate_degradation(
            device["Temperature"], device["DegradationRate_Temperature"], timestamp, device["LastMaintenance"]
        )
        device["Voltage"] = simulate_degradation(
            device["Voltage"], device["DegradationRate_Voltage"], timestamp, device["LastMaintenance"]
        )

        # External Factors
        had_power_outage = random.random() < external_fault_probabilities["PowerOutage"]
        had_fiber_cut = random.random() < external_fault_probabilities["FiberCut"]

        # Impact of External Factors
        if had_power_outage:
            device["Voltage"] = random.uniform(10.0, 11.0)
        if had_fiber_cut:
            device["SpanLoss"] = normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.5, 1.5)
            device["OpticalReturnLoss"] = min(
                device["OpticalReturnLoss"],
                normal_ranges["OpticalReturnLoss"]["alarm_threshold"] - random.uniform(1.0, 5.0)
            )

        # Generate Additional Metrics
        metrics = generate_metrics()

        # Force Fault Injection (10% chance)
        inject_fault = random.random() < 0.10

        # Precompute Alarms Based on Metrics
        alarm_span_loss = 1 if device["SpanLoss"] > normal_ranges["SpanLoss"]["alarm_threshold"] else 0
        alarm_optical_return_loss = 1 if device["OpticalReturnLoss"] < normal_ranges["OpticalReturnLoss"]["alarm_threshold"] else 0
        alarm_temperature = 1 if device["Temperature"] > normal_ranges["Temperature"]["alarm_threshold"] else 0
        alarm_voltage = 1 if device["Voltage"] < normal_ranges["Voltage"]["alarm_threshold"] else 0

        # Create a Temporary Row for Root Cause Calculation
        temp_row = {
            "upstream_status": metrics["upstream_status"],
            "downstream_status": metrics["downstream_status"],
            "interface_status": metrics["interface_status"],
            "interface_in_errors": metrics["interface_in_errors"],
            "interface_out_errors": metrics["interface_out_errors"],
            "cpu_utilization": metrics["cpu_utilization"],
            "memory_utilization": metrics["memory_utilization"],
            "temperature_status": metrics["temperature_status"],
            "fan_status": metrics["fan_status"],
            "power_status": metrics["power_status"],
            "alarms_count": metrics["alarms_count"]
        }

        # Determine Root Cause
        is_root_cause = determine_root_cause(temp_row)

        # Adjust Alarms Based on IsRootCause
        if is_root_cause:
            # Ensure at least one alarm is triggered for root cause
            # Map root cause conditions to relevant alarms
            if temp_row['upstream_status'] == 'up' and temp_row['downstream_status'] == 'all_down':
                # Likely a fiber or connectivity issue
                alarm_span_loss = 1
                alarm_optical_return_loss = 1
                device["SpanLoss"] = max(device["SpanLoss"], normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.5, 1.5))
                device["OpticalReturnLoss"] = min(device["OpticalReturnLoss"], normal_ranges["OpticalReturnLoss"]["alarm_threshold"] - random.uniform(1.0, 5.0))
            elif temp_row['interface_out_errors'] > 250 and temp_row['temperature_status'] != 'normal':
                # Temperature-related issue affecting interfaces
                alarm_temperature = 1
                device["Temperature"] = max(device["Temperature"], normal_ranges["Temperature"]["alarm_threshold"] + random.uniform(1.0, 3.0))
                if random.random() < 0.5:  # Optional secondary alarm
                    alarm_span_loss = 1
                    device["SpanLoss"] = max(device["SpanLoss"], normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.1, 0.5))
            elif temp_row['downstream_status'] == 'partial_down' and temp_row['interface_status'] == 'down' and temp_row['alarms_count'] > 2:
                # Interface or connectivity issue
                alarm_span_loss = 1
                device["SpanLoss"] = max(device["SpanLoss"], normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.5, 1.5))
                if random.random() < 0.5:
                    alarm_optical_return_loss = 1
                    device["OpticalReturnLoss"] = min(device["OpticalReturnLoss"], normal_ranges["OpticalReturnLoss"]["alarm_threshold"] - random.uniform(1.0, 5.0))
            elif temp_row['cpu_utilization'] > 90 and temp_row['memory_utilization'] > 90 and temp_row['fan_status'] == 'failed':
                # Overheating due to high resource usage
                alarm_temperature = 1
                device["Temperature"] = max(device["Temperature"], normal_ranges["Temperature"]["alarm_threshold"] + random.uniform(1.0, 3.0))
                alarm_voltage = 1
                device["Voltage"] = min(device["Voltage"], normal_ranges["Voltage"]["alarm_threshold"] - random.uniform(0.5, 1.0))
            elif temp_row['temperature_status'] == 'critical' and temp_row['interface_in_errors'] > 300:
                # Critical temperature affecting interfaces
                alarm_temperature = 1
                device["Temperature"] = max(device["Temperature"], normal_ranges["Temperature"]["alarm_threshold"] + random.uniform(1.0, 3.0))
                if random.random() < 0.5:
                    alarm_span_loss = 1
                    device["SpanLoss"] = max(device["SpanLoss"], normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.1, 0.5))
        else:
            # For non-root cause cases, allow alarms due to degradation or external factors
            # Apply correlations
            if alarm_temperature and random.random() < 0.3:
                alarm_span_loss = 1
                device["SpanLoss"] = max(device["SpanLoss"], normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.1, 0.5))
            if alarm_temperature and random.random() < 0.2:
                alarm_voltage = 1
                device["Voltage"] = min(device["Voltage"], normal_ranges["Voltage"]["alarm_threshold"] - random.uniform(0.1, 0.3))
            if had_power_outage:
                alarm_voltage = 1
                device["Voltage"] = min(device["Voltage"], random.uniform(10.0, 11.0))

        # Time-Delayed Correlations
        device["TemperatureHistory"].append(device["Temperature"])
        if len(device["TemperatureHistory"]) == device["TemperatureHistory"].maxlen:
            if all(t > normal_ranges["Temperature"]["alarm_threshold"] for t in device["TemperatureHistory"]):
                alarm_span_loss = 1
                device["SpanLoss"] = max(device["SpanLoss"], normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.2, 0.8))

        # Force Fault Injection (Overrides for Balancing)
        if inject_fault:
            alarm_temperature = 1
            alarm_voltage = 1
            alarm_span_loss = 1 if random.random() < 0.6 else 0
            alarm_optical_return_loss = 1 if random.random() < 0.5 else 0
            device["Temperature"] = normal_ranges["Temperature"]["alarm_threshold"] + random.uniform(1.0, 3.0)
            device["Voltage"] = normal_ranges["Voltage"]["alarm_threshold"] - random.uniform(0.5, 1.0)
            if alarm_span_loss:
                device["SpanLoss"] = normal_ranges["SpanLoss"]["alarm_threshold"] + random.uniform(0.5, 1.5)
            if alarm_optical_return_loss:
                device["OpticalReturnLoss"] = normal_ranges["OpticalReturnLoss"]["alarm_threshold"] - random.uniform(2.0, 6.0)
            metrics["cpu_utilization"] = random.randint(90, 100)
            metrics["memory_utilization"] = random.randint(90, 100)
            metrics["fan_status"] = 'failed'
            metrics["power_status"] = 'failed'
            metrics["interface_status"] = 'down'
            metrics["interface_in_errors"] = random.randint(300, 500)
            metrics["interface_out_errors"] = random.randint(300, 500)
            metrics["temperature_status"] = 'critical'
            metrics["alarms_count"] = random.randint(4, 5)
            metrics["downstream_status"] = random.choice(['all_down', 'partial_down'])

        # Create Final Row
        row = {
            "FaultInjected": int(inject_fault),
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "EquipmentID": device_id,
            "EquipmentType": device["EquipmentType"],
            "Location": device["Location"],
            "EquipmentAgeDays": (timestamp - device["InstallationDate"]).days,
            "Alarm_SpanLoss": alarm_span_loss,
            "Alarm_OpticalReturnLoss": alarm_optical_return_loss,
            "Alarm_Temperature": alarm_temperature,
            "Alarm_Voltage": alarm_voltage,
            "SpanLoss": device["SpanLoss"],
            "OpticalReturnLoss": device["OpticalReturnLoss"],
            "Temperature": device["Temperature"],
            "Voltage": device["Voltage"],
            "PowerOutage": had_power_outage,
            "FiberCut": had_fiber_cut,
            "ParentDeviceID": parent_map[device_id],
            **metrics,
            "IsRootCause": is_root_cause
        }

        data.append(row)

    current_timestamp += timedelta(minutes=interval_minutes)

# --- DataFrame Creation ---
df = pd.DataFrame(data, columns=[
    "Timestamp", "EquipmentID", "EquipmentType", "Location",
    "EquipmentAgeDays", "Alarm_SpanLoss", "Alarm_OpticalReturnLoss",
    "Alarm_Temperature", "Alarm_Voltage", "SpanLoss", "OpticalReturnLoss",
    "Temperature", "Voltage", "PowerOutage", "FiberCut", "ParentDeviceID",
    "upstream_status", "downstream_status", "interface_status",
    "interface_in_errors", "interface_out_errors", "cpu_utilization",
    "memory_utilization", "temperature_status", "fan_status", "power_status",
    "alarms_count", "downstream_impact_score", "IsRootCause", "FaultInjected"
])

# --- Save to CSV ---
df.to_csv("telecom_merge1.csv", index=False)

if __name__ == "__main__":
    print(f"Generated dataset with {len(df)} rows and saved as telecom_merge.csv")