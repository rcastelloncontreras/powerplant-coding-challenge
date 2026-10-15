# Powerplant Production Plan API
REST API that calculates how much power each powerplant has to produce to match the load,
at the lowest possible cost and respecting the Pmin and Pmax of each powerplant.


## Requirements
- Python 3.8 or higher

## Installation
```
pip install -r requirements.txt
```

## How to run
Start the API on port 8888:

```
uvicorn api:api --host 0.0.0.0 --port 8888
```

The endpoint is available at:

```
POST http://localhost:8888/productionplan
```

It can be tested from the interactive documentation at `http://localhost:8888/docs`, using the payloads in the `example_payloads` folder.


## Project structure
- `algorithm.py`: production plan algorithm
- `api.py`: REST API (FastAPI) exposing the `/productionplan` endpoint
- `requirements.txt`: project dependencies


## Approach
### Objective
**Distribute the load between the powerplants so that:**
- The sum of the power produced equals the load.
- The cost is as low as possible.
- The Pmin and Pmax of each powerplant are respected.
- The values are multiples of 0.1 MW.

### Cost of each powerplant
- **Gas-fired and turbojet:** fuel price / efficiency (the efficiency is given as a decimal, e.g. 0.53).
- **Wind turbine:** cost 0.

### Power each powerplant can produce
- **Gas-fired and turbojet:** between Pmin and Pmax.
- **Wind turbine:** Pmax · wind / 100 (the wind is given as a percentage, e.g. 60).
  If it is used, it is used entirely.

### Algorithm
1. Sort the powerplants from cheapest to most expensive (merit order), starting with wind.
2. Add the next powerplant and check whether total load > accumulated load:
   - **Yes** → keep adding.
   - **No** → the current powerplant is switched on at its Pmin, and the previous one produces
     (total load − accumulated load before it) − Pmin of the current one.
3. Check that the previous powerplant is between its Pmin and Pmax.
   - **No** → try another option: the previous powerplant produces its maximum and the current one covers the rest.

### Algorithm details
- All powerplants start at 0, so the ones that are not needed are returned with 0.
- Once the load is covered, the algorithm stops.
- Values are rounded to one decimal (multiples of 0.1 MW).
- If the payload is not valid, the error is logged and the API returns an HTTP 500 error with the detail.


## Limitations and next steps
- **A lot of wind:** wind turbines cannot be partially used, so if they produce more than the load,
  this case is not covered yet.
- **When the previous powerplant cannot go down enough:** I decided to go for the cheapest and fastest
  approach, but this case is pending further study.
- **Greedy approach:** only the previous powerplant is adjusted, so the solution is not always the cheapest one.
- **First powerplant exceeding the load:** there is no previous powerplant to adjust, so this case is not handled.
- **Wind turbine as previous powerplant:** the adjustment could assign only part of its production,
  but wind turbines must be used entirely.
- **Load higher than the total available power:** no error is raised.
- **Input validation:** the payload is not validated; a missing field returns a generic error (500) instead of a clear one (400).
- **Not included:** CO2 cost, Docker and unit tests.