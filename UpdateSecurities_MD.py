#!/usr/bin/env python
# Python script to be run in Moneydance to perform amazing feats of financial scripting

# Set to your API key with alphavantage.co
apikey = 'YOUR_API_KEY_GOES_HERE'

# initialize lists used for security data
mapCurrent = []
mapDates = []
mapAccounts = []

try:
  import ssl
except ImportError:
  message = "error: no ssl support"
  print message;

from com.infinitekind.moneydance.model import *
from urllib2 import Request, urlopen, URLError, HTTPError
import json
import sys
import time

# Shamelessly copied from moneydance developer page and modified for my own evil purposes
def setPriceForSecurity(currencies, symbol, price, high, low, volume, dateint):
  #print 'setting price for ' + symbol + ': $' + str(price) 
  price = 1/price
  security = currencies.getCurrencyByTickerSymbol(symbol)
  if not security:
    #print "No security with symbol/name: %s"%(symbol)
    return
  if dateint:
    snapsec = security.setSnapshotInt(dateint, price)
    snapsec.setUserDailyHigh(1/high)
    snapsec.setUserDailyLow(1/low)
    snapsec.setDailyVolume(volume)
    snapsec.syncItem()    
  security.setUserRate(price)
  security.syncItem()  
  #print "Successfully set price for %s"%(security)

def setPriceForCurrency(currencies, symbol, price, dateint):
  #print 'setting price for ' + symbol + ': $' + str(price) 
  price = 1/price
  currency = currencies.getCurrencyByIDString(symbol)
  if not currency:
    #print "No security with symbol/name: %s"%(symbol)
    return
  if dateint:
    snapsec = currency.setSnapshotInt(dateint, price)
    snapsec.syncItem()    
  currency.setUserRate(price)
  currency.syncItem()  
  #print "Successfully set price for %s"%(currency)

def loadAccounts(parentAcct):
   # This function is a derivative of Mike Bray's Moneydance 2015 Security Price Load module (LoadPricesWindow.java) code and has been modified to work in python
   # Original code located here: https://bitbucket.org/mikerb/moneydance-2015/src/346c42555a9ec4be2b05ef5c4469e183135db4cc/src/com/moneydance/modules/features/securitypriceload/?at=master
   # Get list of accounts to iterate through
   sz = parentAcct.getSubAccountCount();
   i = 0
   for i in xrange(0,sz):
      acct = parentAcct.getSubAccount(i)
      if acct.getAccountType() == parentAcct.AccountType.valueOf("SECURITY") :
         #curBal = str(acct.getCurrentBalance());
         #print 'Balance: ' + curBal;
         if(acct.getCurrentBalance() != 0 ):
           ctTicker = acct.getCurrencyType();
           #print ctTicker;
           if (ctTicker != None):
               if (ctTicker.getTickerSymbol() != ''):
                  listSnap = ctTicker.getSnapshots();
                  iSnapIndex = listSnap.size()-1;
                  if (iSnapIndex < 0):
                     #print ctTicker.getTickerSymbol();
                     mapCurrent.append((ctTicker.getTickerSymbol(), 1.0, ctTicker.getName()));
                     mapDates.append((ctTicker.getTickerSymbol(),0));
                     mapAccounts.append((ctTicker.getTickerSymbol(),acct));
                  else:
                     ctssLast = listSnap.get(iSnapIndex);
                     if (ctssLast != None):
                          #print ctTicker.getTickerSymbol();
                          mapCurrent.append((ctTicker.getTickerSymbol(),1.0/ctssLast.getUserRate(),ctTicker.getName()));
                     mapDates.append((ctTicker.getTickerSymbol(), ctssLast.getDateInt()));
                     mapAccounts.append((ctTicker.getTickerSymbol(), acct));
      loadAccounts(acct);

def buildUrl(func, symbol, apikey):
    # Creates url used for JSON quote return
    # Visit www.alphavantage.co to obtain a free api key
    url = 'https://www.alphavantage.co/query?function=' + func + symbol + '&outputsize=compact&apikey=' + apikey;
    return url;

