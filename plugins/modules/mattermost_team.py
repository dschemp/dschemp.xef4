#!/usr/bin/python

# Copyright: (c) 2023, Daniel Schemp (@dschemp)
# MIT License (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: "mattermost_team"

short_description: "Create, delete or update a team in Mattermost."

version_added: "1.0.0"

description: "Create, delete or update a team in Mattermost."

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
- name: "Create a new team."
  dschemp.xef4.mattermost_team:
    url: "https://chat.example.com"
    token: "ohhoosi0thoo0iegophe6vae9k"
    team_slug: "acme-service-squad-2"
    team_name: "ACME Service Squad II"
    team_type: "invite"
    state: "present"

# - name: "Update a teams info."
#   dschemp.xef4.mattermost_team:
#     url: "https://chat.example.com"
#     token: "ohhoosi0thoo0iegophe6vae9k"

- name: "Delete a team."
  dschemp.xef4.mattermost_team:
    url: "https://chat.example.com"
    token: "ohhoosi0thoo0iegophe6vae9k"
    team_id: "ij3aeng7ao8hee3ya8gaihaove"
    permanent: false
    state: "absent"
"""

RETURN = r"""
"""

from ansible_collections.dschemp.xef4.plugins.module_utils import mattermost
from ansible.module_utils.basic import AnsibleModule


def run_module():
    mattermost_conn_args = mattermost.connection_argument_spec()
    module_args = dict(
        team_slug=dict(type="str", aliases=["slug"]),
        team_name=dict(type="str", aliases=["display_name", "name"]),
        team_type=dict(
            type="str", aliases=["type"], choices=["open", "invite"], default="invite"
        ),
        team_id=dict(type="str", aliases=["id"]),
        permanent=dict(type="bool", aliases=["deletion_permanent"], default=False),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module_args.update(mattermost_conn_args)
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        # required_together=[("team_slug", "team_name", "team_type"), ("team_id")],
        # required_one_of=[("team_slug", "team_id")],
        # mutually_exclusive=[("team_slug", "team_id")],
        # required_if=[("state", "absent", ("team_id"))],
    )

    mattermost.fail_imports(module)

    base_url = module.params["url"]
    access_token = module.params["token"]

    team_slug = module.params["team_slug"]
    team_name = module.params["team_name"]
    team_type = module.params["team_type"]
    team_id = module.params["team_id"]
    permanent = module.params["permanent"]
    state = module.params["state"]

    mm_api = mattermost.MattermostAPI(module, base_url, access_token)

    result = dict(changed=False)

    if state == "absent":
        if team_name and not team_id:
            team = mm_api.get_team_by_name(team_name)
            team_id = team.id
        mm_api.delete_team(team_id, permanent=permanent)
        result["changed"] = True
    else:
        # Assume state == "present"
        # Check if already exists
        if mm_api.team_exists(team_name):
            # If already exists, update team
            pass
        else:
            # If not already exists, create
            data = mm_api.create_new_team(team_slug, team_name, team_type)
            result["changed"] = True
            result["team"] = data

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
