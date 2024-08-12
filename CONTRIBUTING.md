<!-- markdownlint-disable MD024 -->
# Contribute to Streamlit Pydantic

Thanks for your interest in contributing to our project. This page will give you a quick overview of how things are organized and, most importantly, how to get involved.

Everyone is welcome to contribute, and we value everybody's contribution. Code is thus not the only way to help the community. Answering questions, helping others, reaching out and improving the documentations are immensely valuable to the projects as well.

## Table of contents

1. [Issues and bug reports](#issues-and-bug-reports)
2. [Contributing to the code base](#contributing-to-the-code-base)
    - [Development instructions](#development-instructions)
    - [Commit messages guidelines](#commit-messages-guidelines)
    - [Opening a pull request](#opening-a-pull-request)
    - [Review & merging of a pull request](#review--merging-of-a-pull-request)
    - [Git workflow & versioning](#git-workflow--versioning)
3. [Code conventions](#code-conventions)
    - [Python conventions](#python-conventions)
4. [Code of conduct](#code-of-conduct)

## Issues and bug reports

- We use GitHub issues to track bugs and enhancement requests. Submit issues for any [feature request and enhancement](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=feature&template=02_feature-request.md&title=), [bugs](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=bug&template=01_bug-report.md&title=), or [documentation](https://github.com/lukasmasuch/streamlit-pydantic/issues/new?assignees=&labels=documentation&template=03_documentation.md&title=) problems.
- First, do a quick search on the Github issue tracker or the known issues section in the readme to see if the issue has already been reported. If so, it's often better to just leave a comment on an existing issue rather than creating a new one. Old - and sometimes closed - issues also often include helpful tips and solutions to common problems.
- When creating an issue, try using one of our [issue templates](https://github.com/lukasmasuch/streamlit-pydantic/issues/new/choose) which already contain some guidelines on which content is expected to process the issue most efficiently. If no template applies, you can of course also create an issue from scratch.
- Please provide as much context as possible when you open an issue. The information you provide must be comprehensive enough to reproduce that issue for the assignee. Therefore, contributors should use but aren't restricted to the issue template provided by the project maintainers.
- Please apply one or more applicable [labels](https://github.com/lukasmasuch/streamlit-pydantic/labels) to your issue so that all community members are able to cluster the issues better.
- If you have questions about one of the existing issues, please comment on them, and one of the maintainers will clarify.

## Contributing to the code base

You are welcome to contribute code in order to fix a bug, to implement a new feature, to propose new documentation, or just to fix a typo. Check out [good first issue](https://github.com/lukasmasuch/streamlit-pydantic/labels/good%20first%20issue) and [help wanted](https://github.com/lukasmasuch/streamlit-pydantic/labels/help%20wanted) issues if you want to find open issues to implement.

- Before writing code, we strongly advise you to search through the existing PRs or issues to make sure that nobody is already working on the same thing. If you find your issue already exists, make relevant comments and add your reaction (👍 - upvote, 👎 - downvote). If you are unsure, it is always a good idea to open an issue to get some feedback.
- Should you wish to work on an existing issue that has not yet been claimed, please claim it first by commenting on the GitHub issue that you want to work on and begin work (the maintainers will assign it to your GitHub user as soon as they can). This is to prevent duplicated efforts from other contributors on the same issue.
- To contribute changes, always branch from the `main` branch and after implementing the changes create a pull request as described [below](#opening-a-pull-request).
- Commits should be as small as possible while ensuring that each commit is correct independently (i.e., each commit should compile and pass tests). Also, make sure to follow the commit message guidelines.
- Test your changes as thoroughly as possible before you commit them. Preferably, automate your test by unit/integration tests.

### Commit messages guidelines

Commit messages should be as standardized as possible within the repository. A few best practices:

1. Always use simple present (imperative mood) to describe what the commit does. Explain what & why, not how!
2. Start with a capital letter.
3. Don’t end the subject line with a period.
4. Descriptive but short subject line (< 50 chars).
5. Link to issues by mentioning them in commit messages.
6. Examples: `Add image to documentation section 3`, `Fix memory leak. Closes #3`, `Split method X into two methods`. Refer to [this blog](https://chris.beams.io/posts/git-commit/) for more information about good commit messages.

### Opening a pull request

1. **Set title**. The title should follow our [commit message guidelines](#commit-messages-guidelines) (example: `Fix memory leak in picture loader`). If the pull request closes a specific issue, the title can be used to mention the issue (example: `Fix memory leak in picture loader. Closes #3`). Prefix the title with `[WIP]` *(Work In Progress)* to indicate that you are not done but need clarification or an explicit review before you can continue your work item.
2. **Add appropriate labels** (e.g. bug, enhancement, documentation).
3. **Set description:** Describe what the pull request is about and add some bullet points describing what’s changed and why (make use of the provided template). Link the pull request to all relevant issues in the pull request description (e.g. `Closes #10`). Find more information on linking pull requests to issues [here](https://help.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue). Add `BREAKING CHANGE` into the description in case the PR introduces breaking changes.
4. Open the pull request and make sure existing tests and checks pass. The PR will only be merged into `main` if it is consistent with style and linting guidelines.
  
### Review & merging of a pull request

1. Every pull request will be reviewed by at least 1 reviewer and will also trigger CI pipelines to automatically build and test the changes. If your PR is not getting reviewed for a longer time, you can @-reply a reviewer in the pull request or comment.
2. Every comment on PR should be accepted as a change request and should be discussed. When something is optional, it should be noted in the comment. If a review requires you to make additional changes, please test the changes again. Create a comment on the PR to notify the reviewers that your amendments are ready for another round of review.
3. Once the pull request is approved by at least 1 reviewer, the pull request can be merged. `Squash & merge` is the preferred merging strategy.
4. In case a new (feature) branch was created in the main repository, please delete this branch after a successful merge.

### Git workflow & versioning

- We use [GitLab Flow](https://docs.gitlab.com/ee/university/training/gitlab_flow.html#release-branch) as our branching workflow.
- Feature branching: Use (short-lived) feature branches. Naming schema:  `feature/<DESCRIPTION>`, if related to one specific issue use suffix: `feature/<DESCRIPTION>/<ISSUE-NUMBER>`. In addition to the `feature/` prefix, we recommend using more descriptive feature branch prefixes such as `bugfix/` for bug-fixes, `maintenance/` for maintenance or refactoring changes, and `documentation/` for changes related to the documentation.
- For versioning, we have adapted the [Semantic Versioning](https://semver.org/) standard. All version tags on Git must be prefixed with `v` (e.g.`v<MAJOR>.<MINOR>.<PATCH>`). The version can be suffixed with a tag that indicates a pre-release or unfinished version. All our local development builds will use the following dev suffix: `-dev.<BRANCH>`.

## Code conventions

- Code Style: [PEP8](https://www.python.org/dev/peps/pep-0008/)
- Documentation Style: [Google Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- Naming Conventions: [naming-convention-guides](https://github.com/naming-convention/naming-convention-guides/tree/master/python#python-naming-convention)
- Code Formatter: [ruff](https://docs.astral.sh/ruff/)
- Import Sorting: [ruff](https://docs.astral.sh/ruff/)
- Linting: [ruff](https://docs.astral.sh/ruff/)
- Type Checking: [mypy](https://github.com/python/mypy)
- Testing: [pytest](http://doc.pytest.org/)
- Package Manager: [rye](https://rye.astral.sh/)
- Use type hints wherever possible: [Cheatsheet](https://mypy.readthedocs.io/en/latest/cheat_sheet_py3.html)
- Minimum compatibility: Python 3.8

### Code formatting

We use [ruff](https://docs.astral.sh/ruff/) for code formatting and import sorting. The following commands runs the formatting on all Python files:

```bash
rye run format
```

### Code linting

We use [ruff](https://docs.astral.sh/ruff/) for linting and [mypy](https://github.com/python/mypy) for type checking. You can find our ruff configuration inside the `pyproject.toml`. The following commands runs all linting and type checks on all python files:

```bash
rye run checks
```

### Adding & running tests

We use the [pytest](http://doc.pytest.org/) framework for testing. For more info on this, see the [pytest documentation](http://docs.pytest.org/en/latest/contents.html). Tests for modules and classes live in their own directories of the same name inside the `tests` folder. To be discovered, all test files and test functions need to be prefixed with `test_`. To run the test suite, execute:

```bash
rye test
```

When adding tests, make sure to use descriptive names, keep the code short and concise and only test for one behavior at a time. Try to avoid unnecessary imports and use `parametrize` test cases wherever possible. Parametrizing tests allows to test multiple inputs to a function and verify that they return the expected output. Use [fixtures](https://docs.pytest.org/en/stable/fixture.html) to share test setups with - optional - setup and tear-down routines. Fixtures can also be parameterized.

## Code of Conduct

All members of the project community must abide by the [Contributor Covenant, version 2.0](./.github/CODE_OF_CONDUCT.md). Only by respecting each other we can develop a productive, collaborative community. Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting a project maintainer.