def getLastRefreshedTimeSeries(func, symbol, apikey):
    url = buildUrl(func, symbol, apikey);
    req = Request(url);
    #print url;
    # Attempt to open the URL, print errors if there are any, otherwise read results 
    try: 
       resp = urlopen(req);
       #print 'response headers: "%s"' % resp.info();
       content = resp.read().decode().strip();
    except IOError, e:
       if hasattr(e, 'code'): # HTTPError
           message = 'http error code: ', e.code;
           print message
       elif hasattr(e, 'reason'): # URLError
           message = "can't connect, reason: ", e.reason;
           print message
           print e;
       else:
           content = resp.read();
           raise;
    # read results, decode, and remove extra spaces
    
    # convert from JSON data to Python dict and return to calling program
    return json.loads(content);

# Iterate through symbols here:

root=moneydance.getCurrentAccountBook()
ra = root.getRootAccount() 

#'''  Skip imports for now

loadAccounts(ra)

x = 0
for security, sDate, acct in zip(mapCurrent, mapDates, mapAccounts):
   symbol = security[0];
   name = security[2];
   func = 'TIME_SERIES_DAILY&symbol='

   if len(symbol) <=11 and '/' not in symbol:  # ignore known security issues
     #print '{0} Security {1}: ${2}.'.format(sDate[1],symbol,security[1]);
     #print 'Getting quote if a valid security...';

     # Set recentQuoteDate to the last security updated date just in case getQuote fails
     recentQuoteDate = sDate[1];
     override = False; # used to add quote information even if data for date already exists
     skip = False;
     try:
       getQuote = getLastRefreshedTimeSeries(func, symbol, apikey);
       recentQuoteDate = str(getQuote['Meta Data']['3. Last Refreshed'])[:10];
       high = float(getQuote['Time Series (Daily)'][recentQuoteDate]['2. high']);
       low = float(getQuote['Time Series (Daily)'][recentQuoteDate]['3. low']);
       close = float(getQuote['Time Series (Daily)'][recentQuoteDate]['4. close']);
       volume = long(float(getQuote['Time Series (Daily)'][recentQuoteDate]['5. volume']));
     except:
       print 'Security {0} ({1}): Invalid ticker symbol'.format(name,symbol);
       skip = True;

     if (recentQuoteDate != sDate[1] or override) and not skip:
        part = recentQuoteDate.split("-");
        lastRefreshDate = part[0]+part[1]+part[2];
        lastRefreshDate = int(lastRefreshDate);
        setPriceForSecurity(root.getCurrencies(), symbol, close, high, low, volume, lastRefreshDate);
        setPriceForSecurity(root.getCurrencies(), symbol, close, high, low, volume,0);
        print 'Security %s (%s): $%s - updated on %s: $%s  ( H:$%s, L:%s, V:%s )'%(name,symbol,security[1],recentQuoteDate,close,high,low,volume);
        skip = False;

# Update all currencies we can find with most recent currency quote
func = 'CURRENCY_EXCHANGE_RATE&to_currency=USD&from_currency='
#func = 'DIGITAL_CURRENCY_DAILY&market=USD&symbol='
currencylist = root.getCurrencies().getAllCurrencies()
x = True;
for currency in currencylist:
  if (currency.getCurrencyType() == currency.getCurrencyType().valueOf("CURRENCY")):
   symbol = currency.getIDString();
   name = currency.getName();
   #print 'Updating ' + name + ' (' + symbol + ')'
   try:
      getCurrency = getLastRefreshedTimeSeries(func, symbol, apikey);
      recentCurrencyDate = str(getCurrency['Realtime Currency Exchange Rate']['6. Last Refreshed'])[:10];
      close = float(getCurrency['Realtime Currency Exchange Rate']['5. Exchange Rate']);
      part = recentCurrencyDate.split("-");
      lastRefreshDate = part[0]+part[1]+part[2];
      lastRefreshDate = int(lastRefreshDate);
      setPriceForCurrency(root.getCurrencies(), symbol, close, lastRefreshDate)
      setPriceForCurrency(root.getCurrencies(), symbol, close, 0)
      print 'Currency %s (%s) - updated on %s: $%s'%(name,symbol,recentQuoteDate,close);
   except:
      print 'Currency %s (%s) - Invalid currency'%(name,symbol);
      skip = True;

   time.sleep(2);  # breathe...it's a free API, don't overwhelm
