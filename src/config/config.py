#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.



"""
This file contains some common constants relevant to statistics collecting.
"""

# Number related to stat data storage
n_jobs = 1                          # Number of jobs per day
n_months = 4                        # Number of months of data to store
n_days = 7                         # Number of days to use in a rolling stat
n_entries = n_jobs*n_days           # Number of entries needed to get n-day rolling stat
max_entries = n_jobs*7*4*n_months   # Max entries for n month storage

# Base oc.tc url
base_url = "https://oc.tc/"