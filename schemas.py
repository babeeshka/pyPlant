from marshmallow import Schema, fields, validate, EXCLUDE

class PlantSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True 

    id = fields.Int(required=True)
    common_name = fields.Str(required=True)
    scientific_name = fields.List(fields.Str(), required=False, allow_none=True)
    other_name = fields.List(fields.Str(), required=False, allow_none=True)
    family = fields.Str(allow_none=True, required=False)
    origin = fields.List(fields.Str(), required=False, allow_none=True)
    type = fields.Str(required=False, allow_none=True)
    dimension = fields.Str(required=False, allow_none=True)
    dimensions = fields.Dict(required=False, allow_none=True)
    cycle = fields.Str(required=False, allow_none=True)
    watering = fields.Str(required=False, allow_none=True)
    sunlight = fields.List(fields.Str(), required=False, allow_none=True)
    propagation = fields.List(fields.Str(), required=False, allow_none=True)
    hardiness = fields.Dict(required=False, allow_none=True)
    hardiness_location = fields.Dict(required=False, allow_none=True)
    growth_rate = fields.Str(required=False, allow_none=True)
    drought_tolerant = fields.Bool(required=False, allow_none=True)
    salt_tolerant = fields.Bool(required=False, allow_none=True)
    thorny = fields.Bool(required=False, allow_none=True)
    invasive = fields.Bool(required=False, allow_none=True)
    tropical = fields.Bool(required=False, allow_none=True)
    indoor = fields.Bool(required=False, allow_none=True)
    care_level = fields.Str(required=False, allow_none=True)
    pest_susceptibility = fields.List(fields.Str(), required=False, allow_none=True)
    flowers = fields.Bool(required=False, allow_none=True)
    flowering_season = fields.Str(allow_none=True, required=False)
    flower_color = fields.Str(required=False, allow_none=True)
    cones = fields.Bool(required=False, allow_none=True)
    fruits = fields.Bool(required=False, allow_none=True)
    edible_fruit = fields.Bool(required=False, allow_none=True)
    edible_fruit_taste_profile = fields.Str(required=False, allow_none=True)
    fruit_nutritional_value = fields.Str(required=False, allow_none=True)
    fruit_color = fields.List(fields.Str(), required=False, allow_none=True)
    harvest_season = fields.Str(allow_none=True, required=False)
    leaf = fields.Bool(required=False, allow_none=True)
    leaf_color = fields.List(fields.Str(), required=False, allow_none=True)
    edible_leaf = fields.Bool(required=False, allow_none=True)
    cuisine = fields.Bool(required=False, allow_none=True)
    medicinal = fields.Bool(required=False, allow_none=True)
    poisonous_to_humans = fields.Field(required=False, allow_none=True)  # Changed to Field to accept both bool and int
    poisonous_to_pets = fields.Field(required=False, allow_none=True)  # Changed to Field to accept both bool and int
    description = fields.Str(required=False, allow_none=True)
    default_image = fields.Dict(required=False, allow_none=True)
    other_images = fields.Field(required=False, allow_none=True)  # Changed to Field to accept both string and list