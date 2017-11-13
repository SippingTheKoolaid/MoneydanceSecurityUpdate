# Moneydance Security Update
Tired of waiting for the update from the Moneydance team to address issues with Yahoo finance API being terminated, I embarked on a means to update this myself.  I am sharing my solution for anyone brave enough to try it.  I take no responsibility for any damage to your data through the use, or mis-use of these instructions and published scripts.

Using the Moneydance Developer API and shamelessly "borrowing" published coding ideas from a variety of individuals, this is the ugly Python script I pulled together to update Moneydance securities AND currency rates.  The goal was a quick solution, not a finely designed application with a front-end.  

## Security & Currency quote retreval
This script uses the free API provided by AlphaVantage (www.alphavantage.co).  You sign up and they provide an apikey that can be passed on command-line, no additional authentication required.

I also used Intrinio (https://intrinio.com/) which requires basic authentication, but went with AlphaVantage due to ease of implementation and support for both currency rates and securities.  The script could be better designed to support a number of the free services, if anyone is so inclined.

## SSL & Jython in Moneydance
In testing various script solutions, I realized the current version of jython in Moneydance 2017 has issues with SSL.  Python scripts would run fine and retrieve security information through both AlphaVantage and Intrinio APIs when run outside Moneydance, but when running through the Python interpreter in Moneydance they would fail with a variety of connectivity errors usually SSL related.  

Errors were similar to:
("can't connect, reason: ", SSLError(1, u'Received fatal alert: internal_error'))
<urlopen error [Errno 1] Received fatal alert: internal_error>

To work around the issues, I tried accessing the APIs using different libraries: urrlib2, requests.  None worked reliably, but error messages were more descriptive using requests and made Jython version issues clearly the problem.  Everything I read indicated issues with netty & SSL were common for older versions of Jython.  Calls through the Intrinio API would occassionally work (same call would be successful one out of every 4-5 executions), so I was originally planning to just deal with it.  Then I had a different thought.

I found the most recent bleeding-edge release of Jython had been published and had addressed a number of SSL issues.  I downloaded it and tried with Moneydance - SSL errors disappeared.

### Danger, Danger, Will Robinson
So here's where anyone implementing this solution needs to decide if getting updates to securities and currency RIGHT NOW is worth making a tweak to their environment that is not fully vetted, and likely unsupported, by Moneydance.  I have had no issues with the solution, and made sure to backup my md files before trying this.  You should, at a minimum, make back-ups of your Moneydance program directory, of your Moneydance data files, and have a general understanding of how you would restore to original setup should something go wrong.  If you proceed with the solution I implemented in my environment, I accept no liability for any damages.  These were the steps I took to implement, your paths and files may vary.

#- Download the latest Jython jar:  http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.1-rc3/jython-standalone-2.7.1-rc3.jar

In your Moneydance program directory (i.e. C:\Program Files\Moneydance), rename the following files to \*.old :
*C:\Program Files\Moneydance\jars\MDPython.jar
C:\Program Files\Moneydance\jars\cachedir\packages\MDpython.pkc*
#- Copy jython-standalone-2.7.1-rc3.jar to C:\Program Files\Moneydance\jars\MDPython.jar

Other details about 2.7.1-rc3 can be found here: http://fwierzbicki.blogspot.com/2017/06/jython-271-release-candidate-3-released.html

