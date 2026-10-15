############ LIBRARIES  ############
import json






############ READ PAYLOAD ############
with open("example_payloads/payload3.json") as f:
    payload = json.load(f)



############ VARIABLES  ############
total_load = payload['load']
powerplants = payload['powerplants']
fuels = payload['fuels']




############ COST CALCULATION ############
for powerplant in powerplants:
    if powerplant['type'] == 'gasfired':
        cost = fuels['gas(euro/MWh)'] / powerplant['efficiency']
    elif powerplant['type'] == 'turbojet':
        cost = fuels['kerosine(euro/MWh)'] / powerplant['efficiency']
    else: 
        cost = 0
    
    powerplant['cost'] = cost


############ AVAILABLE PMAX ############
for powerplant in powerplants:
    if powerplant['type'] == 'windturbine':
         powerplant['pmax_available'] = powerplant['pmax'] * fuels['wind(%)'] / 100
    else:
        powerplant['pmax_available'] = powerplant['pmax'] 


############ SORT BY COST ############
# sort by cost (cheapest first): if same cost, bigger pmax_available first
powerplants.sort(key=lambda powerplant: powerplant['cost'])




############ POWER CALCULATION ############
accumulated_load = 0

# all powerplants start at 0
for powerplant in powerplants:
    powerplant['p'] = 0

for i, powerplant in enumerate(powerplants):

    # Add powerplant with less cost
    accumulated_load = accumulated_load + powerplant['pmax_available']

    #check CT > CA: add next plant
    if total_load > accumulated_load:
        powerplant['p'] = round(powerplant['pmax_available'], 1)

    #check CT <= CA: this powerplant completes the load
    else:
        previous_powerplant = powerplants[i - 1]

        # accumulated load before the previous powerplant
        accumulated_load_before_previous = (
            accumulated_load - powerplant['pmax_available'] - previous_powerplant['pmax_available']
        )

        # P previous = (total load - accumulated load before previous) - Pmin current
        previous_powerplant['p'] = round((total_load - accumulated_load_before_previous) - powerplant['pmin'], 1)

        # current powerplant at its Pmin
        powerplant['p'] = powerplant['pmin']

        # Check P previous: Pmin <= P <= Pmax
        if previous_powerplant['pmin'] <= previous_powerplant['p'] <= previous_powerplant['pmax_available']:
            print('Check OK:', previous_powerplant['name'], 'within its limits')

        # No? -> try another option: previous at its max, current covers the rest
        else:
            previous_powerplant['p'] = round(previous_powerplant['pmax_available'], 1)
            powerplant['p'] = round(total_load - (accumulated_load - powerplant['pmax_available']), 1)

            # check the current powerplant can produce that amount
            if powerplant['p'] < powerplant['pmin']:
                print('WARNING: no valid solution found with this approach')


        break  


############ RESULTS ############
print('Power of each powerplant:')
for powerplant in powerplants:
    print(powerplant['name'], '-->', powerplant['p'])

total_produced = sum(powerplant['p'] for powerplant in powerplants)

if round(total_produced, 1) == total_load:
    print('Total load completed:', total_produced)
else:
    print('Total load NOT completed:', total_produced, 'of', total_load)