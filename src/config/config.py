"""
This file contains some common constants relevant to statistics collecting.
"""

# Number related to stat data storage
n_jobs = 4                          # Number of jobs per day
n_months = 4                        # Number of months of data to store
n_days = 7                         # Number of days to use in a rolling stat
n_entries = n_jobs*n_days           # Number of entries needed to get 2-week rolling stat
max_entries = n_jobs*7*4*n_months   # Max entries for n month storage
# Base oc.tc url
base_url = "https://oc.tc/"