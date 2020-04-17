class BaseValidatePOST:
    required_keys = None

    def validate(self, _dict):
        missing_list = []
        for r in self.required_keys:
            if r not in _dict:
                missing_list.append(r)
        if missing_list:
            raise ValueError(
                'Mandatory key='
                + str(missing_list)
                + ' not provided'
            )

        return True


class ValidateEnclosurePOST(BaseValidatePOST):
    required_keys = [
        'temperature',
        'humidity',
        'uv_index',
        'co2_ppm',
        'cov_ppm'
    ]


class ValidatedCoolerPOST(BaseValidatePOST):
    required_keys = [
        "air_in_temperature",
        "air_out_temperature",
        "air_in_humidity",
        "air_out_humidity"
    ]


class ValidateHeaterPOST(BaseValidatePOST):
    required_keys = [
        ''
    ]


class ValidateWaterPumpPOST(BaseValidatePOST):
    required_keys = [
        'level'
    ]


class ValidateHumidifierPOST(BaseValidatePOST):
    required_keys = [
        ''
    ]


class ValidateSprinklerPOST(BaseValidatePOST):
    required_keys = [
        'tag',
        'soil_humidity'
    ]
