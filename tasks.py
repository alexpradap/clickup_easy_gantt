import requests
import os
import json
import requests
import datetime
import calendar
import pandas

def check_holiday(check_date):
    for h in holidays:
        if check_date == h["date"]:
            return True
    return False

def add_working_days(my_date, days):
    for i in range(days): 
        my_date = my_date + datetime.timedelta(days = 1)
        wd = my_date.strftime("%a")
        while wd == "Sat" or wd == "Sun" or check_holiday(my_date.strftime("%d-%m-%Y")):
            my_date = my_date + datetime.timedelta(days = 1)
            wd = my_date.strftime("%a")
    return my_date

api_key = os.getenv('CU_API_KEY')

with open('data.json') as data_file:
    file_contents = data_file.read()

data = json.loads(file_contents)
team_users = data["team_users"]
list_id = data["list_id"]
holidays = data["holidays"]
next_sprint_kickoff = data["next_sprint_kickoff"]

df = pandas.DataFrame(columns = ["id", "name", "orderindex", "assignee_id", "assignee_username", "start_date", "due_date", "points", "time_estimate"])

for u in team_users:
    query_string = "order_by=id&assignees[]=" + u["id"]
    url = "https://api.clickup.com/api/v2/list/" + list_id + "/task" + "?" + query_string
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    response = requests.get(url, headers = headers)
    data = response.json()

    udf = pandas.DataFrame(columns = ["id", "name", "orderindex", "assignee_id", "assignee_username", "start_date", "due_date", "points", "time_estimate"])
    for t in data["tasks"]:
        rdf = pandas.DataFrame({"id": t["id"],
                "name": t["name"],
                "orderindex": t["orderindex"],
                "assignee_id": t["assignees"][0]["id"],
                "assignee_username": t["assignees"][0]["username"],
                "start_date": t["start_date"],
                "due_date": t["due_date"],
                "points": t["points"],
                "time_estimate": t["time_estimate"]}, index = [0])
        udf = pandas.concat([udf, rdf], ignore_index = True)

    udf.sort_values(by = "orderindex", ascending = True, inplace = True)
    udf.reset_index(inplace = True)

    pivot_date = datetime.datetime.strptime(next_sprint_kickoff, "%d-%m-%Y %H:%M:%S")
    ## pivot_date = datetime.datetime.now()
    ## print(pivot_date.strftime("%d-%m-%Y"))
    
    for i in range(len(udf)):
        udf.at[i, "start_date"] = pivot_date
        points = int(udf.at[i,"points"])
        pivot_date = add_working_days(pivot_date, points)
        udf.at[i, "due_date"] = pivot_date
        udf.at[i, "time_estimate"] = u["daily_dedication"] * points
        pivot_date = add_working_days(pivot_date, 1)
        print(udf.iloc[i])

    df = pandas.concat([df, udf], ignore_index = True)

df.to_csv('tasks.csv', index = False, encoding = 'utf-8')

for index, row in df.iterrows():
    payload = {
        "start_date": calendar.timegm(row["start_date"].timetuple()) * 1000,
        "due_date": calendar.timegm(row["due_date"].timetuple()) * 1000,
        "time_estimate": row["time_estimate"]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    url = "https://api.clickup.com/api/v2/task/" + row["id"]
    reponse = requests.put(url, json = payload, headers = headers)
    if response.status_code != 200:
        raise Exception("Task update failed.")