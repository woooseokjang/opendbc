from opendbc.can import CANParser
from opendbc.car import Bus, structs
from opendbc.car.interfaces import RadarInterfaceBase
from opendbc.car.psa.values import DBC

RADAR_MSG_ADDR = 0x4F6  # HS2_DAT_ARTIV_V2_4F6
RADAR_MSG_NAME = "HS2_DAT_ARTIV_V2_4F6"
RADAR_BUS = 1  # ADAS bus

# ARTIV_SENSOR_STATE: 2 = Active
SENSOR_STATE_ACTIVE = 2


def get_radar_can_parser(CP):
  messages = [(RADAR_MSG_NAME, 10)]  # 10 Hz from rlog analysis
  return CANParser(DBC[CP.carFingerprint][Bus.pt], messages, RADAR_BUS)


class RadarInterface(RadarInterfaceBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.track_id = 0
    self.radar_off_can = CP.radarUnavailable
    self.rcp = get_radar_can_parser(CP) if not self.radar_off_can else None

  def update(self, can_strings):
    if self.radar_off_can or self.rcp is None:
      return super().update(None)

    vls = self.rcp.update(can_strings)
    if RADAR_MSG_ADDR not in vls:
      return None

    return self._update()

  def _update(self):
    ret = structs.RadarData()

    if not self.rcp.can_valid:
      ret.errors.canError = True

    msg = self.rcp.vl[RADAR_MSG_NAME]

    sensor_state = int(msg['ARTIV_SENSOR_STATE'])
    target_detected = bool(msg['TARGET_DETECTED'])

    if sensor_state != SENSOR_STATE_ACTIVE:
      ret.errors.canError = True

    if target_detected:
      if 0 not in self.pts:
        self.pts[0] = structs.RadarData.RadarPoint()
        self.pts[0].trackId = self.track_id
        self.track_id += 1

      self.pts[0].measured = True
      self.pts[0].dRel = float(msg['DISTANCE_GAP'])
      self.pts[0].vRel = float(msg['RELATIVE_SPEED'])
      self.pts[0].yRel = 0.0
      self.pts[0].aRel = float('nan')
      self.pts[0].yvRel = float('nan')
    else:
      self.pts.pop(0, None)

    ret.points = list(self.pts.values())
    return ret
