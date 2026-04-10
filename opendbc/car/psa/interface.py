from opendbc.car import structs, get_safety_config
from opendbc.car.interfaces import CarInterfaceBase
from opendbc.car.psa.carcontroller import CarController
from opendbc.car.psa.carstate import CarState
from opendbc.car.psa.radar_interface import RadarInterface as _RadarInterface

TransmissionType = structs.CarParams.TransmissionType


class CarInterface(CarInterfaceBase):
  CarState = CarState
  CarController = CarController
  RadarInterface = _RadarInterface

  @staticmethod
  def _get_params(ret: structs.CarParams, candidate, fingerprint, car_fw, alpha_long, is_release, docs) -> structs.CarParams:
    ret.brand = 'psa'

    ret.safetyConfigs = [get_safety_config(structs.CarParams.SafetyModel.psa)]

    ret.dashcamOnly = False

    ret.steerActuatorDelay = 0.3
    ret.steerLimitTimer = 0.1
    ret.steerAtStandstill = True

    ret.steerControlType = structs.CarParams.SteerControlType.angle
    # radar available in stock long mode (ARTIV sends 0x4F6 sensing data)
    # OP long disables radar via UDS, so radar is unavailable in that mode
    ret.radarUnavailable = alpha_long

    ret.alphaLongitudinalAvailable = True
    ret.openpilotLongitudinalControl = alpha_long
    ret.startingState = True
    ret.startAccel = 1.0

    # ret.longitudinalTuning.kiBP = [0., 35.]
    # ret.longitudinalTuning.kiV = [0.5, 0.2]

    return ret