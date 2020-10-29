# Python code for Pizza Delivery

The whole objective here is that we have RabbitMq service bus. The orders are taken over an REST endpoint over a queue . This payload is picked up by the receiving client . 

Once received the client, it fake the order such that it gives a random time for order to be prepared (usinfg a rand function). Once waiting for x amount of time, we create another queue which sends over the order data saying that the order is prepared which is then picked up by the server .


## Requirements

```
Rabbitmq
Pika 
env
threading
```

We can create an environment using . This will make sure we are installing everything in an environment  

```
virtualenv env         
source env/bin/activate
```

## Code

Run the following in 2 seperate terminals 

    python3 index.py
    python3 receive.py


Example:

```
curl -X POST \
  http://127.0.0.1:5000/newOrder \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "type": "new",
    "user": {
        "name": "Raj",
        "lastName": "Singh",
        "address": "<>"
    },
    "order":{
        "pizzaType": "veggie",
        "quantity":1,
        "price":16.99,
        "notes":"something"
    }
}'
```

the following will be received on the client as following 

```
 [x] Awaiting RPC requests
New order received for : Raj
Order received at : 15:56:45
Estimated wait time : 23mins
```


The server will wait an x amout of time before it publishes the data that the order is ready to be picked up.

The status of the order can be checked by this curl command
```
curl -X GET \
  http://127.0.0.1:5000/getStatus \
  -H 'cache-control: no-cache'

  ```

the result of which will be seen on the client side as 


```Order Ready to Pickup : 2a137d11-5350-48c1-b44a-2fe81c547a4c for: Raj at 15:57:15```

ToDo:

This all can be integrated into a UI where we can check the status of an order based on what the type is 

