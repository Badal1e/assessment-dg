FROM public.ecr.aws/lambda/python:3.10

COPY requirements/.txt .

# from official docs i found lambdas task root
RUN pip install -r requirements.txt -t /var/task

COPY app.py /var/task

CMD ["app.lambda_handler"]
