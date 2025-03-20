import click
from pymongo import MongoClient
from datetime import datetime

db_client = MongoClient().local
tasks = db_client.tasks
counter_local = db_client.counter

def get_next_task_id():
    """Obtiene el siguiente ID autoincremental de la colección de contadores"""
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

@click.command()
@click.argument("description")
def add(description):
    id = get_next_task_id()
    created_at = updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    "Enter set-task [id] [description of the task] [status of the task]"
    db_client.tasks.insert_one({"id":id,
                                "description": description,
                                "status":"to-do",
                                "created_at":created_at,
                                "updated_at":updated_at})
    click.echo("New task saved")

@click.command()
def list():
    db = db_client.tasks.find({},{"_id":0}).sort("id", 1)
    for document in db:
        click.echo(f"{document}")

@click.command()
@click.argument("id")
@click.argument("status")
def update(id, status):
    "Update the status of a task. Enter the following information: [id] [new status]"
    db_client.tasks.update_one({"id":id}, {"$set":{"status": status}})
    click.echo("Information has been updated")
    

tasks_management.add_command(add)
tasks_management.add_command(list)
tasks_management.add_command(update)


if __name__ == '__main__':
    tasks_management()