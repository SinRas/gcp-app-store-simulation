"""
Google Cloud Pub/Sub Data Publisher for App Store Simulation.

This module provides functionality to generate and publish simulated app store user interaction
events to Google Cloud Pub/Sub. It supports configurable data profiles, event types, and
publishing rates for testing and development purposes.

The module generates realistic mock data including:
- User search queries
- App reviews and ratings
- In-app purchases
- Device and OS information
- Geographic distribution

Example:
    python 01_publisher_initial.py --config publisher_config.json

Dependencies:
    - google-cloud-pubsub
    - faker
    - argparse
    - json
    - time
    - uuid
    - random

Author: App Store Simulation Team
License: MIT
"""

import argparse
import json
import time
import datetime
import pytz
import math
import uuid
import random
from typing import Dict, Any
from faker import Faker
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.publisher.futures import Future

# Global variables
HOURLY_MODULATION_FACTORS = [
    0.272, 0.251, 0.230, 0.210, 0.190,
    0.172, 0.155, 0.138, 0.123, 0.108,
    0.095, 0.083, 0.072, 0.062, 0.054,
    0.047, 0.041, 0.036, 0.033, 0.031,
    0.030, 0.031, 0.033, 0.036, 0.041,
    0.047, 0.054, 0.062, 0.072, 0.083,
    0.095, 0.108, 0.123, 0.138, 0.155,
    0.172, 0.190, 0.210, 0.230, 0.251,
    0.273, 0.295, 0.318, 0.341, 0.365,
    0.389, 0.414, 0.439, 0.464, 0.490,
    0.515, 0.540, 0.566, 0.591, 0.616,
    0.641, 0.665, 0.689, 0.712, 0.735,
    0.758, 0.779, 0.800, 0.820, 0.840,
    0.858, 0.875, 0.892, 0.907, 0.922,
    0.935, 0.947, 0.958, 0.968, 0.976,
    0.983, 0.989, 0.994, 0.997, 0.999,
    1.000, 0.999, 0.997, 0.994, 0.989,
    0.983, 0.976, 0.968, 0.958, 0.947,
    0.935, 0.922, 0.907, 0.892, 0.875,
    0.858, 0.840, 0.820, 0.800, 0.779,
    0.758, 0.735, 0.712, 0.689, 0.665,
    0.641, 0.616, 0.591, 0.566, 0.540,
    0.515, 0.490, 0.464, 0.439, 0.414,
    0.389, 0.365, 0.341, 0.318, 0.295,
]  # Each hour broken into 5 segments -> 24*5=120 factors
USERS_BY_COUNTRY = {}
GLOBAL_TIMESTAMP_MICROS = 0
GLOBAL_TIMESTAMP_HOUR = 0.0
GLOBAL_RATE_MAXIMUM = 0.0

# Initialize Faker for generating mock data
fake = Faker()

def get_current_timestamp_micros() -> int:
    """
    Get the current timestamp in microseconds since epoch.
    """
    return int(time.time() * 1_000_000)

def get_current_hour() -> float:
    """
    Get the current hour in the timezone of Iran.
    """
    now = datetime.datetime.now(tz=pytz.timezone("Asia/Tehran"))
    return now.hour + round(now.minute/60, 1)

def user_daily_activity_pattern(hour: float) -> float:
    """
    Get the user's daily activity pattern based on the hour.
    """
    # Discretized to reduce computation time
    # Continiuous modulation: modulation = 0.03 + 0.97 * (1+math.cos( (hour-16) * (2*math.pi/24) ))/2
    # Discrete modulation   : modulation = HOURLY_MODULATION_FACTORS[int((hour%24)*5)]
    modulation = HOURLY_MODULATION_FACTORS[int( (hour%24)*5 )]
    return modulation

