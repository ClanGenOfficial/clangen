import requests as requests


def fetch_latest_dev():
    action_url = "https://api.github.com/repos/archanyhm/clangen/actions/artifacts"
    result = requests.get(action_url)

    artifacts = result.json()['artifacts']

    for artifact in artifacts:
        run = artifact['workflow_run']

        if run['head_branch'] != 'development':
            continue

        print(run)