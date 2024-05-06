import asyncio
from flask import Flask, request, jsonify
from prisma import Client
from math import sin, cos, sqrt, atan2, radians

app = Flask(__name__)
prisma = Client()

# Approximate radius of earth in km
R = 6373.0


async def setup():
    # Connect Prisma client
    await prisma.connect()

# Explicitly call the setup function to connect Prisma


async def connect_to_database():
    await setup()

# Before the first request, connect to the database


async def before_first_request():
    await connect_to_database()


@app.route('/closest_food_trucks', methods=['GET'])
async def closest_food_trucks():
    # Get latitude and longitude from the request
    lat = radians(float(request.args.get('latitude')))
    lon = radians(float(request.args.get('longitude')))

    # Fetch all food trucks from the database
    food_trucks = await prisma.trucks.find_many()

    # Calculate distances and sort
    food_trucks_with_distance = []
    for truck in food_trucks:
        truck_lat = radians(truck.latitude)
        truck_lon = radians(truck.longitude)
        dlon = truck_lon - lon
        dlat = truck_lat - lat
        a = sin(dlat / 2)**2 + cos(lat) * cos(truck_lat) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        food_trucks_with_distance.append({'id': truck.id, 'name': truck.name, 'distance': distance})

    # Sort food trucks by distance
    sorted_food_trucks = sorted(food_trucks_with_distance, key=lambda x: x['distance'])

    # Return the five closest food trucks
    closest_food_trucks = sorted_food_trucks[:5]

    return jsonify(closest_food_trucks)

if __name__ == '__main__':
    asyncio.run(before_first_request())  # Connect to database before the first request
    app.run(debug=True)
