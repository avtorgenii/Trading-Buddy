# Trading-Buddy

Trading-Buddy is a minimalistic web-client for BingX crypto exchange Peprpetual Futures trading that allows for automatic:
- Posistion size calculation based on data for available deposit, risk(%) and available margin on your futures account
- Limit/take-profit/stop-loss orders placement and cancelation
- Track of your trades in Trade Journal

Read ```RULES_OF_USAGE.txt``` before using Trading-Buddy

# Showcase 

You can check how web app looks [here](http://165.232.125.83:8079). Though you wouldn't be able see opened positions on exchange site(for this launch app with your own API keys), it should give you idea how does app look like and what it can do

# .env setup
- Create ```.env``` file in root directory of project and fill it out:
  ```
      API_KEY="<your API key that you get from BingX>"
      SECRET_KEY="<your Secret API key that you get from BingX>"
      PORT=<port, e.g. 8080>
      SITE_URL="http://<ipv4 address that you get from VPS provider, no need for it for local launching>"
  ```

# Local launching
After setting up .env file, head to ```main.py``` and run it, web-app will be available at ```127.0.0.1:<port>``` in your browser

# Deploy to VPS
Trading-Buddy comes with complete Dockerfile that should be used to build your image and deployed to VPS, personally I am using https://digitalocean.com to host web-app.
I am not providing a link to Image on dockerhub, as for now it requires IP address of VM to be able to send requests to itself from backend, so the image and ```.env``` file should be created by you

Use
```docker build -t <docker_nickname>/trading-buddy:1.0 .``` 
in project root folder to build image

And
```docker push <docker_nickname>/trading-buddy:1.0```
to push image to dockerhub

Then setup VPS on Digital Ocean according to this video: https://www.youtube.com/watch?v=8fi4NvaZpFc&list=WL&index=52

Pull image from dockerhub: ```docker pull <docker_nickname>/trading-buddy:1.0```

And run by ```docker run -p <port>:<port> --name trading-buddy <docker_nickname>/trading-buddy:1.0```

Enter ```<ipv4>:<port>``` in browser and enjoy!

# iPhone
Frontend of web-app has a configured ```site.webmanifest``` file that makes saved on homescreen site look like an IOS app, definitely check it out
