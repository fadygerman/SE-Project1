# Act - GitHub Actions Local Runner

Act is a tool that allows you to run GitHub Actions workflows locally. This makes it easier to test and debug your workflows before pushing them to GitHub.

## Installation

You can install Act by following the instructions on the official GitHub repository: [nektos/act](https://github.com/nektos/act)

## Usage
Before running the workflow, make sure to set up your secrets correctly. You can copy the `.act/secrets.example` file to `.act/secrets` and fill in the required values.

### Run
To run the deployment workflow locally, use the following command:
```bash
act --secret-file .act/secrets -j 'deploy'
```