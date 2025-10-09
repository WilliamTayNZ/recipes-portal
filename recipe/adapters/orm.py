from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship, synonym

from covid.domain import model

# global variable giving access to the MetaData (schema) information of the database
metadata = MetaData()