def generate_time_modulated_weights(country_infos: Dict[str, Any]) -> Dict[str, float]:
    """
    Get time-modulated weights for each country based on the country's timezone.
    
    This function uses the country's timezone to modulate the weights of the countries.
    """
    # --- Step 1: Get the current hour ---
    current_hour = round(GLOBAL_TIMESTAMP_HOUR, 2)
    # --- Step 2: Get the country distribution and timezone ---
    country_distribution = country_infos.get("distribution", {})
    country_timezone = country_infos.get("timezone", {})
    country_distribution_modulated = country_infos.get("distribution_modulated", {})
    # --- Step 3: Generate the time-modulated weights ---
    country_distribution_modulated_sum = 0.0
    for country, weight in country_distribution.items():
        country_hour = current_hour + country_timezone[country]
        country_distribution_modulated[country] = weight * user_daily_activity_pattern(country_hour)
        country_distribution_modulated_sum += country_distribution_modulated[country]
    # --- Step 4: Return the time-modulated weights ---
    return country_distribution_modulated, country_distribution_modulated_sum

def get_weighted_choice(distribution: Dict[str, float]) -> str:
    """
    Select a key from a dictionary based on its weighted distribution.
    
    This function uses random.choices to select items based on their probability weights.
    The values in the dictionary should sum to 1.0 for proper probability distribution.
    
    Args:
        distribution: A dictionary where keys are the items to choose
                     and values are their probabilities (should sum to 1.0).
                     
    Returns:
        The chosen key based on weighted random selection.
        
    Raises:
        ValueError: If the distribution dictionary is empty.
        
    Example:
        >>> dist = {"A": 0.6, "B": 0.4}
        >>> get_weighted_choice(dist)
        "A"  # 60% chance
    """
    if not distribution:
        raise ValueError("Distribution dictionary cannot be empty")
    
    choices, weights = zip(*distribution.items())
    return random.choices(choices, weights=weights, k=1)[0]

