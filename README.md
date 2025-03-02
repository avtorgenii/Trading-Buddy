# Trading-Buddy

Trading-Buddy is a minimalistic web-client for BingX crypto exchange Peprpetual Futures trading that allows for automatic:
- Posistion size calculation based on data for available deposit, risk(%) and available margin on your futures account
- Limit/take-profit/stop-loss orders placement and cancelation
- Track of your trades in Trade Journal

Read ```RULES_OF_USAGE.txt``` before using Trading-Buddy

# .env setup
- Create ```.env``` file in root directory of project and fill it out:
  ```
      API_KEY="<your API key that you get from BingX>"
      SECRET_KEY="<your Secret API key that you get from BingX>"
      PORT=<port, e.g. 8080>
      SITE_URL="http://<url that you get from VPS provider, is not required for local launching>"
  ```

# Local launching
After setting up .env file, head to ```main.py``` and run it, web-app will be available at ```127.0.0.1:<port>``` in your browser

# iPhone
Frontend of web-app has a configured ```site.webmanifest``` file that makes saved on homescreen site look like an IOS app, definitely check it out
