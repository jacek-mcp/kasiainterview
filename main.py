from typing import List, Dict
from flask import Flask
from marshmallow import Schema, fields, post_load
from flask_restful import Api, Resource, request, abort
from datetime import time
import  math

app = Flask(__name__)
api = Api(app)


class Apartment:

    def __init__(self, apartment_number):
        self.apartment_number = apartment_number
        self.sunlight_start = None
        self.sunlight_stop = None

    def __str__(self):
        return "number: {} / sunlight_start: {} / sunlight_stop: {}".format(self.apartment_number, self.sunlight_start, self.sunlight_stop)

    def set_sunlight_hours(self, sunlight_start, sunlight_stop):
        self.sunlight_start = sunlight_start
        self.sunlight_stop = sunlight_stop

    def get_sunlight_hours(self):
        return self.sunlight_start, self.sunlight_stop


class ApartmentSchema(Schema):

    apartment_number = fields.Int(required=True)
    sunlight_start = fields.Time()
    sunlight_stop = fields.Time()

    class Meta:
        fields = ("apartment_number", "sunlight_start", "sunlight_stop")
        ordered = True



class Building:

    def __init__(self, name: str, apartments_count: int, distance: float):
        self.name = name
        self.apartments_count = apartments_count
        self.distance = distance
        self.apartments = [Apartment(i) for i in range(self.apartments_count)]

    def __str__(self):
        return "name: {} / apartment_count: {} / distance:  {}m / apartments: {}".format(self.name, self.apartments_count, self.distance, [str(apartment) for apartment in self.apartments])

    def find_apartment(self, ap_nr: int):
        for a in self.apartments:
            if a.apartment_number == ap_nr:
                return a
        
        return None

class BuildingSchema(Schema):
    name = fields.Str(required=True)
    apartments_count = fields.Int(required=True)
    distance = fields.Int(required=True)
    apartments = fields.List(fields.Nested("ApartmentSchema"))

    class Meta:
        fields = ("name", "apartments_count", "distance", "apartments")
        ordered = True

    @post_load
    def make_building(self, data, **kwargs):
        return Building(**data)

class Neighborhood():

    def __init__(self, name:str, apartments_height:float, buildings: List[Building]):
        self.name = name
        self.apartments_height = apartments_height

        self.buildings = buildings

        self.day_length = 9.183 #hours
        sunrise_hour = 8.2333
        sunset_hour = 17.4166


    def __str__(self):
        return "name: {} / apartments_height: {} / buildings: {}".format(self.name, self.apartments_height, [str(building) for building in self.buildings])

    def find_building(self, name: str):
        for b in self.buildings:
            if b.name == name:
                return b
        
        return None
        

    def get_distance_between_buildings(self, building1: Building, building2: Building):
        distance = 0
        count = False
        for b in self.buildings:
            if (b.name == building1.name or b.name == building2.name) and count == False:
                count = True
                distance += b.distance
                continue
            if (b.name == building1.name or b.name == building2.name) and count == True:
                break
            if count:
                distance += b.distance

        return distance




    def get_angle_between_apartment_and_building(self, apartment: Apartment, target_building: Building, source_building: Building):
        rel_height = self.apartments_height * apartment.apartment_number
        rel_building_height = target_building.apartments_count * self.apartments_height - rel_height

        distance = self.get_distance_between_buildings(target_building, source_building)

        print(distance)

        tg = rel_building_height / distance

        return math.atan(tg)



    def compute_sunlight_hours(self, building: Building, apartment: Apartment):
        left_cover_angle = 0
        right_cover_angle = 0

        left = True

        for b in self.buildings:
            if b.name == building.name:
                left = False
                continue

            if left:
                angle = self.get_angle_between_apartment_and_building(apartment, b, building)
                if angle > left_cover_angle:
                    left_cover_angle = angle
            else:
                angle = self.get_angle_between_apartment_and_building(apartment, b, building)
                if angle > right_cover_angle:
                    right_cover_angle = angle

        
        sunrise_delay = (left_cover_angle * self.day_length) / 180 # [hour]
        sunset_acc = (right * self.day_length) / 180 # [hour]
        
        sunrise_delay_h = math.floor(sunrise_delay)
        sunrise_delay_m = sunrise_delay - sunrise_delay_h

        sunset_acc_h = math.floor(sunset_acc)
        sunset_acc_m = sunset_acc - sunset_acc_h



        # TODO tutaj liczenie tych godzin!
        sunlight_start = self.sunrise_hour + sunrise_delay
        sunlight_stop = self.sunset_hour - sunset_acc
        apartment.set_sunlight_hours(sunlight_start, sunlight_stop)
        return apartment.get_sunlight_hours()


class NeighborhoodSchema(Schema):
    name = fields.Str(required=True)
    apartments_height = fields.Float(required=True)
    buildings = fields.List(fields.Nested(BuildingSchema), required=True)

    class Meta:
        fields = ("name", "apartments_height", "buildings")
        ordered = True

    @post_load
    def make_neighborhood(self, data, **kwargs):
        return Neighborhood(**data)

# sunrise_hour = 8:14
# sunset_hour = 17:25
city = []

def find_neighborhood(neighborhood_name):
    for neighborhood in city:
        if neighborhood.name == neighborhood_name:
            return neighborhood
    return None



class CityController(Resource):

    def init(self, city_data):
        schema = NeighborhoodSchema(many=True)
        city.extend(schema.load(city_data))


    def post(self):
        city_data = request.get_json(force=True)["city_data"]
        self.init(city_data)
        return "City data recieved", 201

    def get(self):
        schema = NeighborhoodSchema(many=True)
        result = schema.dump(city)
        return result

api.add_resource(CityController, "/sunlightAPI/barcelona")


class SunlightController(Resource):


    def getSunlightHours(self, neighborhood_name, building_name, apartment_number):
        neighborhood = find_neighborhood(neighborhood_name)
        if not neighborhood:
            abort("Wrong name of neighborhood")
        building = neighborhood.find_building(building_name)
        if not building:
            abort("Wrong building name")
        apartment = building.find_apartment(apartment_number)
        if not apartment:
            abort("Wrong apartment number")
        sunlight_start, sunlight_stop = apartment.get_sunlight_hours() if all(apartment.get_sunlight_hours()) else neighborhood.compute_sunlight_hours(building, apartment)
        return "{} - {}".format(sunlight_start, sunlight_stop)


        # return "{} hh:mm:ss - hh:mm:ss".format(apartment_number)


    def get(self, neighborhood_name, building_name, apartment_number):
        return self.getSunlightHours(neighborhood_name, building_name, apartment_number)

api.add_resource(SunlightController, "/sunlightAPI/barcelona/<string:neighborhood_name>/<string:building_name>/<int:apartment_number>/")


if __name__ == "__main__":
    app.run(debug=True)
