# Global stuff

# Number related to stat data storage
n_jobs = 48                          # Number of jobs per day
n_months = 2                        # Number of months of data to store
n_days = 14                         # Number of days to use in a rolling stat
n_entries = n_jobs*n_days           # Number of entries needed to get 2-week rolling stat
max_entries = n_jobs*7*4*n_months   # Max entries for n month storage

# Base oc.tc url
base_url = "https://oc.tc/"