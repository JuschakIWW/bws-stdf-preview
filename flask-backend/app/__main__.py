import os
from flask import Flask, request, make_response
from flask_restful import Resource, Api
import json
import sys

from app.controller import (
    data_controller,
    model_controller,
    #    orion_controller,
    #    orion_controller_openapi,
)
from app.utils.exception_handling import make_error_response


"""
Information regarding this API:
The payload / parameters in get and put requests need to be parsed differently
For get requests, the information lies in request.args
For put requests, the information lies in request.data 
"""


def main():
    app = Flask(__name__)

    api = Api(app)

    # TODO: Check which headers should be kept
    @app.after_request
    def modify_header(response):
        """
       Manipulates the header before sending it
       Reason: Set cors part of the header to signal the browser
       that it is allowed to receive request from this api server
       """
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Credentials", True)
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
        response.headers.add(
            "Access-Control-Allow-Headers", "content-type,authorization"
        )
        return response

    def parse_payload(req):
        data = json.loads(req.data.decode()) if req.data else {}
        args = req.args
        return {**data, **args}

    # TODO: Delete if not needed anymore because of Marshmallow
    def parse_arr_str(payload, arr_name):
        if arr_name in payload.keys():
            return [e.strip(" \"'") for e in payload[arr_name].strip("[]").split(",")]
        return None

    class PhysicalMeters(Resource):
        def get(self):
            """Fetches the meta data of all existing physical meters."""
            try:
                include_measurements = (
                    request.args.get("includeMeasurements", False) == "true"
                )
                pms = data_controller.get_physical_meters(None, include_measurements)
                return make_response(pms, 200)
            except Exception as e:
                return make_error_response(e)

    class PhysicalMeter(Resource):
        def get(self, pmid):
            """Fetches the meta data and measurements of the specified physical meter."""
            try:
                include_measurements = "true" == request.args.get(
                    "includeMeasurements", False
                )
                pm = data_controller.get_physical_meters(pmid, include_measurements)
                return make_response(pm, 200)
            except Exception as e:
                return make_error_response(e)

    class VirtualMeters(Resource):
        def get(self):
            """Fetches a list of all models associated with the meter."""
            try:
                vms = data_controller.get_virtual_meters()
                return make_response({"virtualMeters": vms}, 200)
            except Exception as e:
                return make_error_response(e)

        def post(self):
            """Creates a new virtual meter by aggregating existing virtual and physical meters as its submeters."""
            try:
                payload = parse_payload(request)
                vm_details = data_controller.parse_vm_details(payload)
                vm_id = data_controller.create_virtual_meter_endpoint(vm_details)
                return make_response({"virtualMeterId": vm_id}, 200)
            except Exception as e:
                return make_error_response(e)

    class VirtualMeter(Resource):
        def get(self, vmid):
            """Fetches the meta data of the specified virtual meter."""
            try:
                vm = data_controller.get_virtual_meter(vmid)
                return make_response({"virtualMeter": vm}, 200)
            except Exception as e:
                return make_error_response(e)

        def delete(self, vmid):
            """Deletes a virtual meter."""
            try:
                rm_from_super = (
                    request.args.get("removeFromSuperMeters", False) == "true"
                )
                data_controller.delete_virtual_meter_endpoint(vmid, rm_from_super)
                return make_response({}, 200)
            except Exception as e:
                return make_error_response(e)

    class Algorithms(Resource):
        def get(self):
            try:
                include_params = request.args.get("includeParameters", False) == "true"
                meter_id = request.args.get("meterID", None)
                algorithms = model_controller.get_algorithms_endpoint(
                    include_params, meter_id
                )
                return make_response({"algorithms": algorithms}, 200)
            except Exception as e:
                return make_error_response(e)

    class Models(Resource):
        def get(self):
            """Returns all existing models."""
            try:
                models = model_controller.get_models_endpoint()
                return make_response({"MLModels": models}, 200)
            except Exception as e:
                return make_error_response(e)

    class Model(Resource):
        def delete(self, model_id):
            """Deletes the model with the specified id."""
            try:
                model_controller.delete_model_endpoint(model_id=model_id)
                return make_response({}, 200)
            except Exception as e:
                return make_error_response(e)

    class ModelsMeter(Resource):
        def get(self, meter_id):
            """Fetches a list of all models associated with the meter."""
            try:
                models = model_controller.get_models_endpoint(meter_id)
                return make_response({"MLModels": models}, 200)
            except Exception as e:
                return make_error_response(e)

    class ModelsAlgorithm(Resource):
        def put(self, meter_id, algorithm):
            """Trains a model for the specified virtual or physical meter."""
            # TODO: Put request parameters in cache for as long as the training takes
            #       Then pop them out of the cache when the training is done
            #       Make sure that this is always done, even if the training fails
            #       And invalidate the cache after a certain time
            try:
                opts = data_controller.parse_train_options(request.args)
                print("Opts: ", opts)
                # TODO: Check if opts are correctly retrieved
                results = model_controller.train_model_endpoint(
                    meter_id,
                    algorithm,
                    hyper_opt=opts["hyperParamSearch"],
                    # setDefault=opts["setDefault"],
                )
                return make_response(results, 200)
            except Exception as e:
                return make_error_response(e)

        def delete(self, meter_id, algorithm):
            """Deletes the model(s) of a virtual or physical meter that correspond to the specified algorithm."""
            try:
                model_controller.delete_model_endpoint(meter_id, algorithm)
                return make_response({}, 200)
            except Exception as e:
                return make_error_response(e)

    class Forecast(Resource):
        def get(self, meter_id):
            """
            Generates and fetches a 24-hour forecast for the specified meter.
            If no "algorithm" is specified as a query parameter, the algorithm set to default
            for the given meter is used.
            """
            try:
                algorithm = request.args.get("algorithm", None)
                date = request.args.get("date", None)
                forecast = model_controller.get_forecast_endpoint(
                    meter_id, algorithm, date
                )
                return make_response(forecast, 200)
            except Exception as e:
                return make_error_response(e)

    class Debug(Resource):
        def get(self):
            msg = "endpoint reachable!"
            specialMsg = ""
            return make_response({"msg": msg, "specialMsg": specialMsg}, 200)

    api.add_resource(Debug, "/debug")
    api.add_resource(PhysicalMeters, "/physical-meters")
    api.add_resource(PhysicalMeter, "/physical-meters/<string:pmid>")
    api.add_resource(VirtualMeters, "/virtual-meters")
    api.add_resource(VirtualMeter, "/virtual-meters/<string:vmid>")
    api.add_resource(Algorithms, "/algorithms")
    api.add_resource(Models, "/models")
    api.add_resource(Model, "/models/<string:model_id>")
    api.add_resource(ModelsMeter, "/meters/<string:meter_id>/models")
    api.add_resource(
        ModelsAlgorithm, "/meters/<string:meter_id>/models/<string:algorithm>"
    )
    api.add_resource(Forecast, "/meters/<string:meter_id>/forecast")

    @app.after_request
    def flush(response):
        sys.stdout.flush()
        sys.stderr.flush()
        return response

    # orion_controller.register_services()
    app.run(port=os.getenv("CORE_PORT"), debug=True, host="0.0.0.0")
