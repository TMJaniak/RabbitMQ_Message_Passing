# RabbitMQ_Message_Passing
This project was for the final in my CS-4320 class at The University of Missouri. It was meant for using message passing architecture in order to "scale-out" rather than "scale-up". This code receives a message from a host queue, computes the result of the first step, and then pushes the result to a second queue to compute the final result.

## Features
-student_a.py pulls messages from a host server
-Computes the results of the first step and pushes to the student_b.py server
-student_b.py pulls the result from step one and computes the result for step two
-Sends the final result to the result server

## Technologies Used
- Python 3
- RabbitMQ

## Notes
-The servers for this project have been destroyed so it can't be run anymore