def generate_event(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a single user interaction event based on the configuration.
    
    Creates realistic mock data for app store user interactions including app opens,
    searches, installs, reviews, in-app purchases, app closes, and uninstalls.
    The event structure follows a standardized format with configurable distributions
    for various attributes.
    
    Args:
        config: The loaded publisher configuration containing event type, device type,
               and country code distributions.
    
    Returns:
        A dictionary representing the user interaction event with the following structure:
        - event_id: Unique UUID for the event
        - event_timestamp: ISO8601 formatted timestamp
        - user_id: Unique UUID for the user
        - session_id: Unique UUID for the session
        - event_type: Type of interaction (app_open, search, app_install, review_submit, 
                     in_app_purchase, app_close, app_uninstall)
        - app_id: Random app identifier
        - device_type: Device type based on distribution
        - os_version: Operating system and version
        - country_code: Country code based on distribution
        - event_details: JSON string with event-specific details
        
    Example:
        >>> config = {"event_type": {"distribution": {"search": 0.5}}}
        >>> event = generate_event(config)
        >>> event["event_type"]
        "search"
    """
    global USERS_BY_COUNTRY, GLOBAL_TIMESTAMP_MICROS, GLOBAL_TIMESTAMP_HOUR, GLOBAL_RATE_MAXIMUM
    #########################################
    # --- Poisson distribution for events --- #
    #########################################
    dt_seconds = random.expovariate(GLOBAL_RATE_MAXIMUM)
    GLOBAL_TIMESTAMP_MICROS += int(dt_seconds*1_000_000)
    GLOBAL_TIMESTAMP_HOUR += dt_seconds/3600
    
    #########################
    # --- Country code --- #
    #########################
    country_infos = config.get("country_infos", {})
    country_distribution_modulated, country_distribution_modulated_sum = generate_time_modulated_weights(
        country_infos
    )
    # Thinning step: accept/reject an event!
    if random.random() > (country_distribution_modulated_sum/GLOBAL_RATE_MAXIMUM):
        return None
    country_code = get_weighted_choice(country_distribution_modulated)
    user_id = random.choice(USERS_BY_COUNTRY[country_code])

    #########################
    # --- Event type ---    #
    #########################
    event_type = get_weighted_choice(config.get("event_type", {}).get("distribution", {}))

    event_details_obj = {}
    if event_type == "search":
        event_details_obj["search_query"] = fake.bs()
    elif event_type == "review_submit":
        event_details_obj["rating"] = random.randint(1, 5)
    elif event_type == "in_app_purchase":
        event_details_obj["item_id"] = f"iap_{random.randint(100,999)}"
        event_details_obj["price_usd"] = round(random.uniform(0.99, 99.99), 2)

    #########################
    # --- Current timestamp --- #
    #########################
    current_timestamp = get_current_timestamp_micros()

    event = {
        "generation_timestamp": current_timestamp,
        "event_id": str(uuid.uuid4()),
        "event_timestamp": GLOBAL_TIMESTAMP_MICROS,
        "user_id": user_id,
        "session_id": fake.uuid4(),
        "event_type": event_type,
        "app_id": f"app_{random.randint(1000, 9999)}",
        "device_type": get_weighted_choice(config.get("device_type", {}).get("distribution", {})),
        "os_version": f"{random.choice(['iOS', 'Android'])} {random.randint(12, 15)}.{random.randint(0, 5)}",
        "country_code": country_code,
        "event_details": json.dumps(event_details_obj)
    }
    return event

def publish_messages_batch(project_id: str, topic_name: str, config: Dict[str, Any]) -> None:
    """
    Generate and publish messages to a Pub/Sub topic using automatic batching.
    
    This function continuously generates mock app store events and publishes them to
    the specified Google Cloud Pub/Sub topic. It uses the client library's automatic
    batching for optimal performance and handles publish callbacks for monitoring
    success/failure rates.
    
    The publisher will collect messages for up to 1 second or until 500 messages
    are collected, whichever comes first, before publishing the batch.
    
    Args:
        project_id: Google Cloud project ID where the Pub/Sub topic exists.
        topic_name: Name of the Pub/Sub topic to publish messages to.
        config: Publisher configuration containing event distributions and publishing settings.
               Expected to have 'generation_rate' key with 'events_per_second' and 
               'randomness_factor' for rate control.
    
    Raises:
        Exception: Catches and logs any unexpected errors during publishing.
        
    Note:
        This function runs indefinitely until interrupted. Use Ctrl+C to stop.
        The function will print status updates every 1000 published messages.
    """
    # --- Batching Settings ---
    # The publisher will collect messages for 1 second or until 500 messages
    # are collected, whichever comes first.
    batch_settings = pubsub_v1.types.BatchSettings(
        max_messages=500,
        max_latency=1,  # 1 second
    )
    publisher = pubsub_v1.PublisherClient(batch_settings)
    topic_path = publisher.topic_path(project_id, topic_name)

    print(f"Publisher starting for project '{project_id}' on topic '{topic_name}'.")
    print(f"Generating data based on profile: {config.get('description')}")
    print(f"Using automatic batching (max {batch_settings.max_messages} messages or {batch_settings.max_latency}s latency).")
    
    rate_config = config.get("generation_rate", {})
    base_rate = rate_config.get("events_per_second", 0)  # 0 means no rate control
    randomness = rate_config.get("randomness_factor", 0.1)
    
    # Callback for handling publish results
    published_count = 0
    failed_count = 0
    
    def callback(future: Future) -> None:
        """
        Handle the result of a publish operation.
        
        This callback is called when a message publish operation completes.
        It updates the success/failure counters and logs any errors.
        
        Args:
            future: The Future object representing the publish operation.
        """
        nonlocal published_count, failed_count
        try:
            # .result() will raise an exception if publishing failed.
            future.result()
            published_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to publish message: {e}")

    try:
        while True:
            # Generate a single event
            event_data = generate_event(config)
            if event_data is None:
                continue

            # Convert the dictionary to a JSON string (UTF-8 encoded bytes)
            data = json.dumps(event_data).encode("utf-8")

            # The publish() method is non-blocking. It returns a future.
            # The client library handles batching in a background thread.
            future = publisher.publish(topic_path, data)
            future.add_done_callback(callback)
            
            # Control the publishing rate
            if base_rate > 0:
                sleep_duration = (1 / base_rate) * (1 + random.uniform(-randomness, randomness))
                time.sleep(max(0, sleep_duration))
            else:
                time.sleep( 0.00225 )  # No more than 445 req/sec

            # Optional: print a status message periodically
            if published_count > 0 and published_count % 100_000 == 0:
                print(f"Published {published_count} messages so far...", flush=True)

    except KeyboardInterrupt:
        print(f"\nPublisher stopped by user. Total published: {published_count}, failed: {failed_count}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Total published: {published_count}, failed: {failed_count}")


def main() -> None:
    """
    Main entry point for the Pub/Sub Data Publisher.
    
    Parses command line arguments, loads the configuration file, validates
    required settings, and starts the message publishing process.
    
    Command Line Arguments:
        --config: Path to the publisher JSON configuration file (required).
    
    Configuration File Requirements:
        - gcp_project_id: Google Cloud project ID
        - pubsub_topic_name: Name of the Pub/Sub topic
        - event_type: Event type distribution configuration
        - device_type: Device type distribution configuration
        - country_infos: Country code distribution configuration
        - generation_rate: Rate control settings (optional)
        - description: Human-readable description of the data profile
    
    Example Configuration:
        {
            "gcp_project_id": "my-project",
            "pubsub_topic_name": "app-store-events",
            "event_type": {
                "distribution": {
                    "app_open": 0.4,
                    "search": 0.3,
                    "app_install": 0.15,
                    "review_submit": 0.05,
                    "in_app_purchase": 0.05,
                    "app_close": 0.04,
                    "app_uninstall": 0.01
                }
            },
            "device_type": {
                "distribution": {"phone": 0.8, "tablet": 0.15, "desktop": 0.05}
            },
            "country_infos": {
                "distribution": {"US": 0.3, "CA": 0.3, "IR": 0.4}
            },
            "generation_rate": {
                "events_per_second": 0,
                "randomness_factor": 0.2
            },
            "description": "Standard app store traffic profile"
        }
    
    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        json.JSONDecodeError: If the configuration file contains invalid JSON.
        SystemExit: If required configuration values are missing.
    """
    global GLOBAL_TIMESTAMP_MICROS, GLOBAL_TIMESTAMP_HOUR, GLOBAL_RATE_MAXIMUM

    parser = argparse.ArgumentParser(
        description="Pub/Sub Data Publisher for App Store Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 01_publisher_initial.py --config publisher_config.json
  python 01_publisher_initial.py --config /path/to/config.json
        """
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the publisher JSON configuration file.",
    )
    args = parser.parse_args()

    # Load publisher configuration
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {args.config}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {args.config}")
        return

    project_id = config.get("gcp_project_id")
    topic_name = config.get("pubsub_topic_name")

    if not project_id or not topic_name:
        print("Error: 'gcp_project_id' and 'pubsub_topic_name' must be set in the config file.")
        return

    # Initialize users by country
    # --- Step 1: Get the country distribution ---
    country_infos = config.get("country_infos", {})
    country_distribution = country_infos.get("distribution", {})
    country_infos['distribution_modulated'] = { country: 0.0 for country in country_distribution }
    # --- Step 2: Get the simulation parameters ---
    simulation_parameters = config.get("simulation_parameters", {})
    users_population_fraction = simulation_parameters.get("users_population_fraction", 0.001)
    gke_replicas_factor = simulation_parameters.get("gke_replicas_factor", 10)
    user_interactions_per_day = simulation_parameters.get("user_interactions_per_day", 57.0)
    user_interactions_per_second = user_interactions_per_day/(24*60*60)
    # --- Step 3: Initialize users by country ---
    print("--------------------------------")
    print("Initializing users by country...")
    keys = list(country_distribution)
    for country in keys:
        weight = country_distribution[country]
        n_users_in_country = int(weight * users_population_fraction / gke_replicas_factor)
        if n_users_in_country == 0:
            del country_distribution[country]
            continue
        USERS_BY_COUNTRY[country] = [fake.uuid4() for _ in range(n_users_in_country)]
        GLOBAL_RATE_MAXIMUM += n_users_in_country * user_interactions_per_second
        # Report
        print(f"Initialized {country}: {n_users_in_country} users")
    print("--------------------------------")
    print(f"GLOBAL_RATE_MAXIMUM: {GLOBAL_RATE_MAXIMUM}", flush=True)
    # Initialize global timestamp
    GLOBAL_TIMESTAMP_MICROS = get_current_timestamp_micros()
    GLOBAL_TIMESTAMP_HOUR = get_current_hour()
    # HARD-CODED CONTINUE FROM LAST BIGQUERY RECORD
    GLOBAL_TIMESTAMP_MICROS = 1760854441420750  # Last record: "2025-10-19 06:14:01.420750 UTC"
    GLOBAL_TIMESTAMP_HOUR = 6.233727986111111  # Based on time above

    # Start publishing messages
    publish_messages_batch(project_id, topic_name, config)

if __name__ == "__main__":
    main()
