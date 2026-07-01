# French-Language Print Publications in England to 1685 - Django Project

This document is primarily designed for technical staff working on the development of the project (e.g. software engineers and system admins).


## Django Project

The project is called 'frenchprintengland', but project files are stored in the 'core' folder. Please refer to `core/settings.py` for further details


## Django Apps

Apps include:

+ general - this is for static, general sections of the website (e.g. cookies page, accessibility page, etc.) that don't require a data model
+ account - custom user accounts
+ researchdata - this is for storing and interacting with the project's research data


## Django Admin

The provided Django Admin feature is utilised within this Django project, to allow the research project team to perform CRUD operations on the database using an intuitive web interface.


## Tests

There are a series of automated tests located in each Django app folder as 'tests.py'

To perform the tests:

+ Run: python manage.py test
+ Use the feedback given by Django for any failed tests to fix issues
+ Repeat this until returns a 100% pass rate


Once finished testing, remember to reverse the changes made to the project setup:

+ Delete any unwanted migrations in migrations folders
+ Delete the fixtures directory, including test.json fixture, for each app


This also complies with Ruff for testing against PEP8:

+ Use pip install ruff to install (if not already installed)
+ Run `ruff check .` to perform the tests
+ The pyproject.toml file in the repo root directory, can be used to customise Ruff tests


You can use coverage to see how much of the code is included in the tests:

+ Use `pip install coverage` to install (if not already installed)
+ Use the `.coveragerc file` to customise, e.g. to ignore particular folders, etc
+ Run: `coverage run manage.py test`
+ Run: `coverage html`
+ This should create a htmlcov folder. View the index.html page in this folder using a web browser


## Accessibility Tests

Steps for running accessibility tests and accessibility reports. Note that the system must be running at `http://127.0.0.1:8000/` in order for the accessibility tests to work.

The commands below must be run from the root project directory.

0. Install `npm` (if required, see [npm](https://www.npmjs.com/) for details)
```
apt install npm
```
1. Load testing requirements
```
npm ci
```
2. Load the chrome browser in puppeteer
```
npx puppeteer browsers install chrome
```
3a. Run the tests as tests
```
npx jest
```
3b. Run the tests to produce reports (reports will be in the accessibility_reports directory)
```
npx jest --config jest.reporting.config.js
```

Note that when running in reporting mode all of the tests will pass regardless of whether report contains errors or not. The regular tests should be used first to ensure that all automated tests are passing. After this the reports should be generated. The reports contain details of potential accessibility problems that cannot be assessed automatically and which need manual checking. You should act on the information in the reports to ensure that the pages meet the accesibility guidelines.


## JavaScript

+ JavaScript files are stored in `django/core/static/js`
+ For linting JavaScript, we recommend [eslint](https://eslint.org/) and include a `.eslintrc.json` config file in this repository
+ For testing JavaScript, we use [Jest](https://jestjs.io/). Each relevant JavaScript function has a corresponding test script that Jest will run by executing the command `npm run test`
+ For bundling JavaScript files, we use [Browserify](https://browserify.org/). Each time a change is made to the standard files (e.g. main.js or the individual functions) you must bundle these into `bundle.js`, which is then read by the browser. You can bundle by running, for example, `browserify main.js -o bundle.js'


## Accessibility

Our websites must comply with accessibility regulations. See the [BEAR Accessibility](https://accessibility.bear.bham.ac.uk/) site for more information.

Please note that the RSG's template Django project will link to the home page of the BEAR Accessibility website in the footer. This will likely need to be changed (on a per site basis) to the specific page that holds the correct accessibility statement for each site. E.g. standard CAL Django websites can point to: <https://accessibility.bear.bham.ac.uk/statements-cal.html> or you may need to create a new statement page and link to that.


## Database

The SQLite3 database used sits in the Django project root folder (alongside this README file). It is not included within the Git repo, so must instead be requested from the system admin. Once you have a copy of this database, give it a suitable name like `frenchprintengland.sqlite3` and place in the `django/` directory (same directory that stores `manage.py`). Remember to name this database in `local_settings.py` (see Settings section of this document for more details)


## Settings

There are 2 settings related files:

+ `settings.py` (for general project settings, regardless of environment and containing publicly accessible information)
+ `local_settings.py` (for settings specific to that environment (e.g. dev/test/production) and for private information (e.g. API keys))

`local_settings.py` is ignored from Git, as it contains private information that shouldn't be shared with others. Instead, the file `local_settings.example.py` is stored in Git to show you what information your own `local_settings.py` needs to contain. `local_settings.test.py` is used in the CI and should never be used on a production system. The steps you must take to configure `local_settings.py` are:

+ Create a `local_settings.py` file
+ Copy and paste the content from `local_settings.example.py` into `local_settings.py`
+ Customise this content by following the guide in `local_settings.example.py`
+ Do not delete or modify `local_settings.example.py`, as this will be kept in Git to help others
