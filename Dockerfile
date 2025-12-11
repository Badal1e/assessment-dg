FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt /var/task
RUN pip install -r requirements.txt

COPY app.py /var/task

CMD ["app.lambda_handler"]
