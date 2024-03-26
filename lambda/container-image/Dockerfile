# python3.12 lambda base image
FROM public.ecr.aws/lambda/python:3.12

# copy requirements.txt to container
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# installing dependencies
RUN pip3 install -r requirements.txt

# Copy function code to container
COPY app.py ${LAMBDA_TASK_ROOT}

# setting the CMD to your handler file_name.function_name
CMD [ "app.handler" ]
