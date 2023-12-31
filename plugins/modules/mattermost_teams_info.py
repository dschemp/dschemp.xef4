#!/usr/bin/python

# Copyright: (c) 2023, Daniel Schemp (@dschemp)
# MIT License (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: "mattermost_teams_info"

short_description: "Gather information about a team in Mattermost."

version_added: "1.0.0"

description: "Gather information about a team in Mattermost."

options:
    team_id:
        description: "Team ID as specified by the Mattermost API."
        aliases: ["id"]
        type: "str"
    team_name:
        description: "(Display) Name of the Team in Mattermost."
        aliases: ["name"]
        type: "str"

author:
    - Daniel Schemp (@dschemp)
"""

EXAMPLES = r"""
- name: "Get a list of all teams."
  dschemp.xef4.mattermost_teams_info:
    url: "https://chat.example.com"
    token: "ohhoosi0thoo0iegophe6vae9k"

- name: "Get a single team."
  dschemp.xef4.mattermost_teams_info:
    url: "https://chat.example.com"
    token: "ohhoosi0thoo0iegophe6vae9k"
    team_id: "ij3aeng7ao8hee3ya8gaihaove"

- name: "Get a single team by its name."
  dschemp.xef4.mattermost_teams_info:
    url: "https://chat.example.com"
    token: "ohhoosi0thoo0iegophe6vae9k"
    team_name: "ACME Service Squad"
"""

RETURN = r"""
teams:
    description: "List of all teams found."
    returned: "success"
    type: "list"
    contains:
        allow_open_invite:
            type: "bool"
            returned: "success"
        allowed_domains:
            type: "str"
            returned: "success"
        cloud_limits_archived:
            type: "str"
            returned: "success"
        company_name:
            type: "str"
            returned: "success"
        create_at:
            type: "int"
            returned: "success"
        delete_at:
            type: "int"
            returned: "success"
        description:
            type: "str"
            returned: "success"
        display_name:
            type: "str"
            returned: "success"
        email:
            type: "str"
            returned: "success"
        group_constrained:
            type: "str"
            returned: "success"
        id:
            type: "str"
            returned: "success"
        invite_id:
            type: "str"
            returned: "success"
        last_team_icon_update:
            type: "str"
            returned: "success"
        name:
            type: "str"
            returned: "success"
        policy_id:
            type: "str"
            returned: "success"
        scheme_id:
            type: "str"
            returned: "success"
        type:
            type: "str"
            returned: "success"
        update_at:
            type: "int"
            returned: "success"
"""

from ansible_collections.dschemp.xef4.plugins.module_utils import mattermost
from ansible.module_utils.basic import AnsibleModule


def run_module():
    mattermost_conn_args = mattermost.connection_argument_spec()
    module_args = dict(
        team_id=dict(type="str", aliases=["id"]),
        team_name=dict(type="str", aliases=["name"]),
    )
    module_args.update(mattermost_conn_args)
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("team_id", "team_name")],
    )

    mattermost.fail_imports(module)

    base_url = module.params["url"]
    access_token = module.params["token"]

    mm_api = mattermost.MattermostAPI(module, base_url, access_token)
    team_id = module.params["team_id"]
    team_name = module.params["team_name"]
    if team_id:
        data = mm_api.get_team(team_id)
    elif team_name:
        data = mm_api.get_team_by_name(team_name)
    else:
        data = mm_api.get_all_teams()

    if not isinstance(data, list):
        data = [data]

    result = dict(changed=False, teams=data)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
