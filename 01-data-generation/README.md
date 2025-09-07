# 01) Data Generation

In this section, I'll explain how the _scalable real-world synthetic data generation_ works. Here is a breakdown of what it means:

- **Scalable:** I'll use containerization to create a Docker image, then deployed on a configured Kubernetes cluster, to easily increase data generation throughput, e.g. increase number of running containers.
- **Real-world:** World population data [1] is multiplied by each country's internet penetration factor [2] to generate a _potential users_ number, which then is converted to _request generation rate_. Rates are further modulated by time-zone for each country [4], as well as a 24-hour/day-night activity pattern.
- **Synthetic data generation:** Since the rate of change is variable through time, a _Non-homogeneous/Time-varying Poisson Process Simulation_ method is used to accurately simulate real-world behavior.

Checkout the dashboard for data generate rates here at project's the public **Metabase dashboard**: [📊 Metabse: Request Genration Stats](https://sinras-app-store-simulation.metabaseapp.com/public/dashboard/bdebe992-02cc-420b-a352-76efefa9dd4a)



> Recommendation: Keep a file with all the relevant information about your project as well as useful bash scripts. You will get back to them a lot! 😉  
> Example file `environment_variables_and_scripts.sh` on project page.  
> p.s.: A practice is the use of credentials and environment variables managed in your shell or through a manager during run-time, but let's start simple for a showcase project. 😉



## Step 1: Containerized environment
Now let's create a fully functional machinary capable of:

- **Running in a container:** We need to create a proper Docker image with all the required tools and packages. While making sure it's flexible enough, e.g. the python script is loaded from a GCS bucket for full flexibility of code updates.

- **Publishing to Pub/Sub topic in batches [3]:** Make sure the python script is able to communicate the the _Pub/Sub topic_ of the project and does utilize the GCP's batch publish settings.




### Step 1.1: Docker image
You will do the following:
- Create an image with proper operating system, python version (e.g. latest stable), creates a virtual environment, and installs required python packages inside
- This image is then published to `AR_REPO`, with tag given by `IMAGE_TAG`, so it will be available to other GCP services, e.g. Google Kubernetes Engine (GKE) clusters.


First upload the `01-data-generation/Dockerfile` file to your Cloud Shell session storage. This will make it accessible for upcoming commands.


Then create/push Docker images on your `Google Cloud Platform`'s `Artifact Registry`/`Image Registry` service that hosts your docker images, by running:
```bash
export IMAGE_TAG=${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/publisher:v1
docker build -t ${IMAGE_TAG} .
docker push ${IMAGE_TAG}
```
where `REGION`, `PROJECT_ID` and `AR_REPO` (Artifact Registry Reposity path) are retrieved from your GCP infos.


### Step 1.2: Upload to Google Cloud Storage (GCS)

Make sure to create a bucket in `Google Cloud Storage (GCS)`, and upload these two files after renaming them.
- `00_publisher_config.json` -> `publisher_config.json` and write the path down (from details section) for future use.
- `01_publisher_initial.py` -> `publisher.py` and write the path down (from details section) for future use.

This will make these files accessible to all the container instances in the GKE, ensuring the latest version of configurations and codes are downloaded from GCS and executed.
> This way you won't need to re-create a docker image with hard-coded python script and config file, when you make a change.

### Step 1.3: Create a Google Kubernetes Engine (GKE) cluster
This step will create a cluster in GKE which allows scalable execution of the Docker image we made in step (1.1). Also we determine the command to be run in the docker image, e.g. download the python script file from GCS and execute it.


You will create an account named `publisher-ksa`, and grant it proper access so it can 1) publish to `Pub/Sub service`, 2) download files from `GCS buckets`, and 3) grant identity access from `GSA account` for container execution. Finally introduce the new account `publisher-ksa`, with proper linking annotation, to the `GKE`.

