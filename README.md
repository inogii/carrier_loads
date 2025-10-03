# 🚛 Carrier Loads Use Case

This use case leverage the HappyRobot platform to implement a carrier sales representative that negotiates directly with carriers in order to sell loads. 

## Features

- 📲 Built in tool to check the MC Number of the carrier who is calling
- 🖥️ Built in tool to check what loads are available in the system
- 💰 Negotiation mechanism so that the loads are sold taking margins into account. 

## Deployment

This use case has a hybrid deployment, including both an agent in the HappyRobot platform and some APIs in the cloud.

### 🚀 Step 1: Cloud API endpoint deployment

For this use case, the cloud vendor choice has been [fly.io](https://fly.io), since it has pretty affordable cloud deployments. For this reason, ensure you have flyctl installed in your environment. You can find more details on flyctl installation [here](https://fly.io/docs/flyctl/). The cloud endpoint can be easily deployed by running the following commands.

#### Carrier Loads Deployment

```
cd carrier_loads
```

```
flyctl launch
```

You can customize the type of cloud instance, but the minimal one will suffice for this endpoint.


### 🤖 Step 2: HappyRobot Agent Deployment

Once you have your API deployed in the cloud, it is time for us to deploy the agent in the HappyRobot Platform. 

Log into the HappyRobot Platform and follow the steps to deploy the agent:
- 1. Go to the workflows tab and create a new workflow
- 2. Click on upload file and upload the agent/carrier-sales-version-1.json file
- 3. Go to the FMCSA API Tool and change the default webkey value for the actual FMCSA webkey.
- 4. Once you succesfully import the file and make that change, publish it to production

That's it! You can now test your Carrier Sales representative agent by clicking on the play button in the upper right corner. Enjoy the negotiation!

## Feature Log

- Connecting the carrier_loads API to an actual database (PSQL or similar)
- Enhancing the agent by including optional parameters in the API call to the carrier loads search endpoint.




