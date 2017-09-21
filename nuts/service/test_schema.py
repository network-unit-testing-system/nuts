from __future__ import absolute_import
from __future__ import unicode_literals

import yaml

SCHEMA = '''
type: seq
sequence:
  - type: map
    mapping:
      name:
        type: str
        required: yes
        unique: yes
      command:
        type: str
        required: yes
      devices:
        type: str
        required: yes
      parameter:
        type: any
        required: yes
      operator:
        type: str
        required: yes
      expected:
        type: any
        required: yes
      async:
        type: bool
        required: no
      setup: &commands
        type: seq
        required: no
        sequence:
        - type: map
          mapping:
            command:
              type: str
              required: yes
            devices:
              type: str
              required: no
            parameter:
              type: any
              required: no
            save:
              type: str
              required: no
      teardown: *commands
'''

TEST_SCHEMA = yaml.safe_load(SCHEMA)