```bash
# 1. Create a Kubernetes Service Account (KSA)
kubectl create serviceaccount publisher-ksa

# 2. Create a Google Service Account (GSA)
gcloud iam service-accounts create publisher-gsa \
  --display-name="AppStore Publisher GSA"

# 3. Grant the GSA the necessary permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:publisher-gsa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:publisher-gsa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# 4. Link the GSA and KSA together
gcloud iam service-accounts add-iam-policy-binding \
  publisher-gsa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[default/publisher-ksa]"

# 5. Annotate the KSA to complete the link
kubectl annotate serviceaccount publisher-ksa \
  iam.gke.io/gcp-service-account=publisher-gsa@${PROJECT_ID}.iam.gserviceaccount.com
```

Now the proper access levels for your GKE cluster has been defined! 🎉  
It's time to run the cluster with `replicas=0` (essentially initializing the cluster but start any containers yet).

Before continuing, make sure to change the parameters inside this YAML file according to your project, `01-data-generation/publisher-deployment.yaml`. E.g. 

Use the file `01-data-generation/publisher-deployment.yaml` in your Cloud Shell, and following commands:
```bash
kubectl apply -f publisher-deployment.yaml  # Initialize/update the cluster with configurations inside the file
kubectl scale deployment appstore-publisher-deployment --replicas=0  # To stop all the containers/pods. But still keep the cluster running
kubectl scale deployment appstore-publisher-deployment --replicas=4  # Set number of running instance of the containers/pods to 4.
kubectl get pods  # Get list and status of all active pods.
kubectl logs <container/pod-name>  # Get the log from a specific container/pod
kubectl delete -f publisher-deployment.yaml  # Stop all containers/pods and remove the cluster. NOTICE! you will need to initialize the cluster again and it takes some time! If you just need to stop execution, use `--replicas=0` option like above line.
```

### Step 1.4: Congratulations! 🎉

Congratulations! You now have everything ready to start the request generation process!

Before continuing these steps, you need to configure the `Google Pub/Sub` service that will receive the messages, and also use it's proper address/IDs in the `00_publisher_config.json` and `publisher-deployment.yaml` for scripts to send their requests to.

Please go to Guide in `02-data-ingestion` section, setup the `Google Pub/Sub` topic and subscription, make sure to use the information about the subscriptions to update the `00_publisher_config.json` and `publisher-deployment.yaml` and apply them (e.g. upload the `00_publisher_config.json` again and run `kubectl apply -f publisher-deployment.yaml` with the new settings.)


After doing that and making sure all the steps in this guide from step (1.1) till step (1.4) are working, move to the next step.

### Step 1.5: Run the codes and scale infinitely!!!! (just joking 😅)

Not it's time to increase the replications in the GKE cluster, and see if the containers/pods are working as intended. For example increase replications to `4` (four copies of the python script running).
```bash
kubectl scale deployment appstore-publisher-deployment --replicas=4  # Set number of running instance of the containers/pods to 4.
```

Checkout `Google Pub/Sub`'s subscription metrics and see if requests are getting there, e.g. either getting stuck there unacknowledged or being processed if you have setup the processing part (pulling from the topic).
> If all is good, let's move to the next step! 🥳


## Step 2: Enhance data generation

In this section, we will incrementally improve upon the data generation process to make it more realistic and challenging (I mean fun 😄).

### Step 2.1: Modulate requests by real-world data

Combine the data in the sources ([1], [2], and [4]) to get a table like this:
| Country | Population | InternetPenetrationFraction | Timezone |
|:-------:|-----------:|:---------------------------:|---------:|
| IND | 1,463,865,525 | 0.56 |  2.0 |
| CHN | 1,416,096,094 | 0.77 |  4.5 |
| USA |   347,275,807 | 0.93 | -7.5 |
| IDN |   285,721,236 | 0.69 |  3.5 |
| ... | ... | ... | ... |

