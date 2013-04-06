from flask.ext.wtf import Form, RadioField
from flask.ext.wtf import Required

class SubmitForm(Form):
    function = RadioField('function', choices=[
        ('sin','sin function'),
        ('cos','cos function'),
        ('log','log function')
    ])
