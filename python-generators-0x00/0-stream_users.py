
import csv


def stream_users(data):
    with open(data, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        
        for row in reader:
            yield row
            
    
    