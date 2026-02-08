Aerospike Rule Template
This document provides the standardized template and guidelines for contributing new health check rules to the Aerospike Health and Performance Report. Following this template ensures that your rule integrates seamlessly with the automated reporting engine.

Rule Python Template
Use the following structure for your rule file (e.g., `rules/your_check_name.py`).

```

import sqlite3

import pandas as pd

# --- Metadata ---

# ID: {X.y} (e.g., 5.a)

# Title: Descriptive Name

def run_check(db_path="aerospike_health.db"):

    """

    Executes the health check against the local SQLite database.

    

    Returns:

        dict: {

            "id": str,          # The unique identifier (e.g., "5.a")

            "name": str,        # The display name of the rule

            "status": str,      # PASS, WARNING, CRITICAL, or ⚠️ DATA MISSING

            "message": str,     # Human-readable findings

            "remediation": str  # Specific steps to resolve the issue

        }

    """

    # 1. Establish Connection

    conn = sqlite3.connect(db_path)

    

    try:

        # 2. Query Logic

        # Example: query = "SELECT value FROM node_stats WHERE metric = 'your_metric'"

        # df = pd.read_sql_query(query, conn)

        

        # 3. Handle Missing Data

        # if df.empty:

        #     return {

        #         "id": "X.y",

        #         "name": "Template Rule",

        #         "status": "⚠️ DATA MISSING",

        #         "message": "The required telemetry was not found in the bundle.",

        #         "remediation": "Instruct user which asadm command to run."

        #     }

        

        # 4. Evaluate Health

        # status = "PASS"

        # message = "Everything looks good."

        

        return {

            "id": "X.y",

            "name": "Your Rule Name",

            "status": "PASS",

            "message": "Check completed successfully.",

            "remediation": "Optional: Steps to follow if status is not PASS."

        }

        

    except Exception as e:

        return {

            "id": "X.y",

            "name": "Your Rule Name",

            "status": "CRITICAL",

            "message": f"An error occurred: {str(e)}",

            "remediation": "Review logs and database schema."

        }

    finally:

        conn.close()

```

Contribution Guidelines
1. Return Schema: Every rule must return a dictionary with keys: `id`, `name`, `status`, `message`, and `remediation`.

2. Error Handling: Use `try...except...finally` to ensure the reporting engine continues running even if a specific rule fails.

3. Read-Only: Rules should only read from the database.

Status Levels
