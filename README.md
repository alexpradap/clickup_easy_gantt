# clickup_easy_gantt
Use Clickup API to create an organized list so that Gantt view shows a reasonable timeline for project.

This scripts takes the assumption that story points are directly related with days of work. This is done this way in many organizations altough in many other this is a different interpretation. For those, the logic can be modified to use another mechanism to calculate the duration in days.

Task priority index is used to sort tasks, so that your list should have been manually sorted in Clickup before running this script. This is way more practical than creating dependencies manually and allows you to change priorities in any moment without messing task dependencies, which if done manually probes to be the horror for a pm. Script should be ran whenever priorities or estimations change.

**First task in the list should have an innitial date and it will be considered the timeline start date. If not, then current date will be considered the start date.**

# API Key

API Key should be stored as an env variable in your shell .profile (or equivalent) file:
```
CU_API_KEY="your_API_key"
export CU_API_KEY
```

# Data File

You need to create a data file in which users, list_id and holidays are stored. File should be named `data.json` and should live in the project root directory. It has been added to the `.gitignore` file for security reasons.

File structure should follow this:
```
{
   "team_users": [
        {
            "email": "user_email_address",
            "id": "user_id",
            "daily_dedication": <number of hours of daily dedication to project>
        },
        ...
    ],
    "list_id": "your_list_id",
    "holidays": [
        {
            "date": "01-01-2023",
            "weekday": "Sun"
        },
        ...
    ]
}
```

# Pandas

Script uses pandas 2.0.1

In order to check your current version of pandas execute `pip list | grep pandas` from command line.