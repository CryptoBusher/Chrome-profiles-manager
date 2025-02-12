from enum import Enum


class ParamType(Enum):
    INT = 'integer'
    FLOAT = 'float'
    BOOL = 'boolean'
    SELECT = 'select'


class SettingParam:
    def __init__(self, key, param_type, group, name, description, **kwargs):
        self.key = key
        self.param_type = param_type
        self.group = group
        self.name = name
        self.description = description
        self.min = kwargs.get('min')
        self.max = kwargs.get('max')
        self.options = kwargs.get('options')


SETTINGS_META = {
    'general': [
        SettingParam(
            key='max_workers',
            param_type=ParamType.INT,
            group='general',
            name='Max Workers',
            description='Maximum number of worker threads',
            min=1,
            max=100
        )
    ],
    'browser': [
        SettingParam(
            key='launch_delay_sec',
            param_type=ParamType.FLOAT,
            group='browser',
            name='Launch Delay',
            description='Delay between browser starts (seconds)',
            min=0.0,
            max=10.0
        ),
        SettingParam(
            key='reverse_launch_order',
            param_type=ParamType.BOOL,
            group='browser',
            name='Reverse Order',
            description='Launch browsers in reverse order'
        ),
        SettingParam(
            key='distribute',
            param_type=ParamType.BOOL,
            group='browser',
            name='Distribute',
            description='Distribute windows on screen'
        ),
        SettingParam(
            key='working_area_width_px',
            param_type=ParamType.INT,
            group='browser',
            name='Screen Width',
            description='Working area width in pixels',
            min=100,
            max=3840
        ),
        SettingParam(
            key='working_area_height_px',
            param_type=ParamType.INT,
            group='browser',
            name='Screen Height',
            description='Working area height in pixels',
            min=100,
            max=2160
        )
    ]
}