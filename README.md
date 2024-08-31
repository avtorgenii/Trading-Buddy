# Trading-Buddy

Trading-Buddy is a minimalistic web-client for BingX crypto exchange Peprpetual Futures trading that allows for automatic:
- Posistion size calculation based on data for available deposit, risk(%) and available margin on your futures account
- Limit/take-profit/stop-loss orders placement and cancelation
- Track of your trades in Trade Journal

# Setup
Trading-Buddy comes with complete Dockerfile that should be used to build your image and deployed to VPS, personally I am using https://digitalocean.com.
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
