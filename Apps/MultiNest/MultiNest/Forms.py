# -*- coding: UTF-8 -*-

from flask.ext.wtf import Form, IntegerField, FloatField, validators


class SubmitForm(Form):
    xsize = IntegerField(
        'X', [
            validators.NumberRange(
                min=10, max=10000,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=100,
    )
    ysize = IntegerField(
        'Y', [
            validators.NumberRange(
                min=10, max=10000,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=100,
    )
    nodes_min = IntegerField(
        'Min', [
            validators.NumberRange(
                min=1, max=1000,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=10,
    )
    nodes_max = IntegerField(
        'Max', [
            validators.NumberRange(
                min=1, max=1000,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=10,
    )
    sigma_min = FloatField(
        'Min', [
            validators.NumberRange(
                min=1, max=100,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=1,
    )
    sigma_max = FloatField(
        'Max', [
            validators.NumberRange(
                min=1, max=100,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=6,
    )
    n_live_points = IntegerField(
        'Live Points', [
            validators.NumberRange(
                min=10, max=100000,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=1000,
    )
    max_modes = IntegerField(
        'Max Modes', [
            validators.NumberRange(
                min=1, max=1000,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=100,
    )
    sampling_efficiency = FloatField(
        'Sampling Efficiency', [
            validators.NumberRange(
                min=0, max=1,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=0.8,
    )
    evidence_tolerance = FloatField(
        'Evidence Tolerance', [
            validators.NumberRange(
                min=0, max=1,
                message="Wymaga liczby zawartej w <%(min)s, %(max)s>"
            )
        ],
        default=0.5,
    )