> Hints: you can use `pd.read_html(url)` to load all the tables in a page directly, and select the relevant one in each website. Then use some data clearning to make country names comparable. Finally merge all together and select those columns. 🪄

> Hint 2: I've already done it and you can use the notebook or the CSV file in this folder. 😄

> Hint 3: Yes, you can ask any of the common LLMs/chatbots/AI-buddies/... to make the table for you. 👍

Now update the `publisher_config.json` file "country_infos" section and add the "Population*InternetPenetrationFraction" as country weights, e.g.
```json
{
  // ...
  "country_infos": {
    "distribution": {
      "IND":  819764694.00,
      "CHN": 1090393992.38,
      "IR": 73934144.80,
      // ...
    }
  },
  // ...
}
```

Next step is to add a simple time modulation based on 24-hour cycles. This looks not too bad (we will replace this with a more realistic curve estimated from real-data later):

$$
factor = 0.03 + 0.97 \times \frac{1}{2} \left(
  1 + \cos( (HOUR-16) * (2* \pi /24) )
\right)
$$

> Essentially a 24-hour cyclic increase and decrease of activity, with peak being around 4:00 PM and lowest around 4 AM.

Now use the updated code and config files to run the request generation again.
- Copy and rename files `02_publisher_modulated.py` -> `publisher.py` and the config.
- Upload to GCS, overwrite files to they are accessible at the same paths.
- Change GKE replicas to 0, and then to 4 (for example), to terminate and for containers/pods to download new python scripts and configs.


_Et voilà! 🎉 You have the distribution of requests based on real-world population, internet penetration, timezone, and 24h cycles!_

> Notice: The `rate of request generation` is not actually changed here! We only make the distribution of countries that appear, to match those modulation factors mentioned. Still not a Non-homogenous Poisson! This process is similar to a "fixed rate Poisson process (assuming pods generate events at a fixed rate), where the contribution of countries changes over time, but always add to a fixed total rate."

### Step 2.2: Keep track of users 📔

Now let's use the file `01-data-generation/03_publisher_modulated_users.py`. For each country, a fixed set of `user_id`s is generated once, and each container/pod will have it's own set of fixed users. Whenever an event happens in each country, a random `user_id` is selected from that list.

To make it more reliable and scalable, each container will only keep track of a fraction of total users available and generate request for that subset. This ensures each pod can remain whithin memory and CPU limits of a cluster.

### Step 2.3: Non-homogeneous Poisson 🎣

Now let's use the new file for an actual **non-homogeneous Poisson Process Simulation**. Read through it `01-data-generation/04_publisher_modulated_users_Poisson.py` for implementation details, but here are the key things about it:

- **Estimate Maximum Rate:** I use the total population and internet penetration factor to estimate a maximum event generation rate

- **Thinning Method:** Generate an exponential sample from the _maximum rate_, accept it based on daily patterns of each country and their populations.

- **Global Time:** Global time starts from the beginning of the simulation and advances based on Poisson process simulation, making it advance much faster.

### Step 2.3.5: Manage my budget 💰

Running this script on GCP costs money, and the most expensive step so far has been request generation. So I limited the rate of request generation (keeping the simulation time untouched), to pay much less and make it personally managable to pay for. 🥲

The file that applies these changes and resumes from the last simulation timestamp (hard-coded since I don't wanna do this often) is `01-data-generation/05_publisher_modulated_users_Poisson_throttled.py`.

### [Writing in Progress] Step 2.4: Event faster? 🏎

> Even faster with discretization and uniform selection -> one shot, many events.

> Use the shuffling trick to speed up things don't generate new things! -> both for users and cases and all.








[1]: https://www.worldometers.info/world-population/population-by-country
[2]: https://data.worldbank.org/indicator/IT.NET.USER.ZS
[3]: https://cloud.google.com/pubsub/docs/batch-messaging
[4]: https://www.timeanddate.com/worldclock/?low=c&sort=1
