# Moneydance Security Update
Tired of waiting for the update from the Moneydance team to address issues with Yahoo finance API being terminated, I embarked on a means to update this myself.  I am sharing my solution for anyone brave enough to try it.  I take no responsibility for any damage to your data through the use, or mis-use of these instructions and published scripts.

Using the Moneydance Developer API and shamelessly "borrowing" published coding ideas from a variety of individuals, this is the ugly Python script I pulled together to update Moneydance securities AND currency rates.  In testing various script solutions, it was determined the current version of jython in Moneydance 2017 has issues with SSL.  Python scripts would run fine and retrieve security information when run outside Moneydance, but when running through the Python interpreter in Moneydance they would fail with a connectivity error.


## Security & Currency quote retreval
This script uses the free API provided by www.alphavantage.co, but could be better designed to support a number of the free services, if someone wanted to take the time.
