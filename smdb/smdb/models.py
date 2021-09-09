"""
This is the SMDB database model. The database schema derives from this module.

Mike McCann
MBARI 20 May 2021
"""

import uuid as uuid_lib
from django.contrib.gis.db import models


class Person(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    first_name = models.CharField(max_length=128, db_index=True, unique=True)
    last_name = models.CharField(max_length=128, db_index=True, unique=True)
    institution_name = models.CharField(max_length=256, blank=True, null=True)

    class Meta(object):
        verbose_name_plural = "People"

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class PlatformType(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.name


class Platform(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    platformtype = models.ForeignKey(PlatformType, on_delete=models.CASCADE)
    platform_name = models.CharField(max_length=128, db_index=True, unique=True)
    operator_org_name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f"{self.platform_name} ({self.operator_org_name})"


class MissionType(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    missiontype_name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.missiontype_name


class SensorType(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    sensortype_name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.sensortype_name


class Sensor(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    sensortype = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=128)
    comment = models.CharField(max_length=128)
    missions = models.ManyToManyField("Mission")

    def __str__(self):
        return f"{self.sensortype}({self.model_name})"


class Expedition(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    expd_name = models.CharField(max_length=128, null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    investigator = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name="investigator",
        on_delete=models.CASCADE,
    )
    chiefscientist = models.ForeignKey(
        Person,
        blank=True,
        null=True,
        related_name="chiefscientist",
        on_delete=models.CASCADE,
    )
    expd_path_name = models.CharField(max_length=256, null=True)
    expd_db_id = models.IntegerField(null=True)

    def __str__(self):
        name = ""
        if self.expd_name:
            name = self.expd_name
        return f"{self.expd_path_name} ({name})"


class Compilation(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    compilation_dir_name = models.CharField(max_length=128, db_index=True)
    grid_bounds = models.PolygonField(
        srid=4326, spatial_index=True, blank=True, null=True
    )
    compilation_path_name = models.CharField(max_length=128, db_index=True)
    navadjust_dir_path = models.CharField(max_length=128, db_index=True)
    figures_dir_path = models.CharField(max_length=128, db_index=True)
    comment = models.TextField(blank=True, null=True)
    thumbnail_filename = models.CharField(max_length=128, db_index=True)
    kml_filename = models.CharField(max_length=128, db_index=True)
    proc_datalist_filename = models.CharField(max_length=128, db_index=True)
    update_status = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.compilation_dir_name}"


class Mission(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    mission_name = models.CharField(max_length=256, db_index=True)
    grid_bounds = models.PolygonField(
        srid=4326, spatial_index=True, blank=True, null=True
    )
    expedition = models.ForeignKey(
        Expedition, on_delete=models.CASCADE, blank=True, null=True
    )
    missiontype = models.ForeignKey(
        MissionType, on_delete=models.CASCADE, blank=True, null=True
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, blank=True, null=True
    )
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    start_depth = models.FloatField(blank=True, null=True)
    start_point = models.PointField(
        srid=4326, spatial_index=True, dim=2, blank=True, null=True
    )
    quality_comment = models.TextField(blank=True, null=True)
    repeat_survey = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    notes_filename = models.CharField(
        max_length=128, db_index=True, blank=True, null=True
    )
    region_name = models.CharField(max_length=128, db_index=True, blank=True)
    site_detail = models.CharField(max_length=128, db_index=True, blank=True)
    thumbnail_filename = models.CharField(max_length=128, db_index=True, blank=True)
    kml_filename = models.CharField(
        max_length=128, db_index=True, blank=True, null=True
    )
    compilation = models.ForeignKey(
        Compilation, on_delete=models.CASCADE, blank=True, null=True
    )
    update_status = models.IntegerField(blank=True, null=True)
    sensors = models.ManyToManyField(Sensor, blank=True)
    data_archivals = models.ManyToManyField("DataArchival", blank=True)
    citations = models.ManyToManyField("Citation", blank=True)

    def __str__(self):
        return f"{self.mission_name}"

    def display_sensor(self):
        return ", ".join(
            f"{sensor.sensortype}({sensor.model_name})" for sensor in self.sensors.all()
        )

    display_sensor.short_description = "Sensor"

    def display_data_archival(self):
        return ", ".join(
            data_archival.doi for data_archival in self.data_archivals.all()
        )

    display_data_archival.short_description = "Data Archival"

    def display_citation(self):
        return ", ".join(citation.doi for citation in self.citations.all())

    display_citation.short_description = "Citation"


class DataArchival(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    missions = models.ManyToManyField(Mission)
    doi = models.CharField(max_length=256, db_index=True)
    archival_db_name = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return self.doi


class Citation(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    missions = models.ManyToManyField(Mission)
    doi = models.CharField(max_length=256, db_index=True)
    full_reference = models.CharField(max_length=256, db_index=True)

    def __str__(self):
        return self.doi


class Note(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid_lib.uuid4, editable=False)
    text = models.TextField()
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notes for {self.mission.mission_name}"
