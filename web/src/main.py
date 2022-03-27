import os
from datetime import datetime
from typing import Optional


from fastapi import FastAPI, Depends, status
from pydantic import BaseModel, Field

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS


class Measurement(BaseModel):
    rhum: int = Field(..., gt=0, title='Humidity')
    rco2: int = Field(..., gt=0, title='Carbon dioxide')
    pm02: int = Field(..., gt=0, title='Fine particles')
    atmp: float = Field(..., gt=-100, lt=500, title='Temperature')
    chip_id: str
    timestamp: Optional[float] = Field(None, gt=0, title='Time of measurement')


# Dependency
def get_influx_client():
    client = InfluxDBClient.from_env_properties()
    try:
        yield client
    finally:
        client.close()


bucket = os.getenv("INFLUXDB_BUCKET")
app = FastAPI()


@app.get('/')
async def root():
    return {}


@app.post('/measurements', status_code=status.HTTP_201_CREATED, summary='Save measurements from device')
async def create_measurement(data: Measurement, influxdb_client: InfluxDBClient = Depends(get_influx_client)):
    bucket = "my-bucket"
    if 'timestamp' in data:
        timestamp = data.timestamp
    else:
        timestamp = datetime.utcnow()
    write_api = influxdb_client.write_api(write_options=ASYNCHRONOUS)
    point = Point("air_quality") \
        .tag("chip_id", data.chip_id) \
        .field("atmp", data.atmp) \
        .field("pm02", data.pm02) \
        .field("rco2", data.rco2) \
        .field("rhum", data.rhum) \
        .time(timestamp, WritePrecision.NS)

    async_result = write_api.write(bucket, record=point)
    async_result.get()

    return data
