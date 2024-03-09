import random as rnd

from locust import HttpUser, TaskSet, constant, tag, task


class Tests(TaskSet):
    wait_time = constant(1)
    
    @tag("get_id")
    @task
    def check_get_by_id(self):
        id = rnd.randint(1, 4)
        with self.client.get(f'/stations/get_by_id/{id}', catch_response=True, name='/stations/get_by_id/[id]') as response:
            if response.status_code == 200:
                station = response.json().get('value')
                if station["id"] == id:
                    response.success()
                else:
                    response.failure(f'station with {id} id not found')
            else:
                response.failure(f'status code is {response.status_code}')

    @tag("get_all")
    @task
    def check_get_all(self):
        with self.client.get('/transactions/get_all', catch_response=True, name='/transactions/get_all') as response:
            if response.status_code == 200:
                transactions = response.json().get('values')
                if transactions is not None:
                   response.success()
                else:
                   response.failure('Error!')
            else:
                response.failure(f'status code is {response.status_code}')

    @tag("post")
    @task
    def check_add(self):
       station_id = rnd.randint(1, 4)
       fuel_quantity = rnd.randint(10,50)
       data = {"station_id": station_id, "fuel_quantity": fuel_quantity}
       with self.client.post('/transactions/add', catch_response=True,data=data, name='/transactions/add') as response:
           if response.status_code == 200:
               value = response.json().get('value')
               if value > 0:
                   response.success()
               else:
                   response.failure("Error!")
           else:
               response.failure(f'status code is {response.status_code}')

class Website(HttpUser):
    tasks=[Tests]