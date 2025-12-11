FROM public.ecr.aws/lambda/python:3.10

COPY requirements/.txt /
COPY app.py /

CMD ["app.lambda_handler"]
