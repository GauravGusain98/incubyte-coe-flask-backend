from flask_restx import fields

def define_swagger_models(api):
    hello_response_model = api.model("HelloResponse", {
        "message": fields.String,
    })

    return hello_response_model
