import click
from pymongo import MongoClient
from datetime import datetime

db_client = MongoClient().local
tasks = db_client.tasks
counter_local = db_client.counter

def get_next_task_id():
    counter = counter_local.find_one_and_update(
        {"_id": "task_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return counter["seq"]

@click.group()
def tasks_management():
    pass

@click.command("add", short_help="Enter set-task [id] [description of the task] [status of the task]")
@click.argument("description")
def add(description):
    id = get_next_task_id()
    created_at = updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    
    db_client.tasks.insert_one({"id":id,
                                "description": description,
                                "status":"to-do",
                                "created_at":created_at,
                                "updated_at":updated_at})
    click.echo("New task saved")

@click.command("delete", short_help="This is to delete tasks")
@click.argument("id")
def delete(id):
    int_id = int(id)
    db_client.tasks.delete_one({"id":int_id})
    click.echo("The task has been deleted")

@click.command("list", short_help="List all pending tasks, depending on the status or in general")
@click.option("--done", is_flag=True)
@click.option("--todo", is_flag=True)
@click.option("--in_progress", is_flag=True)
def list(done, todo, in_progress):

    sums = sum([done, todo, in_progress])

    if sums == 0:
        db = db_client.tasks.find({},{"_id":0}).sort("id", 1)
        for document in db:
            click.echo(f"{document}")
        
    if done:
        db = db_client.tasks.find({"status":"done"},{"_id":0}).sort("id", 1)
        for document in db:
            click.echo(f"{document}")
    elif todo:
        db = db_client.tasks.find({"status":"to-do"},{"_id":0}).sort("id", 1)
        for document in db:
            click.echo(f"{document}")
    elif in_progress:
        db = db_client.tasks.find({"status":"in-progress"},{"_id":0}).sort("id", 1)
        for document in db:
            click.echo(f"{document}")
    

@click.command("update", short_help="Update the status of a task: [id] [new status]")
@click.argument("id")
@click.argument("status")
def update(id, status):
    
    int_id = int(id)
    if tasks.find_one({"id":int_id})["status"] == status:
        click.echo("The status is currently the same, change the status")
    else:
        new_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_client.tasks.update_one({"id":int_id}, [{"$set":{"status": status}}, {"$set":{"updated_at": new_datetime}}])
        click.echo("Information has been updated")

tasks_management.add_command(add)
tasks_management.add_command(list)
tasks_management.add_command(update)
tasks_management.add_command(delete)

if __name__ == '__main__':
    tasks_management()