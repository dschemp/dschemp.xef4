#!/usr/bin/python

# Copyright: (c) 2023, Daniel Schemp (@dschemp)
# MIT License (see LICENSE)

from urllib.parse import urljoin
from ansible.module_utils.basic import missing_required_lib, AnsibleModule
from ansible.module_utils.common.text.converters import to_native

import traceback

try:
    import requests

    HAS_REQUESTS_PACKAGE = True
    REQUESTS_IMP_ERR = None
except ImportError:
    HAS_REQUESTS_PACKAGE = False
    REQUESTS_IMP_ERR = traceback.format_exc()


def fail_imports(module):
    errors = []
    traceback = []
    if not HAS_REQUESTS_PACKAGE:
        errors.append(missing_required_lib("requests"))
        traceback.append(REQUESTS_IMP_ERR)
    if errors:
        module.fail_json(msg="\n".join(errors), traceback="\n".join(traceback))


def connection_argument_spec():
    return dict(
        url=dict(type="str", required=True),
        token=dict(type="str", required=True),
    )


MATTERMOST_API_GET_TEAM_PATH = "api/v4/teams/{}"
MATTERMOST_API_GET_ALL_TEAMS_PATH = "api/v4/teams"
MATTERMOST_API_GET_TEAM_BY_NAME_PATH = "api/v4/teams/name/{}"


class MattermostAPI:
    def __init__(self, module: AnsibleModule, url: str, access_token: str) -> None:
        self.module = module
        self.base_url = url
        self.access_token = access_token

    def __request(self, method: str, path: str, query_params: dict = None):
        url = urljoin(self.base_url, path)
        headers = {"Authorization": "Bearer {}".format(self.access_token)}

        res = requests.request(
            method=method, url=url, headers=headers, params=query_params
        )

        if res.ok:
            return res.json()
        elif 400 <= res.status_code <= 499:
            """Handle all 4xx status codes (client side errors)."""
            self.module.fail_json(
                msg=res.json()["message"],
                status=res.reason,
                status_code=res.status_code,
            )
        elif 500 <= res.status_code <= 599:
            """Handle all 5xx status codes (server side errors)."""
            self.module.fail_json(
                msg="Unexpected server side error.",
                status=res.reason,
                status_code=res.status_code,
            )
        else:
            """Unhandled errors."""
            self.module.fail_json(msg="Unhandled error.")

    def get_all_teams(self):
        teams = []
        per_page = 60
        page = 0
        q = {"include_total_count": True, "per_page": per_page}

        res = self.__request("GET", MATTERMOST_API_GET_ALL_TEAMS_PATH, query_params=q)
        data = res["teams"]
        teams += data

        total_count = res["total_count"]
        while (per_page * page + len(data)) < total_count:
            page += 1
            res = self.__request(
                "GET",
                MATTERMOST_API_GET_ALL_TEAMS_PATH,
                query_params={**q, "page": page},
            )
            data = res["teams"]
            teams += data

        return teams

    def get_team(self, team_id: str):
        return self.__request("GET", MATTERMOST_API_GET_TEAM_PATH.format(team_id))

    def get_team_by_name(self, name: str):
        return self.__request("GET", MATTERMOST_API_GET_TEAM_BY_NAME_PATH.format(name))
