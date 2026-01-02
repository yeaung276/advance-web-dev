# Adding new module
`uv run manage.py startapp <modulename>`

# Making migration files
`uv run manage.py makemigrations`

# Running migration files
`uv run manage.py migrate`

# Running in dev mode
`uv run manage.py runserver`

# Creating superuser of the app
`uv run manage.py createsuperuser`
User: admin\\
Email: admin@gmail.com\\
Password: admin\\

# Creating normal ser of the app
go to admin dashboard and add user there.\\
User: user\\
Password: AC2SoFC2OfTtoITp\\


# Seeding the data
`uv run manage.py migrate` to create database.
`uv run scripts/bulk_import.py` to add seed data.

# Running the tests
`uv run manage.py test`

