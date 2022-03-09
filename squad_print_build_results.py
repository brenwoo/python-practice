#!/usr/bin/env python3
import argparse
import json
import requests
from pprint import pprint
from tabulate import tabulate

import logging

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()


def get_objects(endpoint_url, expect_one=False, parameters={}):
    """
    gets list of objects from endpoint_url
    optional parameters allow for filtering
    expect_count
    """
    obj_r = requests.get(endpoint_url, parameters)
    if obj_r.status_code == 200:
        objs = obj_r.json()
        if "count" in objs.keys():
            if expect_one and objs["count"] == 1:
                return objs["results"][0]
            else:
                ret_obj = []
                while True:
                    for obj in objs["results"]:
                        ret_obj.append(obj)
                    if objs["next"] is None:
                        break
                    else:
                        obj_r = requests.get(objs["next"])
                        if obj_r.status_code == 200:
                            objs = obj_r.json()
                return ret_obj
        else:
            return objs


def get_testrun_results(squad_url, build, environment):
    testruns_url = squad_url + "/api/testruns/"
    params = {"environment": environment["id"], "build": build["id"]}
    testruns = get_objects(testruns_url, False, params)
    results = {}
    for testrun in testruns["results"]:
        if testrun["tests_file"]:
            _results_resp = requests.get(testrun["tests_file"])
            _results = _results_resp.json()
            results.update(_results)
    return results


def main():

    parser = argparse.ArgumentParser(description="Pull qa-reports data")
    parser.add_argument(
        "--source-project-slug",
        dest="source_project_slug",
        required=True,
        help="slug of the base project, from which to pull data",
    )
    parser.add_argument(
        "--source-project-build",
        dest="source_project_build",
        required=True,
        help="Build version of the source project",
    )
    parser.add_argument(
        "--squad-url",
        dest="squad_url",
        required=True,
        help="URL of SQUAD instance in form https://example.com",
    )

    args = parser.parse_args()
    params = {"slug": args.source_project_slug}
    base_url = args.squad_url + "/api/projects/"
    builds_url = args.squad_url + "/api/builds/"
    envs_url = args.squad_url + "/api/environments/"

    project = get_objects(base_url, True, params)
    project_envs = get_objects(envs_url, False, {"project": project["id"]})
    build = get_objects(
        builds_url,
        True,
        {"project": project["id"], "version": args.source_project_build},
    )

    for env in project_envs:
        source_results = get_testrun_results(args.squad_url, build, env)
        logging.info(env["slug"])
        table_results = []
        for name, result in source_results.items():
            table_results.append([name])
            try:
                with open(env["slug"] + "-%s" % args.source_project_build, "w") as f:
                    f.write(tabulate(table_results))
            except IOError:
                print("File does not exist")


if __name__ == "__main__":
    main()
